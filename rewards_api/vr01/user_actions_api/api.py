"""
Users actions for rewards api
"""
import datetime

from dateutil.relativedelta import relativedelta

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource, BasePutResource, BasePostResource
from common.common_helpers import CommonHelpers
from common.db import DEFAULT, CONSOLIDATION
from repositories.customer_languages_repo import CustomerLanguageRepository
from repositories.customer_repo import CustomerProfile
from repositories.redemption_repo import RedemptionRepository
from repositories.session_repo import SessionRepository
from repositories.translation_repo import MessageRepository
from rewards_api.vr01.user_actions_api.user_savings_validation import rewards_user_savings_action_in_parser
from user_authentication.authentication import get_current_customer
from web_api.get_user_actions.get_user_validation import get_user_action_in_parser
from web_api.post_user_actions.post_user_languages_validation import post_user_languages_in_parser
from web_api.post_user_actions.post_user_validation import post_user_in_parser
from web_api.post_user_actions.user_dempgraphic_validation import post_demographic_update_in_parser


class RewardsGetUserApi(BaseGetResource):
    strict_token = True
    required_token = True
    backup_request_args_for_exception = False
    request_parser = get_user_action_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='rewards_get_user_api/rewards_get_user_api.log',
        ),
        'name': 'rewards_get_user_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT, CONSOLIDATION]

    def populate_request_arguments(self):
        """
        Setting the arguments
        """
        self.currency = self.request_args.get('currency')
        self.location_id = self.request_args.get('location_id')
        self.locale = self.request_args.get('language')

    def initialize_repos(self):
        """
        Initializing the repos
        """
        self.message_repo_instance = MessageRepository()
        self.customer_repo_instance = CustomerProfile(logger=self.logger)

    def initialize_class_attributes(self):
        locale = CommonHelpers.get_locale(self.locale, 0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
        self.customer = get_current_customer()
        self.customer_id = self.customer.get('customer_id')
        self.user_id = None
        self.result = None

    def validate_customer(self):
        # Throw an Error if user_id do not match with customer_id stored in session data
        if self.customer_id != self.user_id:
            self.send_response_flag = True
            self.status_code = 403
            self.response = {
                "message": self.message_repo_instance.get_message_by_id(14, self.messages_locale),
                "success": False,
                "code": 50
            }
            return self.send_response(self.response, self.status_code)

    def get_customer_profile_and_data(self):
        self.result = self.customer_repo_instance.get_customer_profile(self.user_id)

    def generate_final_response(self):
        self.send_response_flag = True
        self.status_code = 200
        self.response = {
            "message": 'success',
            "data": self.result,
            "success": True,
            "code": None
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self, *args, **kwargs):
        """
        Process the request
        :return: Response
        """
        self.initialize_repos()
        self.initialize_class_attributes()
        self.user_id = kwargs.get('user_id')

        self.validate_customer()
        if self.is_send_response_flag_on():
            return

        self.get_customer_profile_and_data()
        self.generate_final_response()


class RewardsPostUserApi(BasePutResource):
    strict_token = True
    required_token = True
    backup_request_args_for_exception = False
    request_parser = post_user_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='post_user_api/post_user_api.log',
        ),
        'name': 'post_user_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT, CONSOLIDATION]

    def populate_request_arguments(self):
        """
        Setting the arguments
        """
        self.language_preference = self.request_args.get('language_preference')
        self.date_of_birth = self.request_args.get('date_of_birth')
        self.locale = self.request_args.get('language')  # language of the user

    def initialize_repos(self):
        """
        Initializing the repos
        """
        self.message_repo_instance = MessageRepository()
        self.customer_repo_instance = CustomerProfile(logger=self.logger)

    def initialize_attributes(self):
        self.messages_locale = CommonHelpers.get_locale_for_messaging(self.locale)

    def test_and_validate_date_of_birth(self):
        is_valid_date_of_birth = True
        if self.date_of_birth and self.date_of_birth != "":
            try:
                self.date_of_birth = self.date_of_birth.replace('/', '-')
                self.date_of_birth = datetime.datetime.strptime(self.date_of_birth, '%d-%m-%Y')
                current_date = datetime.datetime.now()
                date_13_years_back = datetime.datetime.now() - relativedelta(years=13)
                date_13_years_back = datetime.datetime.strftime(date_13_years_back, '%d-%m-%Y')
                date_13_years_back = datetime.datetime.strptime(date_13_years_back, '%d-%m-%Y')
                minimum_valid_dob = datetime.datetime.now() - relativedelta(years=120)
                minimum_valid_dob = datetime.datetime.strftime(minimum_valid_dob, '%d-%m-%Y')
                minimum_valid_dob = datetime.datetime.strptime(minimum_valid_dob, '%d-%m-%Y')

                if self.date_of_birth > current_date or self.date_of_birth < minimum_valid_dob:
                    self.status_code = 422
                    self.send_response_flag = True
                    self.response = {
                        "message": self.message_repo_instance.get_message_by_code(
                            self.message_repo_instance.invalid_dob, self.messages_locale
                        ),
                        "code": 90,
                        "success": False
                    }
                    return self.send_response(self.response, self.status_code)

                if date_13_years_back < self.date_of_birth:
                    self.status_code = 422
                    self.send_response_flag = True
                    self.response = {
                        "message": self.message_repo_instance.get_message_by_code(
                            self.message_repo_instance.dob_minimum_value_error, self.messages_locale
                        ),
                        "code": 90,
                        "success": False
                    }
                    return self.send_response(self.response, self.status_code)
            except Exception:
                is_valid_date_of_birth = False
        if not is_valid_date_of_birth:
            self.status_code = 422
            self.send_response_flag = True
            self.response = {
                "message": self.message_repo_instance.get_message_by_code(
                    self.message_repo_instance.invalid_dob, self.messages_locale
                ),
                "code": 90,
                "success": False
            }
            return self.send_response(self.response, self.status_code)

    def update_customer(self):
        self.cutomer_updated = self.customer_repo_instance.update_customer_profile(self.user_id, self.request_args)

    def check_updated_customer_and_generate_final_response(self):
        if self.cutomer_updated:
            self.status_code = 200
            self.send_response_flag = True
            self.response = {
                "message": "success",
                "success": True,
                "data": []
            }
            return self.send_response(self.response, self.status_code)
        else:
            self.send_response_flag = True
            self.status_code = 400
            self.response = {
                "message": self.message_repo_instance.get_message_by_id(16, self.messages_locale),
                "success": False,
                "code": 95
            }
            return self.send_response(self.response, self.status_code)

    def process_request(self, *args, **kwargs):
        """
        Process the request
        :return: Response
        """
        self.initialize_attributes()
        self.initialize_repos()
        self.user_id = kwargs.get('user_id')
        self.test_and_validate_date_of_birth()
        if self.is_send_response_flag_on():
            return

        self.update_customer()
        self.check_updated_customer_and_generate_final_response()


