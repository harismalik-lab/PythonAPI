"""
Sessions Update api of rewards
"""
from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from repositories.customer_repo import CustomerProfile
from repositories.player import PlayerRepository
from repositories.send_email_repo import SendEmailsRepository
from repositories.session_repo import SessionRepository
from repositories.translation_repo import MessageRepository
from repositories.vip_group_key import VipGroupKeyRepository
from repositories.wl_company_repo import WLCompanyRepository
from rewards_api.vr01.sessions_update.validation import rewards_user_session_update


class RewardsSessionsUpdate(BasePostResource):
    """
    Class Contains all the methods for
    """
    backup_request_args_for_exception = False
    request_parser = rewards_user_session_update
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='rewards_sessions_update_api/rewards_sessions_update_api.log',
        ),
        'name': 'rewards_sessions_update_api'
    }
    logger = None
    status_code = 200
    connections_names = ['default', 'consolidation']

    def populate_request_arguments(self):
        self.vip_key = self.request_args.get('vip_key')  # vip key of customer
        self.customer_id = self.request_args.get('customer_id')  # customer id
        self.device_os = self.request_args.get('device_os')  # device os android or ios
        self.device_model = self.request_args.get('device_model')  # device model name
        self.device_install_token = self.request_args.get('device_install_token')  # provided by app
        self.device_id = self.request_args.get('device_uid')  # unique id of the device
        self.locale = self.request_args.get('language')  # language of the user
        self.app_version = self.request_args.get('app_version')  # application version like 'entertainer'
        self.session_token = self.request_args.get('session_token')  # session token

    def initialize_repos(self):
        """
        Initializes the different repos
        """
        self.vip_group_key_repo_instance = VipGroupKeyRepository()
        self.session_repo_instance = SessionRepository()
        self.message_repo_instance = MessageRepository()
        self.customer_repo_instance = CustomerProfile(logger=self.logger)
        self.player_repo_instance = PlayerRepository()
        self.wl_company_repo_instance = WLCompanyRepository()

    def setting_language_and_variables(self):
        """
        Set the locale for user message
        """
        self.messages_locale = CommonHelpers.get_locale(self.locale, 0)
        # self.messages_locale = CommonHelpers.get_locale_for_messaging(locale)
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

    def load_customer(self):
        """
        Loads the customer
        """
        self.customer = self.customer_repo_instance.load_customer_by_id(self.customer_id)
        if self.customer:
            self.email = self.customer.get('email')

    def check_on_vip_key(self):
        """
        Checks the customer on the base of the vip key
        """
        if self.vip_key:
            self.result = self.vip_group_key_repo_instance.get_key_info_vc01(self.vip_key)
            if self.result:
                self.result = self.result[0]
                self.is_send_email_for_vip_activation = int(self.result.get['is_email_to_send']) == 1

                if self.result["isReusable"] == "true":
                    self.result = self.vip_group_key_repo_instance.get_key_info_by_email(self.vip_key, self.email)

                    if self.result:
                        self.result = self.result[0]
                        if self.result["active"] == "true":
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
                            if group_count > self.result_group["usageLimit"]:
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
                    if self.result.get('active') == "false" or \
                            (self.result["isused"] == "true" and self.email != self.result.get('email')):
                        self.status_code = 422
                        self.send_response_flag = True
                        self.response = {
                            "message": self.message_repo_instance.get_message_by_id(3, self.messages_locale),
                            "code": 70,
                            "success": False
                        }
                        return self.send_response(self.response, self.status_code)
                    elif self.result["isused"] == "true" and self.email == self.result["email"]:
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
                    if group_count > self.result_group["usageLimit"]:
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
            self.message = self.message_repo_instance.get_message_by_id(10, self.messages_locale)

    def setting_customer_data_and_token(self):
        """
        Setting the customer data and the sessions for current user
        """
        self.customer_data = self.customer_repo_instance.get_customer_session_data_vc01(
            self.customer_id,
            self.customer_profile
        )
        if self.session_token:
            self.session_repo_instance.update_session(
                session_token=self.session_token,
                customer_data=self.customer_data,
                app_version=self.app_version,
                company='Slice'
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
            'player_info': self.player_info,
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
        self.load_customer()
        self.check_on_vip_key()
        if self.is_send_response_flag_on():
            return

        self.set_customer_profile()
        self.updating_vip_group_key()
        self.setting_customer_data_and_token()
        self.getting_player_info()
        self.generating_final_response()
