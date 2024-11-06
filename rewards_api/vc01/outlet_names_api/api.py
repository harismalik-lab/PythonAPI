"""
Rewards Outlet names api
"""
from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.db import DEFAULT
from repositories.outlet_repo import OutletRepository
from web_api.outlet.validation_outlet_names import outlet_names_parser


class RewardsOutletNamesApi(BaseGetResource):
    __author__ = 'Saqib'
    backup_request_args_for_exception = False
    request_parser = outlet_names_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='outlet_api/rewards_outlet_names_api.log',
        ),
        'name': 'rewards_outlet_names_api'
    }
    logger = None
    status_code = 200
    required_token = True
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.outlet_ids = self.request_args.get('outlet_ids[]')
        self.locale = self.request_args.get('language')

    def initialize_repos(self):
        self.outlet_class_instance = OutletRepository()

    def process_request(self):
        self.initialize_repos()
        self.set_response({
            'data': {
                'OutletNames': self.outlet_class_instance.get_outlet_names(
                    outlet_ids=self.outlet_ids,
                    locale=self.locale
                )},
            'message': 'success',
            'success': True
        })
