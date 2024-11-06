"""
Verify devices against outlets_sf_id
"""
from flask import current_app

from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.db import DEFAULT
from delivery_cashless_api.v01.merchant_login.validation import merchant_login
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository
from repositories.dm_repositories.merchant_login_repo import MerchantLogin
from repositories.merchant_repo import MerchantRepository


class MerchantLoginApi(BasePostResource):
    """
    Merchant login api that provide devices against outlets_sf_id
    """
    is_delivery_cashless = True
    request_parser = merchant_login
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='merchant_login_api/merchant_login_api.log',
        ),
        'name': 'merchant_login_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.merchant_sf_id = self.request_args.get('merchant_sf_id')
        self.pin = self.request_args.get('pin')
        self.device_id = self.request_args.get('device_id')
        self.locale = self.request_args.get('language')
        self.device_model = self.request_args.get('device_model')
        self.device_token = self.request_args.get('device_token')
        self.device_id = self.request_args.get('device_id')
        self.device_name = self.request_args.get('device_name')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.dm_device_repo = DmDevicesRepository()
        self.merchant_login_repo = MerchantLogin()
        self.merchant_class_instance = MerchantRepository()

    def merchant_login(self):
        """Gives devices against outlet_sf_id
        params: merchant_sf_if
        params: pin"""
        self.merhant_data = self.merchant_login_repo.get_merchant_outlets_data(
            merchant=self.merchant,  locale=self.locale
        )

    def generating_final_response(self):
        """Generate final response against outlets_sf_id"""
        self.send_response_flag = True
        self.data = dict()
        self.data['merchant_data'] = self.merhant_data
        self.data['device_info'] = self.new_device
        self.status_code = 200
        merchant_repo_instance = MerchantLogin()
        self.status_code = 200
        self.response = {
            'data': self.data,
            'success': True,
            'message': 'success',
            'code': self.status_code
        }
        if self.data and current_app.config['JWT_TOKEN_ENABLED']:
            self.response['access_token'] = merchant_repo_instance.generate_token(
                self.merchant_sf_id,
                self.pin,
                self.device_id
            )
        return self.send_response(self.response, self.status_code)

    def inserting_new_device(self):
        """
        Inserting new merchant information into database
        """
        self.merchant = self.merchant_class_instance.find_merchant_data_by_sf_id(self.merchant_sf_id)
        if not self.merchant:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "No merchant found with sf_id:{sf_id}".format(sf_id=self.merchant_sf_id),
                "success": False,
                "code": 422
            }
            return self.send_response(self.response, self.status_code)

        if self.merchant.get('pin') != self.pin:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": "Invalid pin found",
                "success": False,
                "code": 422
            }
            return self.send_response(self.response, self.status_code)

        data = {'merchant_sf_id': self.merchant.get('sf_id')}
        if self.device_id:
            data['device_id'] = self.device_id
        self.device = self.dm_device_repo.find_device_by_filter_merchant(_filters={
            'merchant_sf_id': self.merchant.get('sf_id'),
            'is_active': 1
        })
        data['device_model'] = self.device_model
        data['device_token'] = self.device_token
        data['device_name'] = self.device_name
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

    def process_request(self):
        self.initialize_repos()
        self.inserting_new_device()
        if self.is_send_response_flag_on():
            return
        self.merchant_login()
        self.generating_final_response()
