"""
This module handles the Location API endpoint for rewards api.
"""
from requests import codes

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.common_helpers import CommonHelpers
from repositories.location_repo import LocationRepository
from web_api.location.validation import location_parser


class RewardsLocationApi(BaseGetResource):
    """
    This class handles the get_locations endpoint
    """
    request_parser = location_parser
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='location_api/rewards_location_api.log',
        ),
        'name': 'rewards_location_api'
    }

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')
        self.__platform = self.request_args.get('__platform')

    def initialize_repos(self):
        self.location_class_instance = LocationRepository()

    def initialize_class_attributes(self):
        self.locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.locations = self.location_class_instance.get_locations_lookup_vc01(self.locale)

    def process_request(self):
        """
        This method processes the requests and retrives all the locations matching the given criteria
        :return: Response with a list of locations
        """
        self.initialize_repos()
        self.initialize_class_attributes()

        self.send_response_flag = True
        self.response = {
            'data': {'locations': self.locations},
            'location_version': "47",
            'success': True,
            'message': 'success'
        }
        self.status_code = codes.OK