class RewardsUserSavingsAPI(BaseGetResource):
    """
    Setting the api arg_parser and log file path
    """
    strict_token = True
    required_token = True
    backup_request_args_for_exception = False
    request_parser = rewards_user_savings_action_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='rewards_user_savings_api/rewards_user_savings_api.log',
        ),
        'name': 'rewards_user_savings_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT]

    def populate_request_arguments(self):
        """
        Setting the arguments
        """
        self.currency = self.request_args.get('currency')
        self.magento_customer_id = self.request_args.get('magento_customer_id')
        self.locale = self.request_args.get('language')
        self.platform = self.request_args.get('__platform')

    def initialize_repos(self):
        """
        Initializing the repos
        """
        self.customer_repo_instance = CustomerProfile(logger=self.logger)

    def intialize_variables(self):
        customer = get_current_customer()
        self.customer_id = customer.get('customer_id')
        self.current_year = str(datetime.datetime.now().year)

    def fetch_user_savings(self):
        self.savings = self.customer_repo_instance.get_user_savings_vc01(
            self.customer_id,
            self.current_year,
            self.currency,
            self.platform
        )
        self.savings['is_average_product_value_exceeded'] = \
            (self.savings['savings'] >= RedemptionRepository.Average_Product_Value_AED)

    def generate_final_response(self):
        self.send_response_flag = True
        self.status_code = 200
        self.response = {
            "message": 'success',
            "data": self.savings,
            "success": True,
            "code": None
        }

    def process_request(self, *args, **kwargs):
        """
        Process the request
        :return: Response
        """
        self.initialize_repos()
        self.intialize_variables()
        self.fetch_user_savings()
        self.generate_final_response()


