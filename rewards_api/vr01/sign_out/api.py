"""
Rewards Sign out api
"""
from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BasePostResource
from repositories.session_repo import SessionRepository
from web_api.sign_out.validation_logout import user_sign_out_parser


class RewardsLogoutApi(BasePostResource):
    strict_token = True
    required_token = True
    request_parser = user_sign_out_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='rewards_logout_api/rewards_logout_api.log',
        ),
        'name': 'rewards_logout_api'
    }
    logger = None
    status_code = 200
    connections_names = ['default']

    def populate_request_arguments(self):
        """
        Populates the request argument
        """
        self.user_id = self.request_args.get('__i')
        self.session_id = self.request_args.get('__sid')
        self.session_token = self.request_args.get('session_token')

    def initialize_repos(self):
        """
        Initializes the different repos
        """
        self.session_repo_instance = SessionRepository()

    def process_request(self):
        self.initialize_repos()
        session = self.session_repo_instance.find_by_id(session_id=self.session_id)
        if session:
            session['isactive'] = False
            self.session_repo_instance.remove_session(self.session_id)

        self.send_response_flag = True
        self.response = {
            "message": 'success',
            "success": True,
            "data": [],
            "code": 0
        }
        return self.send_response(self.response, self.status_code)
