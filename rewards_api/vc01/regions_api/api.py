"""
This is the API for regions
"""
from requests import codes

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT
from repositories.region_repo import RegionRepository
from rewards_api.vc01.regions_api.validation import rewards_region_parser
from user_authentication.authentication import get_current_customer


class AllRegionApi(BaseGetResource):
    """
    This class handles the regions endpoint
    """
    request_parser = rewards_region_parser
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='region_api/region_api.log',
        ),
        'name': 'region_api'
    }
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        """
        populates the request arguments
        """
        self.is_travel = self.request_args.get('is_travel')
        self.locale = self.request_args.get('language')

    def initialize_repos(self):
        """
        initializes repo instances
        """
        self.region_class_instance = RegionRepository()

    def initialize_class_attributes(self):
        self.locale = CommonHelpers.get_locale(self.locale, location_id=0)
        self.customer = get_current_customer()

    def process_request(self):
        """
        This handles the retrieval of all the regions.
        """
        self.initialize_repos()
        self.initialize_class_attributes()
        if self.is_travel:
            regions = self.region_class_instance.get_region_for_travel_vc01(
                self.locale,
                self.customer.get('purchased_skus')
            )
        else:
            regions = self.region_class_instance.get_region(self.locale)

        self.send_response_flag = True
        self.response = {
            'data': {'regions': regions},
            'success': True,
            'message': 'success'
        }
        self.status_code = codes.OK
