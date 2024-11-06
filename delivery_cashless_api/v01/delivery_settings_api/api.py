"""
Delivery settings API version Delivery Cashless
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.db import DEFAULT
from delivery_cashless_api.v01.delivery_settings_api.validation import delivery_settings_parser
from repositories.dm_repositories.dm_delivery_settings_repo import DeliverySettingsRepository
from user_authentication.authentication import get_current_session_info


class DeliverySettingsApi(BasePostResource):
    """
    Delivery Settings Api
    """
    request_parser = delivery_settings_parser
    response = {}
    required_token = True
    is_delivery_cashless = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='delivery_settings_api/delivery_settings_api.log',
        ),
        'name': 'delivery_settings_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.delivery_repo_instance = DeliverySettingsRepository()

    def process_request(self):
        self.initialize_repos()
        delivery_details = self.delivery_repo_instance.get_delivery_details(self.outlet_sf_id, self.merchant_sf_id)
        self.send_response_flag = True
        self.status_code = 200
        self.response = {
            'data': delivery_details,
            'success': True,
            'message': 'success',
            'code': self.status_code
        }
