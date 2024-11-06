"""
Merchants Api, gets all the merchants of the desired name. Bsed on the given name of the merchant or the entered
sf_id of the merchant.
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.db import DEFAULT
from delivery_cashless_api.v01.get_all_merchants_api.validation import merchant_parser
from repositories.dm_repositories.dm_management_pin_repo import ManagementPinRepository
from repositories.merchant_repo import MerchantRepository
from repositories.translation_repo import MessageRepository


class GetAllMerchantsApi(BasePostResource):
    """
    Gets all the merchants along with the outlets
    """
    is_delivery_cashless = True
    request_parser = merchant_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='merchants_api/merchants_api.log',
        ),
        'name': 'merchants_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.merchant_name_or_sf_id = self.request_args.get('query')  # merchant's name
        self.locale = self.request_args.get('language')

    def initialize_local_veriables(self):
        self.merchant_ids = []

    def check_params(self):
        """
        Checks whether the params are given or not
        """
        if not self.merchant_name_or_sf_id:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": self.message_repo_instance.enter_valid_values,
                "success": False,
                "code": 0
            }
            return self.send_response(self.response, self.status_code)

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.management_pin_repo = ManagementPinRepository()
        self.message_repo_instance = MessageRepository()
        self.merchant_repo_instance = MerchantRepository()

    def get_merchants_ids(self):
        """
        Gets all the merchants ids, and its corresponding outlets
        """
        self.merchant_ids = self.merchant_repo_instance.get_merchants_ids(self.merchant_name_or_sf_id)
        if not self.merchant_ids:
            if not self.merchant_name_or_sf_id:
                self.send_response_flag = True
                self.status_code = 422
                self.response = {
                    "message": self.message_repo_instance.no_merchant_found,
                    "success": False,
                    "code": 0
                }
                return self.send_response(self.response, self.status_code)

    def get_merchant_details(self):
        """
        Gets all the merchant_details
        """
        self.merchant_details = self.merchant_repo_instance.get_dm_merchant_details(self.merchant_ids, self.locale)

    def generating_final_response(self):
        self.send_response_flag = True
        if self.merchant_details:
            self.status_code = 200
            self.response = {
                'data': self.merchant_details,
                'success': True,
                'message': 'success',
                'code': 0
            }
        else:
            self.status_code = 422
            self.response = {
                'data': {},
                'success': False,
                'message': 'No merchant found',
                'code': 0
            }

    def process_request(self):
        self.initialize_repos()
        self.check_params()
        if self.is_send_response_flag_on():
            return

        self.initialize_local_veriables()
        self.get_merchants_ids()
        if self.is_send_response_flag_on():
            return

        self.get_merchant_details()
        self.generating_final_response()
