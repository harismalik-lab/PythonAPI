"""
User logout API
"""
from app_configurations.settings import ONLINE_LOG_PATH
from common.base_resource import BasePostResource
from repositories.session_repo import SessionRepository
from user_authentication.authentication import get_current_customer

from .validation_logout import user_sign_out_parser


class LogoutUserApi(BasePostResource):
    strict_token = True
    required_token = True
    family_authentication = False
    request_parser = user_sign_out_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=ONLINE_LOG_PATH,
            file_path='logout_api/logout_api.log',
        ),
        'name': 'logout_api'
    }
    logger = None
    status_code = 200
    connections_names = ['default']

    def populate_request_arguments(self):
        """
        Populates the request argument
        """
        self.session_id = self.request_args.get('__sid')

    def initialize_repos(self):
        """
        Initializes the different repos
        """
        self.session_repo_instance = SessionRepository()

    def process_request(self):
        self.initialize_repos()
        customer = get_current_customer()
        session_id = customer.get('id')
        self.session_repo_instance.remove_session(session_id)
        self.send_response_flag = True
        self.response = {
            "message": 'success',
            "success": True,
            "data": [],
            "code": 0
        }
        return self.send_response(self.response, self.status_code)
