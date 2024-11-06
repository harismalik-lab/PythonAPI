"""
This module contains Filter API Controller
"""
from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.common_helpers import CommonHelpers
from repositories.merchant_repo import MerchantRepository
from web_api.filters.validation import filters_api_parser


class RewardsFiltersApi(BaseGetResource):
    __author__ = 'Saqib'

    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='filters_api/filters_api.log',
        ),
        'name': 'filters_api'
    }
    required_token = True
    logger = None
    request_parser = filters_api_parser

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')

    def parse_locale(self):
        self.locale = CommonHelpers.get_locale_for_messaging(self.locale)

    def initialize_repos(self):
        self.merchant_repo = MerchantRepository()

    def get_merchant_filters(self):
        self.merchant_filters = self.merchant_repo.get_merchant_filters(self.locale)
        self.set_response(
            {
                'data': self.merchant_filters,
                'success': True,
                'message': 'success'
            },
            0
        )

    def process_request(self, *args, **kwargs):
        self.parse_locale()
        self.initialize_repos()
        self.get_merchant_filters()
