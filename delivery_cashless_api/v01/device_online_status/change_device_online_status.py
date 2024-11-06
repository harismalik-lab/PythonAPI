"""
Status management APIs
"""

from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT
from repositories.dm_repositories.delivery_order_details_repo import OrderDetailsRepository
from repositories.dm_repositories.dm_device_history_repo import DeviceHistoryRepository
from repositories.dm_repositories.dm_devices_app_versions import DmDevicesAppVersionsRepository
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository
from repositories.translation_repo import MessageRepository
from user_authentication.authentication import get_current_session_info
from .validation_device_online_parser import device_online_parser, device_online_check_parser


class ChangeDeviceOnlineStatus(BasePostResource):
    required_token = True
    request_parser = device_online_parser
    is_delivery_cashless = True
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='device_online_status/change_device_online_status.log',
        ),
        'name': 'change_device_online_status'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')  # language of the merchant
        # device online status
        self.device_online_status = self.request_args.get('device_online_status', False)

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.dm_devices_repo = DmDevicesRepository()
        self.message_repo_instance = MessageRepository()

    def sets_language_and_variables(self):
        """
        Set the locale for user message
        """
        locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')
        self.device_id = current_session_info.get('device_id')

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.data = {}
        self.success = False
        self.send_response_flag = True
        self.status_code = 200

        self.is_status_changed = self.dm_devices_repo.change_device_online_status(
            self.device_id, self.device_online_status
        )
        self.success = True
        self.message = 'Success'
        self.data = {
            'is_device_online': self.device_online_status
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


class PingApi(BasePostResource):
    required_token = True
    is_delivery_cashless = True
    request_parser = device_online_check_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='device_online_status/get_device_online_status.log',
        ),
        'name': 'get_device_online_status'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')  # language of the merchant
        self.current_app_version = self.request_args.get('current_app_version')
        self.current_battery_status = self.request_args.get('current_battery_status')
        self.current_free_space = self.request_args.get('current_free_space')
        self.is_offline = self.request_args.get('is_offline')
        self.offline_start_time = self.request_args.get('offline_start_time')
        self.offline_end_time = self.request_args.get('current_network_status')
        self.current_network_status = self.request_args.get('current_network_status')
        self.current_data_usage = self.request_args.get('current_data_usage')
        self.monthly_data_usage = self.request_args.get('monthly_data_usage')
        self.daily_data_usage = self.request_args.get('daily_data_usage')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.dm_device_repo = DmDevicesRepository()
        self.message_repo_instance = MessageRepository()
        self.device_history_repo = DeviceHistoryRepository()
        self.device_app_version_repo = DmDevicesAppVersionsRepository()
        self.order_details_repo = OrderDetailsRepository()

    def sets_language_and_variables(self):
        """
        Set the locale for user message
        """
        locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')
        self.device_id = current_session_info.get('device_id')

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.data = {}
        self.success = False
        self.send_response_flag = True
        self.status_code = 200

        self.is_device_online = self.dm_device_repo.check_device_online_status(self.device_id)
        self.device_history_data = {
            'dm_device_id': self.device_id,
            'current_app_version': self.current_app_version,
            'current_battery_status': self.current_battery_status,
            'current_free_space': self.current_free_space,
            'is_offline': self.current_free_space,
            'offline_start_time': self.offline_start_time,
            'offline_end_time': self.offline_end_time,
            'current_network_status': self.current_network_status,
            'current_data_usage': self.current_data_usage,
            'monthly_data': self.monthly_data_usage,
            'daily_data': self.daily_data_usage
        }
        self.device_history = self.device_history_repo.insert_into_device_history(data=self.device_history_data)
        self.app_version = self.device_app_version_repo.find_app_version_by_filter(
            _filters={'is_latest': 1, 'platform': 'android'}
        )
        self.success = True
        self.message = 'Success'
        self.data = {
            'is_device_online': bool(self.is_device_online.get('is_device_online', False)),
            'device_history': self.device_history,
            'download_path': self.app_version.get('app_url_link', ''),
            'latest_version': self.app_version.get('app_version', ''),
            'ping_time': self.dm_device_repo.PING_TIME
        }
        pending_orders = []
        pending_orders_list = self.order_details_repo.get_pending_orders(
            merchant_sf_id=self.merchant_sf_id, outlet_sf_id=self.outlet_sf_id
        )
        for pending_order in pending_orders_list:
            pending_orders.append(pending_order.get('id'))
        self.data['pending_orders'] = pending_orders
        self.response = {
            "message": self.message,
            'data': self.data,
            'success': self.success,
            "code": 200
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self):
        self.initialize_repos()
        self.sets_language_and_variables()
        self.generating_final_response()
