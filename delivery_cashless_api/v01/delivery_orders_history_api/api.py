"""
Delivery orders history API
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT
from delivery_cashless_api.v01.delivery_orders_history_api.validation import get_orders_history
from repositories.dm_repositories.dm_delivery_all_statuses_repo import DeliveryStatusesRepository
from repositories.dm_repositories.dm_delivery_orders_history_repo import DeliveryOrdersHistory
from user_authentication.authentication import get_current_session_info


class GetOrdersHistoryApi(BasePostResource):
    """
    Delivery get orders history Api
    """
    is_delivery_cashless = True
    required_token = True
    request_parser = get_orders_history
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='get_orders_history_api/get_orders_history_api.log',
        ),
        'name': 'get_orders_history_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')
        self.order_status = self.request_args.get('order_status')
        self.tracking_number = self.request_args.get('tracking_number')
        self.customer_name = self.request_args.get('customer_name')
        self.time_stamp = self.request_args.get('time_stamp')
        self.page_num = self.request_args.get('page_num', 1)

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.orders_history_repo = DeliveryOrdersHistory()
        self.delivery_statues_repo = DeliveryStatusesRepository()

    def sets_language_and_variables(self):
        """
        Sets the locale for user message
        """
        locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
        self.data = {}
        self.success = False
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.send_response_flag = True
        self.orders_history = self.orders_history_repo.get_orders(
            merchant_sf_id=self.merchant_sf_id,
            outlet_sf_id=self.outlet_sf_id,
            order_status=self.order_status,
            tracking_number=self.tracking_number,
            customer_name=self.customer_name,
            time_stamp=self.time_stamp,
            page_num=self.page_num if self.page_num and self.page_num > 0 else 1
        )
        self.statuses = self.delivery_statues_repo.get_filter_status(
            filters={'is_sub_status': 0}, single=False,
            in_filters=[{'short_title': [
                self.delivery_statues_repo.COMPLETED,
                self.delivery_statues_repo.Rejected,
                self.delivery_statues_repo.Pending,
                self.delivery_statues_repo.Refunded
            ]}]
        )
        self.success = True
        self.message = 'Success'
        self.data = {
            'orders_history': self.orders_history,
            'delivery_statuses': self.statuses,
            'merchant_sf_id': self.merchant_sf_id,
            'outlet_sf_id': self.outlet_sf_id,
        }

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
        if self.is_send_response_flag_on():
            return
        self.generating_final_response()
