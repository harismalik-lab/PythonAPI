"""
Rewards Country API.
"""
from requests import codes

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.common_helpers import CommonHelpers, multi_key_sort, get_formated_date
from common.db import DEFAULT
from repositories.country_repo import CountryRepository
from repositories.customer_repo import CustomerProfile
from repositories.global_ads_repo import GlobalAdsRepository
from user_authentication.authentication import get_current_customer
from .validation import country_parser


class RewardsCountryApi(BaseGetResource):
    """
    This class handles the get_country endpoint
    """
    required_token = True
    strict_token = True
    request_parser = country_parser
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='country_api/rewards_country_api.log'
        ),
        'name': 'rewards_country_api'
    }
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        """
        populates the request arguments
        """
        self.locale = self.request_args.get('language')
        self.is_travel = self.request_args.get('istravel')
        self.user_id = self.request_args.get('user_id')

    def initialize_repos(self):
        """
        initializes the repos
        """
        self.country_class_instance = CountryRepository()
        self.global_ads_class_instance = GlobalAdsRepository()
        self.customer_repo = CustomerProfile()

    def initialize_class_attributes(self):
        self.locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.global_travel_ads = []
        self.countries = []
        self.customer = get_current_customer()
        if self.customer:
            self.customer['purchased_skus'] = self.customer_repo.get_customer_products_vc01(
                self.customer.get('customer_id')
            )

    def process_date(self):
        for ad in self.global_travel_ads:
            ad['valid_from'] = get_formated_date(ad['valid_from'])
            ad['valid_to'] = get_formated_date(ad['valid_to'])

    def get_countries(self):
        if self.is_travel:
            self.countries = self.country_class_instance.get_country_by_region_vc01(
                self.locale,
                self.customer.get('purchased_skus', [])
            )
        else:
            self.countries = self.country_class_instance.get_country(self.locale)
            self.countries = multi_key_sort(self.countries, ['position'])

    def generate_response(self):
        """
        Generates response
        """
        self.global_travel_ads = self.global_ads_class_instance.get_global_ads('Travel')
        self.process_date()
        self.send_response_flag = True
        self.response = {
            'data': {
                'countries': self.countries,
                'global_travel_ads': self.global_travel_ads
            },
            'success': True,
            'message': 'success'}
        self.status_code = codes.OK

    def process_request(self):
        """
        This method processes the request and retrieves the countries matching the search criteria
        :return: Returns the country object
        """
        self.initialize_repos()
        self.initialize_class_attributes()
        self.get_countries()
        self.generate_response()
