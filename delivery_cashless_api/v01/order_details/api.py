"""
Order detail API version Delivery Cashless
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.db import DEFAULT
from delivery_cashless_api.v01.order_details.validation import \
    order_details_parser
from repositories.dm_repositories.delivery_order_details_repo import \
    OrderDetailsRepository
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository
from user_authentication.authentication import get_current_session_info


class OrderDetailApi(BasePostResource):
    """
    Delivery Settings Api
    """
    is_delivery_cashless = True
    required_token = True
    request_parser = order_details_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='order_detail_api/order_detail_api.log',
        ),
        'name': 'order_detail_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.order_id = self.request_args.get('order_id')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.order_details_repo = OrderDetailsRepository()
        self.dm_device_repo = DmDevicesRepository()

    def initialize_local_variables(self):
        """
        Initializes local variables
        """
        self.order_detail = {}
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')

    def get_customer_order_details(self):
        self.order_detail = self.order_details_repo.get_order_details(
            self.outlet_sf_id,
            self.merchant_sf_id,
            self.order_id
        )

    def generate_final_response(self):
        if self.order_detail:
            self.send_response_flag = True
            self.status_code = 200
            self.response = {
                'data': self.order_detail,
                'success': True,
                'message': 'success',
                'code': self.status_code
            }
        else:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                'data': self.order_detail,
                'success': True,
                'message': 'success',
                'code': self.status_code
            }

    def process_request(self):
        self.initialize_repos()
        self.initialize_local_variables()
        self.get_customer_order_details()
        if self.is_send_response_flag_on():
            return
        self.generate_final_response()
