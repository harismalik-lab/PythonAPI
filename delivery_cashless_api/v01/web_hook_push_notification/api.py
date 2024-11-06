"""
Order detail API version Delivery Cashless
"""
from flask import current_app
from pyfcm import FCMNotification

from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT
from delivery_cashless_api.v01.order_details.validation import order_details_parser
from repositories.dm_repositories.delivery_order_details_repo import OrderDetailsRepository
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository


class WebHookPushNotification(BasePostResource):
    """
    Delivery Settings Api
    """
    is_delivery_cashless = True
    request_parser = order_details_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='order_detail_api/web_hook_push_notification.log',
        ),
        'name': 'web_hook_push_notification'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.outlet_sf_id = self.request_args.get('outlet_sf_id')
        self.merchant_sf_id = self.request_args.get('merchant_sf_id')
        self.outlet_id = self.request_args.get('outlet_id')
        self.merchant_id = self.request_args.get('merchant_id')
        self.device_id = self.request_args.get('device_id')
        self.order_id = self.request_args.get('order_id')
        self.locale = self.request_args.get('language')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.order_details_repo = OrderDetailsRepository()
        self.dm_device_repo = DmDevicesRepository()
        self.push_service = FCMNotification(api_key=current_app.config.get('FIRE_BASE_API_KEY'))
        self.push_service_android = FCMNotification(api_key=current_app.config.get('FIRE_BASE_API_KEY_ANDROID'))
        locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)

    def initialize_local_variables(self):
        """
        Initializes local variables
        """
        self.order_detail = {}
        data = {
            'merchant_sf_id': self.merchant_sf_id,
            'is_device_online': True,
            'is_active': True
        }
        if self.outlet_sf_id:
            data['outlet_sf_id'] = self.outlet_sf_id
        self.devices = self.dm_device_repo.find_device_by_filter_merchant(
            _filters=data, multiple_devices=True
        )
        self.devices_token = []

    def get_customer_order_details(self):
        if not self.devices:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "No device found",
                "success": True,
                "code": 422
            }
            return self.send_response(self.response, self.status_code)

        for device in self.devices:
            if device and device.get('is_active', False) and device.get('device_token'):
                    self.devices_token.append(device.get('device_token'))
        self.devices_token = list(filter(None, self.devices_token))

        if not self.devices_token:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "No Device token found.",
                "success": True,
                "code": 422
            }
            return self.send_response(self.response, self.status_code)

        self.order_detail = self.order_details_repo.get_order_details(
            self.outlet_sf_id,
            self.merchant_sf_id,
            self.order_id
        )

    def generate_final_response(self):
        self.data = {}
        if self.order_detail:
            self.push_notification_data = {
                'category': 'newOrder',
                'order_ref': self.order_detail.get('order_ref', ''),
                'order_id': self.order_id,
                'outlet_sf_id': self.outlet_sf_id,
                'merchant_sf_id':  self.merchant_sf_id
            }
            push_notification_result = self.push_service.notify_multiple_devices(
                registration_ids=self.devices_token,
                message_title='NEW ORDER RECEIVED',
                click_action=current_app.config.get('CLICK_ACTION_ORDER'),
                message_icon=current_app.config.get('CLICK_ACTION_ICON'),
                data_message=self.push_notification_data
            )
            push_notification_result_android = self.push_service_android.notify_multiple_devices(
                registration_ids=self.devices_token,
                message_title='NEW ORDER RECEIVED',
                click_action=current_app.config.get('CLICK_ACTION_ORDER'),
                message_icon=current_app.config.get('CLICK_ACTION_ICON'),
                data_message=self.push_notification_data
            )
            self.data['push_notification_result'] = push_notification_result
            self.data['push_notification_result_android'] = push_notification_result_android
            self.data['push_notification_data'] = self.push_notification_data
            self.send_response_flag = True
            self.status_code = 200
            self.response = {
                'data': self.data,
                'success': True,
                'message': 'success',
                'code': self.status_code
            }
        else:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                'data': self.data,
                'success': False,
                'message': 'no order found',
                'code': self.status_code
            }

    def process_request(self):
        self.initialize_repos()
        self.initialize_local_variables()
        self.get_customer_order_details()
        if self.is_send_response_flag_on():
            return
        self.generate_final_response()
