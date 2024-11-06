"""
Menu item status Api. Changes the item status on the items menu ans save it in DB.
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.db import DEFAULT
from delivery_cashless_api.v01.menu_item_status_api.validation import outlet_menu_status_parser
from repositories.outlet_menu_repo import OutletMenuRepo
from user_authentication.authentication import get_current_session_info


class MenuItemStatusApi(BasePostResource):
    """
    Menu item status Api
    """
    required_token = True
    is_delivery_cashless = True
    request_parser = outlet_menu_status_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='menu_items_status_api/menu_items_status_api.log',
        ),
        'name': 'menu_items_status_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.item_id = self.request_args.get('item_id')
        self.item_status = self.request_args.get('item_status')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.outlet_menu_repo = OutletMenuRepo()

    def initialize_local_variables(self):
        self.updated_data = {}
        self.item_status_value = 'offline'
        if self.item_status:
            self.item_status_value = 'online'
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')
        self.device_id = current_session_info.get('device_id')

    def update_items_status(self):
        self.updated_data = self.outlet_menu_repo.change_outlet_menu_item_status(
            self.item_id,
            self.item_status,
            self.item_status_value,
            self.outlet_sf_id,
            self.merchant_sf_id
        )

    def generate_final_response(self):
        self.send_response_flag = True
        if self.updated_data:
            self.status_code = 200
            self.response = {
                "data": self.updated_data,
                "message": "Status updated",
                "success": True,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)
        else:
            self.status_code = 422
            self.response = {
                "data": {},
                "message": "Status not updated",
                "success": False,
                "code": self.status_code
            }
            return self.send_response(self.response, self.status_code)

    def process_request(self):
        """
        Processes the api request
        """
        self.initialize_repos()
        self.initialize_local_variables()
        self.update_items_status()
        self.generate_final_response()
