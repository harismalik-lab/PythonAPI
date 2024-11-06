"""
This module contains the Outlets api endpoints
"""
from operator import itemgetter
from flask import current_app

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT
from repositories.customer_repo import CustomerProfile
from repositories.session_repo import SessionRepository
from user_authentication.authentication import get_current_customer
from .validation_outlet_tabs import outlet_tabs_parser


class RewardsGetTabsAction(BaseGetResource):

    request_parser = outlet_tabs_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='outlet_api/rewards_outlet_api.log',
        ),
        'name': 'rewards_tabs_action'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        self.location_id = self.request_args.get('location_id')
        self.session_token = self.request_args.get('session_token')
        self.locale = CommonHelpers.get_locale(self.request_args.get('language'), self.location_id)
        self.customer = {}

    def load_customer(self):
        session = SessionRepository().find_by_token(session_token=self.session_token)
        user_id = 0
        if session:
            user_id = session.get('customer_id')
        if user_id:
            self.customer['purchased_skus'] = self.customer_repo.get_customer_products_vc01(user_id)

    def initialize_repos(self):
        self.customer_repo = CustomerProfile(logger=self.logger)

    def get_tabs(self):
        self.tabs = self.customer_repo.get_tabs_vc01(self.customer['purchased_skus'], self.locale)

    def process_request(self):
        self.initialize_repos()
        self.load_customer()
        self.get_tabs()
        self.set_response({
            'data': {
                'limit': self.customer_repo.MAX_OUTLETS,
                'tabs': self.tabs
            },
            'message': 'success',
            'success': True
        })
