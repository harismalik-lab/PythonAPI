"""
This module contains the currency endpoint
"""

from requests import codes

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.common_helpers import CommonHelpers
from repositories.currency_repo import CurrencyRepository
from .validation import currency_parser


class RewardsCurrencyApi(BaseGetResource):
    """
    This class handles the connectivity configs endpoint
    """
    request_parser = currency_parser
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='currency_api/rewards_currency_api.log',
        ),
        'name': 'rewards_currency_api'
    }

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')

    def initialize_repos(self):
        self.currency_class_instance = CurrencyRepository()

    def initialize_class_attributes(self):
        self.locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.currencies = self.currency_class_instance.get_currencies_lookup(self.locale)

    def process_request(self):
        """
        This method handles the retrieval of currently active currencies.
        :return: Response with a list of currencies
        """
        self.initialize_repos()
        self.initialize_class_attributes()

        self.send_response_flag = True
        self.response = {
            'data': {'currencies': self.currencies},
            'success': True,
            'message': 'success'
        }
        self.status_code = codes.OK
