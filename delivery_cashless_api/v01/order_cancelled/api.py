from app_configurations.settings import DELIVERY_LOGS_PATH
from delivery_cashless_api.v01.order_rejected.api import OrderRejected


class OrderCancelled(OrderRejected):
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='order_cancelled/order_cancelled.log',
        ),
        'name': 'order_cancelled'
    }

    def get_order_status(self):
        self.order_status = self.order_status_repo.get_filter_status(
            filters={'short_title': self.order_status_repo.Cancelled}
        )
        self.merchant_order_changes['order_status_id'] = self.order_status.get('id')
        self.merchant_order_changes['reject_reason'] = self.reject_reason
        self.merchant_order_changes['is_cancelable'] = 0
        self.merchant_order.update(
            self.order_details_repo.update_merchant_order(self.order_id, data=self.merchant_order_changes)
        )
        self.data = {
            'order_id': self.merchant_order.get('id'),
            'status_id': self.order_status.get('id'),
            'status_identifier': self.order_status.get('short_title'),
            'status_title': self.order_status.get('title'),
            'status_label': self.order_status.get('label'),
            'is_active': self.merchant_order.get('is_active'),
            'order_red': self.merchant_order.get('order_number'),
            'tracking_number': self.merchant_order.get('tracking_number'),
            'is_cancelable': self.merchant_order.get('is_cancelable'),
            'is_delivered': self.merchant_order.get('is_delivered'),
            'reject_reason': self.merchant_order.get('reject_reason')
        }

    def verify_merchant_order(self):
        super().verify_merchant_order()
        if self.send_response_flag:
            return

        if not self.merchant_order.get('is_cancelable', 0):
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "Order already cancelled.",
                "success": self.success,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)
