"""
Status management APIs
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.db import DEFAULT
from delivery_cashless_api.v01.device_token.validation import device_token_parser
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository
from repositories.translation_repo import MessageRepository
from user_authentication.authentication import get_current_session_info


class UpdateDeviceToken(BasePostResource):
    is_delivery_cashless = True
    required_token = True
    request_parser = device_token_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='device_online_status/update_device_token.log',
        ),
        'name': 'update_device_token'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')  # language of the merchant
        self.device_id = self.request_args.get('device_id')  # device id of the merchant
        self.device_token = self.request_args.get('device_token', False)
        current_session_info = get_current_session_info()
        self.device_db_id = current_session_info.get('device_id_db')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.dm_devices_repo = DmDevicesRepository()
        self.message_repo_instance = MessageRepository()

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.data = {}
        self.success = False
        self.send_response_flag = True
        self.status_code = 200

        self.data = {
            'device_token': self.device_token
        }
        self.dm_devices_repo.update_device(self.device_db_id, data=self.data)
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
        self.generating_final_response()
