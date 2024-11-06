"""
User Sign up api
"""
import datetime
import threading

from dateutil.relativedelta import relativedelta
from flask import request

from app_configurations.settings import ONLINE_LOG_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from repositories.customer_device_repo import CustomerDeviceRepository
from repositories.customer_on_boarding_info_repo import CustomerOnboardingInfoRepository
from repositories.customer_repo import CustomerProfile
from repositories.customer_social_acc_repo import CustomerSocialAccRepository
from repositories.session_repo import SessionRepository
from repositories.share_offer_repo import ShareOfferRepository
from repositories.translation_repo import MessageRepository

from .validation import user_sign_up_in_parser


class SignUpApi(BasePostResource):
    backup_request_args_for_exception = False
    request_parser = user_sign_up_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=ONLINE_LOG_PATH,
            file_path='sign_up_api/sign_up_api.log',
        ),
        'name': 'sign_up_api'
    }
    logger = None
    status_code = 200
    connections_names = ['default', 'consolidation']

    def populate_request_arguments(self):
        self.locale = self.request_args.get('language')  # language of the user
        self.is_social = self.request_args.get('social_registration')  # user is
        self.facebook_id = self.request_args.get('facebook')  # facebook id
        self.email = self.request_args.get('email')
        self.password = self.request_args.get('password')
        self.device_os = self.request_args.get('device_os')  # required (device_os)
        self.device_model = self.request_args.get('device_model')
        self.device_install_token = self.request_args.get('device_install_token')  # provided by app
        self.device_id = self.request_args.get('device_uid')  # unique id of the device
        self.app_version = self.request_args.get('app_version')
        self.nationality = self.request_args.get('nationality')
        self.date_of_birth = self.request_args.get('date_of_birth')
        self.device_key = self.request_args.get('device_key')
        self.affiliate_code = self.request_args.get('affiliate_code')
        self.location_id = self.request_args.get('location_id')
        self.first_name = self.request_args.get('firstname')
        self.last_name = self.request_args.get('lastname')
        self.device_key = self.request_args.get('device_key')
        self.country_of_residence = self.request_args.get('country_of_residence')
        self.confirm_password = self.request_args.get('confirm_password')
        self.gender = self.request_args.get('gender')
        self.mobile_phone = self.request_args.get('mobile_phone')

    def initialize_repos(self):
        """
        Initializes the different repos
        """
        self.message_repo_instance = MessageRepository()
        self.share_offer_repo_instance = ShareOfferRepository()
        self.customer_device_repo_instance = CustomerDeviceRepository()
        self.customer_repo_instance = CustomerProfile(logger=self.logger)
        self.customer_onboarding_info_repo_instance = CustomerOnboardingInfoRepository()
        self.social_repo_instance = CustomerSocialAccRepository()
        self.session_repo_instance = SessionRepository()

    def setting_language_and_variables(self):
        """
        Set the locale for user message
        """
        locale = CommonHelpers.get_locale(self.locale, self.location_id)  # noqa: F841
        self.messages_locale = CommonHelpers.get_locale_for_messaging(self.request_args.get('language'))
        self.session_id = 0
        self.session = None
        self.result = None
        self.result_group = None
        self.customer_data = None
        self.customer_profile = None
        self.session_token = ""

    def setting_device_id(self):
        """
        Sets the device id
        """
        if self.device_key:
            self.device_id = self.device_key

    def checking_device_os(self):
        if self.device_os:
            if self.device_os.lower() == "wp":
                self.send_response_flag = True
                self.status_code = 422
                self.response = {
                    "message": self.message_repo_instance.end_of_life_message_for_windows_app_user,
                    "success": False,
                    "code": 70
                }
                return self.send_response(self.response, self.status_code)

    def check_device_black_listed(self):
        """
        Checking the blacklisted device
        """
        if self.customer_device_repo_instance.is_device_linked_to_blacklisted_user(self.device_id):
            self.status_code = 422
            self.send_response_flag = True
            self.response = {
                "message": self.message_repo_instance.device_blacklisted,
                "code": 70,
                "success": False
            }
            return self.send_response(self.response, self.status_code)

    def test_and_validate_date_of_birth(self):
        is_valid_date_of_birth = True
        if self.date_of_birth and self.date_of_birth != "":
            try:
                self.date_of_birth = self.date_of_birth.replace('/', '-')
                self.date_of_birth = datetime.datetime.strptime(self.date_of_birth, '%Y-%m-%d')
                current_date = datetime.datetime.now()
                date_13_years_back = datetime.datetime.now() - relativedelta(years=13)
                date_13_years_back = datetime.datetime.strftime(date_13_years_back, '%Y-%m-%d')
                date_13_years_back = datetime.datetime.strptime(date_13_years_back, '%Y-%m-%d')
                minimum_valid_dob = datetime.datetime.now() - relativedelta(years=120)
                minimum_valid_dob = datetime.datetime.strftime(minimum_valid_dob, '%Y-%m-%d')
                minimum_valid_dob = datetime.datetime.strptime(minimum_valid_dob, '%Y-%m-%d')

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
                            self.message_repo_instance.dob_minimum_value_error, self.messages_locale),
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
                    self.message_repo_instance.invalid_dob, self.messages_locale),
                "code": 90,
                "success": False
            }
            return self.send_response(self.response, self.status_code)

    def validate_app_version(self):
        """
        Validates the app version
        """
        if not self.app_version:
            self.status_code = 422
            self.send_response_flag = True
            self.response = {
                "message": self.message_repo_instance.get_message_by_code(
                    self.message_repo_instance.upgrade_your_app, self.messages_locale),
                "code": 70,
                "success": False,
                "data": []
            }
            return self.send_response(self.response, self.status_code)

    def validate_customer_already_exist(self):
        """
        Validates the customer exists in the db or not
        """
        customer_exist = self.customer_repo_instance.load_customer_by_email(self.email)
        if customer_exist:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": self.message_repo_instance.get_message_by_id(19, self.messages_locale),
                "success": False,
                "code": 90,
                "data": []
            }
            return self.send_response(self.response, self.status_code)

    def check_first_name(self):
        """
        Checks the first name of user
        """
        if not self.first_name:
            self.send_response_flag = True
            self.status_code = 500
            self.response = {
                "message": "Request parameter firstname is empty",
                "success": False,
                "code": 0,
                "data": []
            }
            return self.send_response(self.response, self.status_code)

    def check_last_name(self):
        """
        Checks the last name of user
        """
        if not self.last_name:
            self.send_response_flag = True
            self.status_code = 500
            self.response = {
                "message": "Request parameter lastname is empty",
                "success": False,
                "code": 0,
                "data": []
            }
            return self.send_response(self.response, self.status_code)

    def check_country_of_residence(self):
        """
        Checks the county of residence
        :return:
        """
        if not self.country_of_residence:
            self.send_response_flag = True
            self.status_code = 500
            self.response = {
                "message": "Request parameter country_of_residence is empty",
                "success": False,
                "code": 0,
                "data": []
            }
            return self.send_response(self.response, self.status_code)

        if len(self.country_of_residence) > 2:
            self.send_response_flag = True
            self.status_code = 500
            self.response = {
                "message": self.customer_repo_instance.COUNTRY_OF_RESIDENCE_ERROR_MESSAGE.format(
                    country=self.country_of_residence, value={2}
                ),
                "success": False,
                "code": 0,
                "data": []
            }
            return self.send_response(self.response, self.status_code)

    def check_confirm_password(self):
        if not self.is_social and not self.confirm_password:
            self.send_response_flag = True
            self.status_code = 500
            self.response = {
                "message": "Request parameter confirm_password is empty",
                "success": False,
                "code": 0,
                "data": []
            }
            return self.send_response(self.response, self.status_code)

    def create_new_customer(self):
        self.customer_id = self.customer_repo_instance.create_new_customer(self.request_args)

    def validate_customer_created(self):
        if not self.customer_id:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": self.message_repo_instance.get_message_by_id(16, self.messages_locale),
                "success": False,
                "code": 90
            }
            return self.send_response(self.response, self.status_code)

    def send_email_to_user(self):
        email_data = {'user_id': self.customer_id}  # noqa: F841
        # TODO: Welcome email disabled on prod for now.
        # self.customer_repo_instance.send_email(
        #     email_type_id=SendEmailsRepository.ACTIVATION_OF_TRIAL,
        #     email=self.email,
        #     email_data=email_data,
        #     language=self.locale
        # )

    def setting_customer_data(self):
        """
        Setting the customer data and the customer profile
        """
        self.customer_profile = self.customer_repo_instance.load_customer_profile_by_user_id(self.customer_id)
        self.customer_profile = self.customer_repo_instance.put_customer_in_trial_membership_if_qualifies(
            self.customer_id,
            self.customer_profile
        )
        self.customer_data = self.customer_repo_instance.get_customer_session_data(
            self.customer_id,
            self.customer_profile
        )

    def setting_session(self):
        """
        Sets the session data and the session id
        """
        api_version = self.session_repo_instance.get_api_version(request)
        session_id = self.session_repo_instance.generate_session(
            self.customer_id,
            self.customer_data,
            self.app_version,
            api_version,
            last_row=True
        )
        self.session = self.session_repo_instance.find_by_id(session_id)
        if self.session:
            self.session_id = self.session.get('id')
            self.session_token = self.session.get('session_token')

    def setting_the_customer_device_data(self):
        """
        Setting the customer device
        :return:
        """
        self.customer_device_repo_instance.create_new_record(
            self.customer_id,
            self.device_install_token,
            self.device_os,
            self.device_model,
            self.session, 1,
            self.device_id
        )
        if self.is_social:
            data = {
                'customer_id': self.customer_id,
                'facebook_id': self.facebook_id
            }
            self.social_repo_instance.insert_customer_social_acc_data(data=data)
        self.share_offer_repo_instance.update_customer_id_shared_offer(
            self.email,
            self.customer_id
        )

    def finish_onboarding(self):
        """
        Finishing the on boarding of the user
        """
        if self.device_key:
            on_boarding_device_info = self.customer_onboarding_info_repo_instance.get_onboarding_info_by_key(
                self.device_key)
            self.customer_onboarding_info_repo_instance.insert_customer_onboarding_info(
                self.customer_id,
                self.device_os,
                self.device_key,
                (not on_boarding_device_info) if 1 else 0
            )
            if (
                on_boarding_device_info and
                self.customer_profile['new_member_group'] == CustomerProfile.MEMBERSTATUS_ONBOARDING
            ):
                self.customer_profile = self.customer_repo_instance.finish_on_boarding(self.customer_id)
                self.customer_data = self.customer_repo_instance.get_customer_session_data(
                    self.customer_id,
                    self.customer_profile
                )
                if self.session_token:
                    if not self.session:
                        self.session = self.session_repo_instance.find_by_token(self.session_token)
                    data = self.session_repo_instance.dumps(self.customer_data)
                    self.session_repo_instance.update_session_data(data=data, customer_id=self.customer_id)

    def validate_email(self):
        if not self.email:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": self.message_repo_instance.get_message_by_id(11, self.messages_locale),
                "success": False,
                "code": 70,
                "data": []
            }
            return self.send_response(self.response, self.status_code)

    def credit_smiles(self):
        host = getattr(request, 'remote_addr', '')
        self.customer_repo_instance.credit_smiles_to_referrer(host, self.customer_id, self.messages_locale)

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.status_code = 200
        self.send_response_flag = True
        data = {
            'user_id': self.customer_id,
            'session_token': self.session_token,
            'member_type': self.customer_profile['new_member_group'],
            'onboarding_status': self.customer_profile['onboarding_status'],
            'onboarding_limit': CustomerProfile.ONBOARDING_LIMIT,
            'onboarding_redeemed': self.customer_profile['onboarding_redemptions_count'],
            'currency': self.customer_profile['currency'],
            'new_user': True,
            'sitUID': self.customer_id,
            'device_install_token': self.device_install_token,
            'device_uid': self.device_id,
            'device_os': self.device_os,
            'device_model': self.device_model,
            'is_demographics_updated': 0,
            'affiliate_code': (self.customer_profile['affiliate_code']
                               if self.customer_profile.get('affiliate_code') else ""),
            'validation_params': {
                '__i': self.customer_id,
                '__sid': self.session_id,
                'session_token': self.session_token}
        }
        self.response = {
            "message": 'success',
            'data': data,
            'success': True,
            "code": None
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self):
        self.setting_device_id()
        self.initialize_repos()
        self.setting_language_and_variables()
        self.checking_device_os()
        if self.is_send_response_flag_on():
            return

        self.check_device_black_listed()
        if self.is_send_response_flag_on():
            return

        self.test_and_validate_date_of_birth()
        if self.is_send_response_flag_on():
            return

        self.validate_app_version()
        if self.is_send_response_flag_on():
            return

        # validating at the request parser
        self.validate_email()
        if self.is_send_response_flag_on():
            return

        self.check_first_name()
        if self.is_send_response_flag_on():
            return

        self.check_last_name()
        if self.is_send_response_flag_on():
            return

        self.check_country_of_residence()
        if self.is_send_response_flag_on():
            return

        self.check_confirm_password()
        if self.is_send_response_flag_on():
            return

        self.validate_customer_already_exist()
        if self.is_send_response_flag_on():
            return

        self.create_new_customer()
        self.validate_customer_created()
        if self.is_send_response_flag_on():
            return

        thread = threading.Thread(target=self.credit_smiles(), args=())
        thread.daemon = True
        thread.start()
        self.send_email_to_user()
        self.setting_customer_data()
        self.setting_session()
        self.setting_the_customer_device_data()
        self.finish_onboarding()
        self.generating_final_response()