class RewardsPostUserLanguagesApi(BasePostResource):
    backup_request_args_for_exception = False
    request_parser = post_user_languages_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='post_user_languages_api/post_user_languages_api.log',
        ),
        'name': 'post_user_languages_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT, CONSOLIDATION]

    def populate_request_arguments(self):
        """
        Setting the arguments
        """
        self.locale = self.request_args.get('language')
        self.session_token = self.request_args.get('session_token')

    def check_session_token(self):
        if not self.session_token:
            self.send_response_flag = True
            self.status_code = 403
            self.response = {
                "message": "Session Token is missing",
                "code": 403
            }

    def initialize_repos(self):
        """
        Initializing the repos
        """
        self.session_repo_instance = SessionRepository()
        self.customer_language_repo_instance = CustomerLanguageRepository()

    def get_session(self):
        self.session = self.session_repo_instance.find_by_token(self.session_token)

    def setting_variables_and_inserting_language(self):
        self.locale = CommonHelpers.get_locale(self.locale, 0)
        session_id = self.session.get('id')
        self.customer_id = self.session.get('customer_id')
        self.customer_language_repo_instance.insert_customer_language(
            self.customer_id,
            session_id,
            self.locale
        )

    def generate_final_response(self):
        self.send_response_flag = True
        self.status_code = 200
        self.response = {
            "message": 'success',
            "data": [],
            "success": True,
            "code": None
        }

    def process_request(self, *args, **kwargs):
        """
        Process the request
        :return: Response
        """
        self.check_session_token()
        if self.is_send_response_flag_on():
            return

        self.initialize_repos()
        self.get_session()
        self.setting_variables_and_inserting_language()
        self.generate_final_response()


class RewardsUserUpdateDemographicStateApi(BasePostResource):
    strict_token = True
    required_token = True
    backup_request_args_for_exception = False
    request_parser = post_demographic_update_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='post_user_update_demographic_api/post_user_update_demographic_api.log',
        ),
        'name': 'post_user_update_demographic_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT, CONSOLIDATION]

    def populate_request_arguments(self):
        """
        Setting the arguments
        """
        self.user_id = self.request_args.get('user_id')
        self.app_version = self.request_args.get('app_version')
        self.locale = self.request_args.get('language')

    def check_user_id(self):
        if not self.user_id:
            self.status_code = 500
            self.send_response_flag = True
            self.response = {
                "message": "Request parameter user_id is empty.",
                "code": 500,
                "success": False
            }
            return self.send_response(self.response, self.status_code)

    def initialize_repos(self):
        """
        Initializing the repos
        """
        self.customer_repo_instance = CustomerProfile(logger=self.logger)

    def initialize_attributes(self):
        self.locale = CommonHelpers.get_locale(self.locale, 0)

    def update_demographic_and_data(self):
        is_verification_state_updated = self.customer_repo_instance.update_demographic_state(
            self.user_id,
            self.locale
        )
        self.data = {
            'is_verification_state_updated': is_verification_state_updated
        }

    def generate_final_response(self):
        self.send_response_flag = True
        self.status_code = 200
        self.response = {
            "message": 'success',
            "data": self.data,
            "success": True,
            "code": None
        }

    def process_request(self, *args, **kwargs):
        """
        Process the request
        :return: Response
        """
        self.check_user_id()
        if self.is_send_response_flag_on():
            return

        self.initialize_attributes()
        self.initialize_repos()
        self.update_demographic_and_data()
        self.generate_final_response()
