"""
Device config post API
"""

from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT
from repositories.dm_repositories.dm_delivery_settings_repo import DeliverySettingsRepository
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository
from repositories.merchant_repo import MerchantRepository
from repositories.outlet_repo import OutletRepository
from repositories.translation_repo import MessageRepository
from user_authentication.authentication import get_current_session_info
from .validation import merchant_login_parser


class NewDeviceRegistration(BasePostResource):
    required_token = True
    is_delivery_cashless = True
    request_parser = merchant_login_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='device_config/device_config_post.log',
        ),
        'name': 'device_config_post'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')  # language of the merchant
        self.device_id = self.request_args.get('device_id')  # device id of the merchant
        self.device_make = self.request_args.get('device_make')
        self.device_model = self.request_args.get('device_model')
        self.android_version = self.request_args.get('android_version')
        self.group_name = self.request_args.get('group_name')
        self.app_version = self.request_args.get('app_version')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.outlet_class_instance = OutletRepository()
        self.merchant_class_instance = MerchantRepository()
        self.message_repo_instance = MessageRepository()
        self.dm_device_repo = DmDevicesRepository()
        self.dm_device_outlet_settings = DeliverySettingsRepository()

    def sets_language_and_variables(self):
        """
        Set the locale for user message
        """
        locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
        self.message = ""
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')
        self.outlet_id = current_session_info.get('outlet_db_id', 0)
        self.merchant_id = current_session_info.get('merchant_db_id', 0)

    def inserting_new_device(self):
        """
        Inserting new merchant information into database
        """
        self.dm_outlet_settings = self.dm_device_outlet_settings.get_dm_outlet_setting(
            outlet_sf_id=self.outlet_sf_id, merchant_sf_id=self.merchant_sf_id
        )
        if not self.dm_outlet_settings:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "Please setup this outlet Delivery Settings to continue.",
                "success": False,
                "code": 422
            }
            return self.send_response(self.response, self.status_code)

        data = {
            'merchant_sf_id': self.merchant_sf_id,
            'outlet_sf_id': self.outlet_sf_id,
            'outlet_id': self.outlet_id,
            'merchant_id': self.merchant_id
        }
        if self.device_id:
            data['device_id'] = self.device_id
        self.device = self.dm_device_repo.find_device_by_filter(
            _filters={
                'merchant_sf_id': self.merchant_sf_id,
                'outlet_sf_id': self.outlet_sf_id,
                'is_active': 1
            },
            order_by='desc'
        )
        data['device_make'] = self.device_make
        data['device_model'] = self.device_model
        data['android_version'] = self.android_version
        data['group_name'] = self.group_name
        data['app_version'] = self.app_version
        if self.device:
            self.dm_device_repo.update_device(self.device.get('id', 0), data=data)
            self.device.update(data)
            self.new_device = self.device
            self.status_code = 200
            self.message = "updated"
            self.new_device['is_device_online'] = bool(self.new_device['is_device_online'])
            self.new_device['is_active'] = bool(self.new_device['is_active'])
            del self.new_device['created_at']
            del self.new_device['updated_at']
            del self.new_device['last_ping']
        else:
            self.new_device = self.dm_device_repo.insert_new_device(data)
            self.status_code = 201
            self.message = "created"

    def generating_final_response(self):
        """
        Preparing final response
        """
        if self.new_device:
            self.send_response_flag = True
            self.success = True
            del self.new_device['id']
            self.response = {
                'data': self.new_device,
                'success': self.success,
                'message': self.message,
                'code': self.status_code
            }

    def process_request(self):
        self.initialize_repos()
        self.sets_language_and_variables()
        self.inserting_new_device()
        if self.is_send_response_flag_on():
            return
        self.generating_final_response()
