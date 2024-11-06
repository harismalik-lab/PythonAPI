"""
Verify management pin API version Deliver Cashless
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import get_current_date_time
from common.db import DEFAULT
from delivery_cashless_api.v01.managemnet_pin_api.validation import management_pin_parser
from repositories.dm_repositories.dm_management_pin_repo import ManagementPinRepository


class ManagementPinApi(BasePostResource):
    """
    Management api and all of its modules
    """
    is_delivery_cashless = True
    request_parser = management_pin_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='management_pin_api/management_pin_api.log',
        ),
        'name': 'management_pin_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.management_pin = self.request_args.get('pin')  # management pin of the user
        self.is_pin_active = False

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.management_pin_repo = ManagementPinRepository()

    def verify_pin(self):
        self.is_pin_active = self.management_pin_repo.verify_management_pin(self.management_pin)

    def update_pin_data(self):
        data = {
            'last_used': get_current_date_time()
        }
        self.management_pin_repo.update_management_pin_info(self.management_pin, data)

    def generating_final_response(self):
        self.send_response_flag = True
        if self.is_pin_active:
            self.status_code = 200
            self.response = {
                'data': {},
                'success': True,
                'message': 'Pin verified',
                'code': 0
            }
        else:
            self.status_code = 422
            self.response = {
                'data': {},
                'success': False,
                'message': 'Pin not verified',
                'code': 0
            }

    def process_request(self):
        self.initialize_repos()
        self.verify_pin()
        if self.is_pin_active:
            self.update_pin_data()
        self.generating_final_response()
