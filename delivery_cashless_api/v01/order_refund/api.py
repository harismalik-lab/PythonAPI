from app_configurations.settings import DELIVERY_LOGS_PATH
from delivery_cashless_api.v01.order_refund.validation import order_refund_parser
from delivery_cashless_api.v01.order_rejected.api import OrderRejected
from repositories.merchant_repo import MerchantRepository


class OrderRefund(OrderRejected):
    request_parser = order_refund_parser
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='order_refund/order_refund.log',
        ),
        'name': 'order_refund'
    }

    def initialize_repos(self):
        """
        Initializes different repos
        """
        super().initialize_repos()
        self.merchant_class_instance = MerchantRepository()

    def populate_request_arguments(self):
        super().populate_request_arguments()
        self.merchant_pin = self.request_args.get('merchant_pin', '')
        self.refund_amount = self.request_args.get('refund_amount', '')

    def get_order_status(self):
        self.sub_order_status = self.order_status_repo.get_filter_status(
            filters={'short_title': self.order_status_repo.Refund_Requested}
        )
        self.merchant_order_changes['order_status_id'] = self.order_status.get('id')
        self.merchant_order_changes['reject_reason'] = self.reject_reason
        self.merchant_order_changes['is_cancelable'] = 0
        self.merchant_order_changes['is_delivered'] = 0
        self.merchant_order_changes['refund_amount'] = self.refund_amount
        self.merchant_order_changes['sub_status_id'] = self.sub_order_status.get('id')
        self.merchant_order.update(
            self.order_details_repo.update_merchant_order(self.order_id, data=self.merchant_order_changes)
        )
        self.data = {
            'order_id': self.merchant_order.get('id'),
            'status_id': self.order_status.get('id'),
            'status_identifier': self.order_status.get('short_title'),
            'status_title': self.order_status.get('title'),
            'status_label': self.order_status.get('label'),
            'sub_status_id': self.sub_order_status.get('id'),
            'sub_status_identifier': self.sub_order_status.get('short_title'),
            'sub_status_title': self.sub_order_status.get('title'),
            'sub_status_label': self.sub_order_status.get('label'),
            'is_active': self.merchant_order.get('is_active'),
            'order_red': self.merchant_order.get('order_number'),
            'tracking_number': self.merchant_order.get('tracking_number'),
            'is_cancelable': self.merchant_order.get('is_cancelable'),
            'refund_amount': self.merchant_order.get('refund_amount', 0),
            'is_refunded': self.merchant_order.get('is_refunded'),
            'is_delivered': self.merchant_order.get('is_delivered'),
            'reject_reason': self.merchant_order.get('reject_reason'),
            'updated_at': str(self.merchant_order.get('updated_at')),
            'is_refundable': False
        }

    def verify_merchant_order(self):
        super().verify_merchant_order()
        if self.send_response_flag:
            return

        self.order_status = self.order_status_repo.get_filter_status(
            filters={'short_title': self.order_status_repo.Refunded}
        )
        if self.merchant_order.get('order_status_id', 0) == self.order_status.get('id'):
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "Order is refunded already.",
                "success": self.success,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)

        self.merchant_status_order = self.order_status_repo.get_filter_status(
            filters={'id': self.merchant_order.get('order_status_id', 0)}
        )
        if self.merchant_status_order.get('short_title', '') not in [
            self.order_status_repo.COMPLETED,
            self.order_status_repo.Accepted
        ]:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "Order cant be refunded.",
                "success": self.success,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)

        if self.merchant_order.get('is_refunded', 0):
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "Order is refunded already.",
                "success": self.success,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)

        if not self.merchant_order.get('is_cancelable', 0):
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "Order is cancelled already.",
                "success": self.success,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)

        self.merchant_instance = self.merchant_class_instance.find_by_sf_id(self.merchant_sf_id)
        if not self.merchant_instance:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "No merchant found.",
                "success": self.success,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)

        if self.merchant_instance and str(self.merchant_instance['pin'][::-1]) != self.merchant_pin:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": self.message_repo_instance.get_message_by_id(32, self.locale),
                "success": self.success,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)
