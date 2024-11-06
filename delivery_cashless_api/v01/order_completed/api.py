from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT
from delivery_cashless_api.v01.order_completed.validation import order_completed_parser
from repositories.dm_repositories.delivery_order_details_repo import OrderDetailsRepository
from repositories.dm_repositories.dm_delivery_all_statuses_repo import DeliveryStatusesRepository
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository
from repositories.translation_repo import MessageRepository
from user_authentication.authentication import get_current_session_info


class OrderCompleted(BasePostResource):
    is_delivery_cashless = True
    required_token = True
    request_parser = order_completed_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='order_completed/order_completed.log',
        ),
        'name': 'order_completed'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.device_id = self.request_args.get('device_id')  # device id of the merchant
        self.order_id = self.request_args.get('order_id')
        self.locale = self.request_args.get('language')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.dm_devices_repo = DmDevicesRepository()
        self.message_repo_instance = MessageRepository()
        self.order_details_repo = OrderDetailsRepository()
        self.order_status_repo = DeliveryStatusesRepository()

    def sets_language_and_variables(self):
        """
        Set the locale for user message
        """
        locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.data = {}
        self.success = False
        self.send_response_flag = True
        self.status_code = 200

        self.merchant_order = self.order_details_repo.get_merchant_order_by_id(
            self.order_id, self.merchant_sf_id, self.outlet_sf_id
        )
        if not self.merchant_order:
            self.status_code = 422
            self.response = {
                "message": "No order found.",
                "success": self.success,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)

        self.order_status = self.order_status_repo.get_filter_status(
            filters={'short_title': self.order_status_repo.COMPLETED}
        )
        self.merchant_order_changes = dict()
        self.merchant_order_changes['order_status_id'] = self.order_status.get('id')
        self.merchant_order_changes['is_delivered'] = 1
        self.merchant_order_changes['is_cancelable'] = 0
        self.merchant_order.update(
            self.order_details_repo.update_merchant_order(self.order_id, data=self.merchant_order_changes)
        )
        self.data = {
            'order_id': self.merchant_order.get('id'),
            'status_id': self.order_status.get('id'),
            'status_identifier': self.order_status.get('short_title'),
            'delivery_time': self.merchant_order.get('delivery_time'),
            'status_title': self.order_status.get('title'),
            'status_label': self.order_status.get('label'),
            'is_active': self.merchant_order.get('is_active'),
            'order_red': self.merchant_order.get('order_number'),
            'tracking_number': self.merchant_order.get('tracking_number'),
            'is_cancelable': self.merchant_order.get('is_cancelable'),
            'is_delivered': self.merchant_order.get('is_delivered')
        }

        self.order_history = self.merchant_order
        del self.order_history['id']
        self.order_details_repo.insert_into_order_history(self.order_history)

        self.success = True
        self.message = 'Success'
        self.response = {
            "message": self.message,
            'data': self.data,
            'success': self.success,
            "code": self.status_code
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self):
        self.initialize_repos()
        self.sets_language_and_variables()
        self.generating_final_response()
