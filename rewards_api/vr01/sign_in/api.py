"""
Rewards API Sign in
"""
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
from .validation import reward_user_login_in_parser


class RewardsSignInApi(BasePostResource):
    """
    Sign in Repository for the rewards
    """
    backup_request_args_for_exception = False
    request_parser = reward_user_login_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='rewards_login_api/rewards_login_api.log',
        ),
        'name': 'rewards_login_api'
    }
    logger = None
    status_code = 200
    connections_names = ['default', 'consolidation']

    def populate_request_arguments(self):
        self.email = self.request_args.get('email')  # User Email Address
        self.password = self.request_args.get('password')  # User's password
        self.device_os = self.request_args.get('device_os')  # device os android or ios
        self.device_model = self.request_args.get('device_model')  # device model name
        self.device_install_token = self.request_args.get('device_install_token')  # provided by app
        self.device_id = self.request_args.get('device_uid')  # unique id of the device
        self.social = self.request_args.get('issocial')  # user is social active or not
        self.facebook = self.request_args.get('facebook')  # Token of the facebook
        self.locale = self.request_args.get('language')  # language of the user
        self.app_version = self.request_args.get('app_version')  # application version like 'entertainer'
        self.session_token = self.request_args.get('session_token')  # session token
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

    def check_app_version(self):
        """
        Checks the App version
        """
        if not self.app_version:
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": self.message_repo_instance.get_message_by_code(
                    self.message_repo_instance.upgrade_your_app,
                    self.messages_locale
                ),
                "success": False,
                "code": 70
            }

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

    def social_user_having_email_and_password(self):
        """
        Checks that If user is connected and hav email and the password
        """
        if self.social:
            if not self.email:
                self.send_response_flag = True
                self.status_code = 422
                self.response = {
                    "message": self.message_repo_instance.get_message_by_id(1, self.messages_locale),
                    "success": False,
                    "code": 70
                }
                return self.send_response(self.response, self.status_code)
        else:
            if not self.email or not self.password:
                self.status_code = 422
                self.send_response_flag = True
                self.response = {
                    "message": self.message_repo_instance.get_message_by_id(2, self.messages_locale),
                    "success": False,
                    "code": 70,
                    "data": []
                }
                return self.send_response(self.response, self.status_code)

    def inserting_user_new_social_account(self):
        """
        Inserting new device information into database
        """
        data = {
            'customer_id': self.customer_id,
            'facebook_login': self.facebook,
            'instagram_login': "",
            "twitter_login": ""
        }
        self.social_repo_instance.insert_customer_social_acc_data(data=data)
        self.code = 10
        self.message = self.message_repo_instance.get_message_by_id(5, self.messages_locale)
        self.message = self.message.replace("XXX1", "( " + self.email + " )")

    def load_user_based_on_hash_password(self):
        """
        Loading user if have a valid password hash
        """
        password_hashed = self.customer_repo_instance.get_password_hash(self.email, users=self.users)
        if password_hashed:
            self.customer = self.customer_repo_instance.login_customer(
                self.email,
                self.password,
                password_hashed,
                users=self.users
            )
            if not self.customer:
                self.status_code = 422
                self.send_response_flag = True
                self.response = {
                    "message": self.message_repo_instance.get_message_by_id(42, self.messages_locale),
                    "code": 70,
                    "success": False,
                    "data": []
                }
                return self.send_response(self.response, self.status_code)
        else:
            self.status_code = 422
            self.send_response_flag = True
            self.response = {
                "message": self.message_repo_instance.get_message_by_id(42, self.messages_locale),
                "code": 70,
                "success": False,
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
                    self.result = self.vip_group_key_repo_instance.get_key_info_by_email(self.vip_key, self.email)

                    if self.result:
                        if self.result["active"]:
                            self.status_code = 422
                            self.send_response_flag = True
                            self.response = {
                                "message": self.message_repo_instance.get_message_by_id(9, self.messages_locale),
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
                    if not self.result['active'] or \
                            (self.result["isused"] and self.email != self.result.get('email')):
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

    def loading_customer(self):
        """
        Loading the customer on base of email
        """
        self.users = self.customer_repo_instance.load_customer_by_email(self.email, single=False)
        if self.social:
            self.customer = {}
            if self.users:
                self.customer = self.users[0]
            if self.customer:
                self.customer_id = self.customer.get('id')
                if not self.customer_id:
                    self.status_code = 422
                    self.send_response_flag = True
                    data = {
                        'code': "00",
                        'message': self.message_repo_instance.get_message_by_id(4, self.messages_locale)
                    }
                    self.response = {
                        "message": "success",
                        "success": False,
                        "code": None,
                        "data": data
                    }
                    return self.send_response(self.response, self.status_code)
                else:
                    results = self.social_repo_instance.is_exist(self.customer_id)
                    if not results:
                        self.inserting_user_new_social_account()
            else:
                self.code = "00"
                self.status_code = 200
                self.send_response_flag = True
                data = {'code': "00", 'message': self.message_repo_instance.get_message_by_id(4, self.messages_locale)}
                self.response = {
                    "message": 'success',
                    "data": data,
                    "success": True
                }
                return self.send_response(self.response, self.status_code)
        else:
            self.load_user_based_on_hash_password()

    def set_customer_profile(self):
        """
        Setting the customer profile
        """
        self.customer_id = self.customer['id']
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

    def device_info_of_user(self):
        """
        Loads the user and tests whether have authenticated and limited use of devices
        """
        device_info = self.customer_device_repo_instance.find_one_by_device_id_and_customer_id(
            self.customer_id,
            self.device_id
        )
        if not device_info:
            devices_num = self.customer_device_repo_instance.count_devices_by_customer_id(self.customer_id)
            if devices_num >= CustomerProfile.ALLOWED_NUMBER_OF_DEVICES:
                self.status_code = 422
                self.send_response_flag = True
                self.response = {
                    "message": self.message_repo_instance.get_message_by_id(50, self.messages_locale),
                    "code": 70,
                    "success": False
                }
                return self.send_response(self.response, self.status_code)
            self.customer_device_repo_instance.create_new_record(
                self.customer_id,
                self.device_install_token,
                self.device_os,
                self.device_model,
                self.session,
                0 if devices_num else 1,
                self.device_id
            )

    def getting_player_info(self):
        """
        Getting the player info
        """
        self.player_info = self.player_repo_instance.get_player_by_user_id(self.customer_id)

    def generating_final_response(self):
        """
        Preparing final response
        """
        self.status_code = 200
        self.send_response_flag = True
        data = {
            'code': self.code,
            'message': self.message,
            'user_id': self.customer['id'],
            'session_token': self.session_token,
            'member_type': self.customer_profile['new_member_group'],
            'onboarding_status': self.customer_profile['onboarding_status'],
            'onboarding_limit': CustomerProfile.ONBOARDING_LIMIT,
            'onboarding_redeemed': self.customer_profile['onboarding_redemptions_count'],
            'currency': self.customer_profile['currency'],
            'new_user': False,
            'device_install_token': self.device_install_token,
            'device_uid': self.device_id,
            'device_os': self.device_os,
            'device_model': self.device_model,
            'is_demographics_updated': 0,
            'player_info': self.player_info,
            'verification_state': 0,
            'is_phone_verified': 0,
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
        self.initialize_repos()
        self.setting_language_and_variables()

        self.check_app_version()
        if self.is_send_response_flag_on():
            return

        self.social_user_having_email_and_password()
        if self.is_send_response_flag_on():
            return

        self.check_on_vip_key()
        if self.is_send_response_flag_on():
            return

        self.loading_customer()
        if self.is_send_response_flag_on():
            return

        self.set_customer_profile()
        self.updating_vip_group_key()
        self.setting_customer_data_and_token()
        self.device_info_of_user()
        if self.is_send_response_flag_on():
            return

        self.getting_player_info()
        self.generating_final_response()
