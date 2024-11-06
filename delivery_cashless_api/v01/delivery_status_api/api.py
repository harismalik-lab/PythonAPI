"""
Delivery all statuses API version Delivery Cashless
"""
from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BaseGetResource
from common.db import DEFAULT
from delivery_cashless_api.v01.delivery_status_api.validation import delivery_statuses_parser
from repositories.dm_repositories.dm_delivery_all_statuses_repo import DeliveryStatusesRepository
from user_authentication.authentication import get_current_session_info


class GetDeliveryAllStatusesApi(BaseGetResource):
    """
    Delivery all active statuses api
    """
    required_token = True
    is_delivery_cashless = True
    request_parser = delivery_statuses_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='delivery_all_statuses_api/delivery_all_statuses_api.log',
        ),
        'name': 'delivery_all_statuses_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        current_session_info = get_current_session_info()
        self.merchant_sf_id = current_session_info.get('merchant_sf_id')
        self.outlet_sf_id = current_session_info.get('outlet_sf_id')
        self.device_id = current_session_info.get('device_id')

    def initialize_repos(self):
        """
        Initializes different repos
        """
        self.delivery_statues_repo = DeliveryStatusesRepository()

    def sets_variables(self):
        """
        Set the variables
        """
        self.statuses = None
        self.data = {}
        self.success = False

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.send_response_flag = True
        self.statuses = self.delivery_statues_repo.get_filter_status(filters={'is_sub_status': 0}, single=False)
        self.success = True
        self.message = 'Success'
        self.data = {'delivery_statuses': self.statuses}
        self.response = {
            "message": self.message,
            'data': self.data,
            'success': self.success,
            "code": self.code
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self):
        self.initialize_repos()
        self.sets_variables()
        if self.is_send_response_flag_on():
            return
        self.generating_final_response()
