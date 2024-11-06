"""
Connect app configs API
"""
from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseDynamicResource
from common.common_helpers import CommonHelpers
from common.db import CONSOLIDATION, DEFAULT
from repositories.customer_repo import CustomerProfile
from user_authentication.authentication import get_current_customer
from web_api.configs.validation_configs import configs_parser as config_parser


class ConnectConfigsApi(BaseDynamicResource):
    """
    Configs API handler for connect.
    """
    request_parser = config_parser
    required_token = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='connect_configs_api/connect_configs_api.log',
        ),
        'name': 'connect_configs_api'
    }
    connections_names = [DEFAULT, CONSOLIDATION]

    def populate_request_arguments(self):
        self.os = self.request_args.get('os')
        self.session_token = self.request_args.get('session_token')
        self.locale = self.request_args.get('language')
        self.key = self.request_args.get('key')

    def initialize_repos(self):
        self.customer_profile_class_instance = CustomerProfile(logger=self.logger)

    def initialize_class_attributes(self):
        self.locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.configs = []

    def response_on_os(self):
        version_number = '40'
        if self.os:
            self.configs = [
                {'key': 'log_analytics', 'value': 'false'},
                {'key': 'is_gamification_on', 'value': 'false'},
                {'key': 'locations', 'value': version_number}
            ]
        else:
            self.configs = [
                {'key': 'log_analytics', 'value': 'false', 'os': 'ios'},
                {'key': 'log_analytics', 'value': 'false', 'os': 'wp'},
                {'key': 'log_analytics', 'value': 'false', 'os': 'android'},
                {'key': 'is_gamification_on', 'value': 'false', 'os': 'ios'},
                {'key': 'is_gamification_on', 'value': 'false', 'os': 'wp'},
                {'key': 'is_gamification_on', 'value': 'false', 'os': 'android'},
                {'key': 'locations', 'value': version_number, 'os': 'all'}
            ]

    def response_on_no_session_token(self):
        if not self.session_token:
            self.send_response_flag = True
            self.response = {
                'data': {
                    'config': self.configs,
                    'customer': [],
                    'offer_pinging_pending': []
                },
                'success': True,
                'message': 'success'
            }
            self.status_code = 200
            return self.send_response(self.response, self.status_code)

    def loading_customer_data_and_offers(self):
        session = get_current_customer()
        customer_id = session.get('customer_id', 0) if session else 0
        customer = self.customer_profile_class_instance.get_customer_profile(customer_id)
        self.send_response_flag = True
        self.response = {
            'data': {
                'config': self.configs,
                'customer': customer,
                'offer_pinging_pending': []
            },
            'success': True,
            'message': 'success'
        }
        self.status_code = 200
        return self.send_response(self.response, self.status_code)

    def process_request(self):
        """
        This method is used to retrieve all the configs
        :return: Returns the configs retrieved against the criteria
        """
        self.initialize_repos()
        self.initialize_class_attributes()
        self.response_on_os()
        self.response_on_no_session_token()
        if self.is_send_response_flag_on():
            return

        self.loading_customer_data_and_offers()
        if self.is_send_response_flag_on():
            return
