"""
Get outlet menu
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT
from delivery_cashless_api.v01.get_outlet_menu.validation import get_outlet_menu_parset
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository
from repositories.outlet_menu_repo import OutletMenuRepo
from user_authentication.authentication import get_current_session_info


class GetOutletMenuAPi(BasePostResource):
    """
    Get outlet menu Api
    """
    is_delivery_cashless = True
    required_token = True
    request_parser = get_outlet_menu_parset
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='get_outlet_menu_api/get_outlet_menu_api.log',
        ),
        'name': 'get_outlet_menu_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.dm_devices_repo = DmDevicesRepository()
        self.outlet_menu_repo = OutletMenuRepo()

    def sets_language_and_variables(self):
        """
        Set the locale for user message
        """
        locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
        self.data = {}
        self.success = False
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')
        self.device_id = current_session_info.get('device_id')

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.send_response_flag = True
        self.outlet_menu = self.outlet_menu_repo.get_outlet_menu(self.merchant_sf_id, self.outlet_sf_id)
        self.success = True
        self.message = 'success'
        self.data = {
            'outlet_menu': self.outlet_menu,
            'outlet_sf_id': self.outlet_sf_id,
            'merchant_sf_id': self.merchant_sf_id
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
        self.generating_final_response()
