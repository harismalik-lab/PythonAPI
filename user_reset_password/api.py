"""
Reset Password API
"""
# pylint: disable=import-error
# pylint: disable=unused-import
from flask import current_app
from phpserialize import dumps as php_json_dumps
# pylint: disable=fixme
# pylint: disable=attribute-defined-outside-init
from validate_email import validate_email

from app_configurations.settings import ONLINE_LOG_PATH
from common import translations_constants
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from common.db import CONSOLIDATION, DEFAULT
from common.security import Security
from repositories.customer_repo import CustomerProfile
from repositories.send_email_repo import SendEmailsRepository

from .validation import user_password_reset_in_parser


class UserPasswordResetApi(BasePostResource):
    """
    Setting the api arg_parser and log file path
    """
    backup_request_args_for_exception = False
    request_parser = user_password_reset_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=ONLINE_LOG_PATH,
            file_path='password_reset_api/password_reset_api.log',
        ),
        'name': 'password_reset_api'
    }
    logger = None
    status_code = 200
    connections_names = [DEFAULT, CONSOLIDATION]

    def populate_request_arguments(self):
        """
        Setting the arguments
        """
        self.locale = self.request_args.get('language')
        self.email = self.request_args.get('email')
        self.reset_password = self.request_args.get('reset_password')

    def initialize_repos(self):
        """
        Initializing the repos
        """
        self.customer_repo_instance = CustomerProfile(logger=self.logger)
        self.security_repo_instance = Security()

    def check_email(self):
        if not self.email and self.email != "":
            self.status_code = 422
            self.send_response_flag = True
            self.response = {
                "message": 'Request parameter email is empty',
                "data": []
            }
        else:
            if not validate_email(self.email):
                self.status_code = 422
                self.send_response_flag = True
                self.response = {
                    "message": '{} is not a valid email'.format(self.email),
                    "data": {
                        "message": '{} is not a valid email'.format(self.email)
                    }
                }

    def initialize_attributes(self):
        self.locale = CommonHelpers.get_locale(self.locale, 0)

    def validate_customer(self):
        self.customer = self.customer_repo_instance.load_customer_by_email(self.email)

    def setting_language_and_message(self):
        self.message = "We’ve emailed you a password reset link."
        if self.locale == 'cn':
            self.message = translations_constants.LOCALE_CN_RESET_PASSWORD
        if self.locale == 'ar':
            self.message = translations_constants.LOCALE_AR_RESET_PASSWORD

    def generate_response(self):
        data = {
            'is_sent': True,
            'message': self.message
        }
        self.status_code = 201
        self.send_response_flag = True
        self.response = {
            "message": 'success',
            'data': data,
            "success": True
        }
        return self.send_response(self.response, self.status_code)

    def generate_response_on_no_valid_customer(self):
        code = 55
        self.status_code = 422
        self.send_response_flag = True
        self.response = {
            "message": 'Email address not found.',
            'code': code,
            "data": [],
            "success": False
        }
        return self.send_response(self.response, self.status_code)

    def sending_email_to_customer(self):
        if self.customer:
            password_reset_token = self.security_repo_instance.generate_random_string(length=20)
            self.customer_repo_instance.update_password_reset_token(
                self.customer['id'],
                password_reset_token
            )
            email_data = php_json_dumps({
                "user_id": self.customer['id'],
                "{PASSWORD_RESET_URL}": '{password_reset_url}{password_reset_token}'.format(
                    password_reset_url=current_app.config.get('PASSWORD_RESET_URL'),
                    password_reset_token=password_reset_token
                )
            })
            self.customer_repo_instance.send_email(
                SendEmailsRepository.FORGOT_PASSWORD,
                email_data=email_data.decode(errors='ignore'),
                email=self.email,
                language=self.locale,
                priority=SendEmailsRepository.Priority_High,
                dump=False,
                optional_data=None
            )
        self.setting_language_and_message()
        self.generate_response()

    def process_request(self):
        """
        Process the request
        :return: Response
        """
        self.check_email()
        if self.is_send_response_flag_on():
            return

        self.initialize_repos()
        self.initialize_attributes()
        self.validate_customer()
        self.sending_email_to_customer()
