"""
Rewards API Sign Up APi
"""
import datetime

from dateutil.relativedelta import relativedelta
from flask import request

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from repositories.customer_device_repo import CustomerDeviceRepository
from repositories.customer_on_boarding_info_repo import CustomerOnboardingInfoRepository
from repositories.customer_repo import CustomerProfile
from repositories.customer_social_acc_repo import CustomerSocialAccRepository
from repositories.player import PlayerRepository
from repositories.send_email_repo import SendEmailsRepository
from repositories.session_repo import SessionRepository
from repositories.share_offer_repo import ShareOfferRepository
from repositories.translation_repo import MessageRepository
from repositories.vip_group_key import VipGroupKeyRepository
from repositories.vip_group_product_repo import VIPGroupProduct
from repositories.wl_company_repo import WLCompanyRepository
from rewards_api.vr01.sign_up.validation import rewards_user_sign_up_in_parser


class RewardsSignUpApi(BasePostResource):
    """
    Sign up API for the rewards
    """
    backup_request_args_for_exception = False
    request_parser = rewards_user_sign_up_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='rewards_sign_up_api/rewards_sign_up_api.log',
        ),
        'name': 'rewards_sign_up_api'
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
        self.vip_key = self.request_args.get('vip_key')

    def initialize_repos(self):
        """
        Initializes the different repos
        """
        self.vip_group_key_repo_instance = VipGroupKeyRepository()
        self.vip_group_product_repo_instance = VIPGroupProduct()
        self.session_repo_instance = SessionRepository()
        self.message_repo_instance = MessageRepository()
        self.customer_device_repo_instance = CustomerDeviceRepository()
        self.social_repo_instance = CustomerSocialAccRepository()
        self.customer_repo_instance = CustomerProfile(logger=self.logger)
        self.customer_onboarding_info_repo_instance = CustomerOnboardingInfoRepository()
        self.share_offer_repo_instance = ShareOfferRepository()
        self.player_repo_instance = PlayerRepository()
        self.wl_company_repo_instance = WLCompanyRepository()

    def setting_language_and_variables(self):
        """
        Set the locale for user message
        """
        locale = CommonHelpers.get_locale(self.locale, 0)
        self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
        self.session_id = 0
        self.code = 11
        self.message = ""
        self.customer = None
        self.customer_id = None
        self.customer_data = None
        self.session = None
        self.result = None
        self.result_group = None
        self.group_count = 0
        self.is_send_email_for_vip_activation = True

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
                self.request_args['date_of_birth'] = self.date_of_birth

                if self.date_of_birth > current_date or self.date_of_birth < minimum_valid_dob:
                    self.status_code = 422
                    self.send_response_flag = True
                    self.response = {
                        "message": self.message_repo_instance.get_message_by_code(
                        self.message_repo_instance.invalid_dob, self.messages_locale),
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

    def check_on_vip_key(self):
        """
        Checks the customer on the base of the vip key
        """
        if self.vip_key:
            self.result = self.vip_group_key_repo_instance.get_key_info_vc01(self.vip_key)
            if self.result:
                self.is_send_email_for_vip_activation = int(self.result.get('is_email_to_send')) == 1

                if self.result["isreusable"]:
                    self.result_group = self.vip_group_key_repo_instance.get_group_key_info_vc01(self.vip_key)

                    if self.result_group:
                        group_count = self.vip_group_key_repo_instance.get_count_by_group_id(
                            self.result_group["groupId"]
                        )
                        if group_count > self.result_group["usage_limit"]:
                            self.status_code = 422
                            self.send_response_flag = True
                            self.response = {
                                "message": self.message_repo_instance.get_message_by_id(3, self.messages_locale),
                                "code": 70,
                                "success": False
                            }
                            return self.send_response(self.response, self.status_code)
                    else:
                        self.status_code = 422
                        self.send_response_flag = True
                        self.response = {
                            "message": self.message_repo_instance.get_message_by_id(3, self.messages_locale),
                            "code": 70,
                            "success": False
                        }
                        return self.send_response(self.response, self.status_code)
                else:
                    if not self.result['active'] or self.result["isused"]:
                        self.status_code = 422
                        self.send_response_flag = True
                        self.response = {
                            "message": self.message_repo_instance.get_message_by_id(3, self.messages_locale),
                            "code": 70,
                            "success": False
                        }
                        return self.send_response(self.response, self.status_code)
                    elif self.result["isused"] and self.email == self.result["email"]:
                        self.status_code = 422
                        self.send_response_flag = True
                        self.response = {
                            "message": self.message_repo_instance.get_message_by_id(9, self.messages_locale),
                            "code": 70,
                            "success": False
                        }
                        return self.send_response(self.response, self.status_code)
            else:
                self.result_group = self.vip_group_key_repo_instance.get_group_key_info_vc01(self.vip_key)
                if self.result_group:
                    self.is_send_email_for_vip_activation = (int(self.result_group['is_email_to_send']) == 1)
                    group_count = self.vip_group_key_repo_instance.get_count_by_group_id(self.result_group["groupId"])
                    if group_count > self.result_group["usage_limit"]:
                        self.status_code = 422
                        self.send_response_flag = True
                        self.response = {
                            "message": self.message_repo_instance.get_message_by_id(3, self.messages_locale),
                            "code": 70,
                            "success": False
                        }
                        return self.send_response(self.response, self.status_code)
                else:
                    self.status_code = 422
                    self.send_response_flag = True
                    self.response = {
                        "message": self.message_repo_instance.get_message_by_id(3, self.messages_locale),
                        "code": 70,
                        "success": False
                    }
                    return self.send_response(self.response, self.status_code)

    def validate_customer_already_exist(self):
        """
        Validates that user is exists in the db or not.
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

    def set_customer_profile(self):
        """
        Setting the customer profile
        """
        self.customer_profile = self.customer_repo_instance.load_customer_profile_by_user_id(self.customer_id)

    def updating_vip_group_key(self):
        """
        Updates or inserts the vip group key in the DB
        """
        if self.vip_key and self.customer_id:
            if self.result_group:
                self.company_id = self.result_group.get('company_id')
                self.vip_group_key_repo_instance.insert_vip_group_key(
                    self.vip_key,
                    self.result_group["groupId"],
                    self.email,
                    self.customer_id
                )
            else:
                self.company_id = self.result["company_id"]
                self.vip_group_key_repo_instance.update_vip_info(self.vip_key, self.email, self.customer_id)

            if self.is_send_email_for_vip_activation:
                company_name = self.wl_company_repo_instance.get_company_name(self.company_id)
                email_data = {'user_id': self.customer_id}
                optional_data = {
                    "{CONNECT_CLIENT}": company_name,
                    "{FIRST_NAME}": self.customer_profile['firstname']
                }
                self.customer_repo_instance.send_email(
                    email_type_id=SendEmailsRepository.VIP_KEY_ACTIVATION_REWARD_PLUS,
                    email_data=email_data,
                    email=self.email,
                    language=self.locale,
                    priority=SendEmailsRepository.Priority_Medium,
                    optional_data=optional_data
                )
            self.customer_profile = self.customer_repo_instance.update_vip_customer_vc01(self.customer_profile)

    def setting_customer_data_and_token(self):
        """
        Setting the customer data and the sessions for current user
        """
        self.customer_data = self.customer_repo_instance.get_customer_session_data_vc01(
            self.customer_id,
            self.customer_profile
        )
        api_version = self.session_repo_instance.get_api_version(request)
        self.session_id = self.session_repo_instance.generate_session_vc01(
            self.customer_id,
            self.customer_data,
            self.app_version,
            company=api_version,
            last_row=True
        )

        if self.session_id and not self.session:
            self.session = self.session_repo_instance.find_by_id(self.session_id)
        if self.session:
            self.session_token = self.session.get('session_token')
            self.session_id = self.session.get('id')

    def setting_the_customer_device_data(self):
        """
        Settind teh customer device
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
            'siteUID': self.customer_id,
            'device_install_token': self.device_install_token,
            'device_uid': self.device_id,
            'device_os': self.device_os,
            'device_model': self.device_model,
            'is_demographics_updated': 0,
            'verification_state': self.customer_profile.get('verification_state'),
            'is_phone_verified': self.customer_profile.get('is_phone_verified'),
            'validation_params': {
                '__i': self.customer_id,
                '__sid': self.session_id,
                'session_token': self.session_token
            }
        }
        self.response = {
            "message": 'success',
            'data': data,
            'success': True,
            "code": 0
        }
        return self.send_response(self.response, self.status_code)

    def process_request(self):
        self.setting_language_and_variables()
        self.initialize_repos()

        self.test_and_validate_date_of_birth()
        if self.is_send_response_flag_on():
            return

        self.validate_app_version()
        if self.is_send_response_flag_on():
            return

        self.validate_email()
        if self.is_send_response_flag_on():
            return

        self.check_on_vip_key()
        if self.is_send_response_flag_on():
            return

        self.validate_customer_already_exist()
        if self.is_send_response_flag_on():
            return

        self.create_new_customer()
        self.validate_customer_created()
        if self.is_send_response_flag_on():
            return

        self.set_customer_profile()
        self.updating_vip_group_key()
        self.setting_customer_data_and_token()
        self.setting_the_customer_device_data()
        self.generating_final_response()
