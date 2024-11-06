"""
User Login API
"""
import threading

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
from user_authentication.authentication import set_customer_and_device_id

from .validation import user_login_in_parser


class LoginUserApi(BasePostResource):
    backup_request_args_for_exception = False
    request_parser = user_login_in_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=ONLINE_LOG_PATH,
            file_path='login_api/login_api.log',
        ),
        'name': 'login_api'
    }
    logger = None
    status_code = 200
    connections_names = ['default', 'consolidation']

    def __init__(self, *args, **kwargs):
        """
        Initialize instance attribute.
        """
        self.is_sign_in_from_sign_up = False
        super(LoginUserApi, self).__init__(*args, **kwargs)

    def populate_request_arguments(self):
        self.email = self.request_args.get('email')  # User Email Address
        self.password = self.request_args.get('password')  # User's password
        self.device_os = self.request_args.get('__platform')  # device os android or ios
        self.device_model = self.request_args.get('device_model')  # device model name
        self.device_install_token = self.request_args.get('device_install_token')  # provided by app
        self.device_id = self.request_args.get('device_uid')  # unique id of the device
        self.social = self.request_args.get('issocial')  # user is social active or not
        self.facebook = self.request_args.get('facebook')  # Token of the facebook
        self.locale = self.request_args.get('language')  # language of the user
        self.app_version = self.request_args.get('app_version')  # application version like 'entertainer'
        self.device_key = self.request_args.get('device_key')  # generated key from the device
        self.location_id = self.request_args.get('location_id')  # Location id
        self.session_token = self.request_args.get('session_token')  # session token

    def changed_repositories(self):
        self.session_repo_instance = SessionRepository()
        self.customer_repo_instance = CustomerProfile(logger=self.logger)

    def initialize_repos(self):
        """
        Initializes the different repos
        """
        self.message_repo_instance = MessageRepository()
        self.customer_device_repo_instance = CustomerDeviceRepository()
        self.social_repo_instance = CustomerSocialAccRepository()
        self.customer_onboarding_info_repo_instance = CustomerOnboardingInfoRepository()
        self.share_offer_repo_instance = ShareOfferRepository()
        self.changed_repositories()

    def changed_variables(self):
        self.messages_locale = CommonHelpers.get_locale_for_messaging(self.request_args.get('language'))

    def setting_language_and_variables(self):
        """
        Set the locale for user message
        """
        self.session_id = 0
        self.code = 11
        self.message = ""
        self.customer = None
        self.customer_id = None
        self.customer_data = None
        self.session = None
        self.password_update_required = False
        self.changed_variables()
        self.master_node = False
        if self.is_sign_in_from_sign_up:
            self.master_node = True

    def setting_device_id(self):
        """
        Sets the device id
        """
        if self.device_key:
            self.device_id = self.device_key

    def checking_device_os(self):
        if self.device_os.lower() == "wp":
            self.send_response_flag = True
            self.status_code = 422
            self.response = {
                "message": self.message_repo_instance.end_of_life_message_for_windows_app_user,
                "success": False,
                "code": 70
            }
            return self.send_response(self.response, self.status_code)

    def social_user_having_email_and_password(self):
        """
        Checks that If user is connected and have email and the password
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

    def check_black_listed_user(self):
        """
        Checking the black listed user and device
        """
        if self.customer['status'] == self.customer_repo_instance.STATUS_BLACKLISTED:
            self.status_code = 422
            self.send_response_flag = True
            self.response = {
                "message": self.message_repo_instance.user_blacklisted,
                "code": 70,
                "success": False
            }
            return self.send_response(self.response, self.status_code)

    def check_device_black_listed(self):
        """
        Checking the blacklisted device
        """
        if self.customer_device_repo_instance.is_device_linked_to_blacklisted_user(
                self.device_id, master=self.master_node
        ):
            self.status_code = 422
            self.send_response_flag = True
            self.response = {
                "message": self.message_repo_instance.device_blacklisted,
                "code": 70,
                "success": False
            }
            return self.send_response(self.response, self.status_code)

    def set_customer_profile(self):
        """
        Setting the customer profile
        """
        self.customer_id = self.customer['id']
        self.customer_profile = self.customer_repo_instance.load_customer_profile_by_user_id(self.customer_id)  # noqa
        self.customer_profile = self.customer_repo_instance.\
            put_customer_in_trial_membership_if_qualifies(self.customer_id, self.customer_profile)

    def update_customer_trial_date(self):
        """
        update customer trial date.

        moved this function from middleware token to login to reduce call on each call
        """
        try:
            is_member_on_trail = all([
                self.customer_profile.get('new_member_group') == self.customer_repo_instance.MEMBERSTATUS_ONBOARDING,
                self.customer_profile.get('onboarding_status') == 1,
                self.customer_profile.get('onboarding_redemptions_count', 0) < self.customer_repo_instance.TRAIL_REDEMPTIONS_LIMIT  # noqa: E501
            ])
            if not is_member_on_trail and self.customer_profile.get('new_member_group') not in [
                self.customer_repo_instance.MEMBERSTATUS_MEMBER, self.customer_repo_instance.MEMBERSTATUS_REPROSPECT
            ]:
                self.customer_profile.update(self.customer_repo_instance.update_trial_date(customer_id=self.customer_id))
        except Exception:
            self.logger.exception('passing error ocurred on update of customer update_trial_date')

    def setting_customer_data_and_token(self):
        """
        Setting the customer data and the sessions for current user
        """
        self.customer_data = self.customer_repo_instance.get_customer_session_data(
            self.customer_id,
            self.customer_profile
        )
        api_version = self.session_repo_instance.get_api_version(request)
        self.session_id = self.session_repo_instance.generate_session(
            self.customer_id,
            self.customer_data,
            self.app_version,
            company=api_version,
            last_row=True
        )
        self.customer_profile = self.customer_repo_instance.refresh_customer_sessions(
            self.customer_id,
            self.customer_profile
        )
        if self.session_id and not self.session:
            self.session = self.session_repo_instance.find_by_id(self.session_id, master=True)
        self.update_customer_trial_date()
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
            if devices_num >= self.customer_repo_instance.ALLOWED_NUMBER_OF_DEVICES:
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

    def update_share_offers_of_customer(self):
        """
        Updates the customer share offers data
        """
        self.share_offer_repo_instance.update_customer_id_shared_offer(self.email, self.customer_id)

    def finishing_onboarding(self):
        """
        Finishes the customer onboarding
        """
        add_new_record = True
        is_primary = False

        if self.device_key:
            on_boarding_device_info = self.customer_onboarding_info_repo_instance.get_onboarding_info_by_key(
                self.device_key
            )
            if on_boarding_device_info:
                for on_boarding_device in on_boarding_device_info:
                    if on_boarding_device['customer_id'] == int(self.customer_id):
                        is_primary = bool(on_boarding_device['is_primary'])
                        add_new_record = False
            else:
                is_primary = True

            if add_new_record:
                is_primary = 1 if not on_boarding_device_info else 0
                self.customer_onboarding_info_repo_instance.insert_customer_onboarding_info(
                    self.customer_id,
                    self.device_os,
                    self.device_key,
                    is_primary
                )
            if not is_primary and self.customer_profile['member_group'] == CustomerProfile.MEMBERSTATUS_ONBOARDING:
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
            'is_demographics_updated': self.customer_repo_instance.is_demographics_updated(self.customer['id']),
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
        self.setting_device_id()
        self.setting_language_and_variables()
        self.initialize_repos()

        self.checking_device_os()
        if self.is_send_response_flag_on():
            return

        self.social_user_having_email_and_password()
        if self.is_send_response_flag_on():
            return

        self.loading_customer()
        if self.is_send_response_flag_on():
            return

        self.check_black_listed_user()
        if self.is_send_response_flag_on():
            return

        self.check_device_black_listed()
        if self.is_send_response_flag_on():
            return

        self.set_customer_profile()
        set_customer_and_device_id(self.customer_id, self.device_key)
        self.setting_customer_data_and_token()
        self.device_info_of_user()
        if self.is_send_response_flag_on():
            return

        thread = threading.Thread(target=self.credit_smiles(), args=())
        thread.daemon = True
        thread.start()
        self.finishing_onboarding()
        self.update_share_offers_of_customer()
        self.generating_final_response()
