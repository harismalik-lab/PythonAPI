"""
Merchant endpoints for Rewards api
"""

from requests import codes

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.common_helpers import CommonHelpers, OfferManager, get_formated_date
from repositories.customer_repo import CustomerProfile
from repositories.exchange_rates_repo import ExchangeRatesRepository
from repositories.merchant_repo import MerchantRepository
from repositories.offer_repo import OfferRepository
from repositories.offer_slice_active_repo import OfferSliceActiveRepository
from repositories.outlet_repo import OutletRepository
from repositories.translation_repo import MessageRepository
from rewards_api.vc01.merchants_api.validation import rewards_merchant_parser
from rewards_api.vc01.merchants_api.validation_merchant_name import merchant_name_parser
from user_authentication.authentication import get_current_customer


class RewardsMerchantApi(BaseGetResource):
    """
    This class contains endpoint for get merchant by id
    """
    __author__ = 'Saqib'

    required_token = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='merchants_api/merchants_api.log',
        ),
        'name': 'merchants_api'
    }
    request_parser = rewards_merchant_parser
    connections_names = ['default', 'consolidation']

    def populate_request_arguments(self):
        self.redeemability = self.request_args.get('redeemability')
        self.locale = self.request_args.get('language')
        self.currency = self.request_args.get('currency')
        self.location_id = self.request_args.get('location_id')
        self.lattitude = self.request_args.get('lat')
        self.longitude = self.request_args.get('lng')

    def initialize_repos(self):
        """
        This method initializes repository instances
        """
        self.customer_repo = CustomerProfile(logger=self.logger)
        self.message_repo = MessageRepository()
        self.currency_converter = ExchangeRatesRepository()
        self.merchant_repo = MerchantRepository()
        self.outlet_repo = OutletRepository()
        self.offer_repo = OfferSliceActiveRepository()

    def parse_api_params(self):
        self.locale = CommonHelpers.get_locale(self.locale, self.location_id)
        # Latitude & Longitude are used for sorting Outlets by proximity
        self.lat_long = "{},{}".format(self.lattitude, self.longitude)
        self.message_locale = CommonHelpers.get_locale_for_messaging(self.locale)

    def load_customer(self):
        self.customer = get_current_customer() or {}

    def initialze_local_variables(self):
        self.is_user_onboard = False
        self.customer_id = self.customer.get('customer_id')
        self.customer_info = {}
        self.outlets_filtered = []
        self.shared_offers_send = []

    def load_products(self):
        if self.customer:
            self.customer['purchased_skus'] = self.customer_repo.get_customer_products_vc01(self.customer_id)

    def get_merchant(self, *args, **kwargs):
        self.merchant = self.merchant_repo.find_by_id_vc01(
            kwargs['merchant_id'],
            self.locale,
            self.customer.get('purchased_skus', [])
        )
        if not self.merchant:
            message = self.message_repo.get_message_by_code(
                self.message_repo.merchant_details_not_found,
                self.locale
            )
            self.status_code = codes.unprocessable_entity
            self.response = {'success': False, 'code': 70, 'message': message}
            self.send_response_flag = True

    def get_merchant_attributes(self, **kwargs):
        # Get merchant attributes
        self.merchant['is_tutorial'] = self.merchant['is_tutorial'] > 0
        self.merchant_attributes = self.merchant_repo.get_merchant_attributes_by_merchant_id(
            kwargs['merchant_id'],
            self.merchant['category'],
            self.message_locale
        )
        self.merchant['merchant_attributes'] = self.merchant_attributes

    def get_active_outlets(self, **kwargs):
        # Grab Active Outlets for this Merchant
        self.outlets, self.outlet_ids = self.outlet_repo.find_by_merchant(
            merchant_id=kwargs['merchant_id'],
            latlong=self.lat_long,
            locale=self.locale,
            return_ids=True
        )

    def load_customer_object(self):
        logged_in_customer = get_current_customer()
        self.customer_info['member_type'] = 0
        self.customer_info['user_id'] = 0
        if logged_in_customer:
            # Load the Customer Object
            user_info = self.customer_repo.load_customer_profile_by_user_id(self.customer['customer_id'])
            self.customer_info["user_id"] = self.customer_id
            self.customer_info["member_type"] = user_info['new_member_group']
            self.customer_info["membership_expiration_date"] = str(user_info['membership_expiry'])
            self.customer_info["using_trial"] = user_info['is_using_trial']
            self.customer_info["onboarding_redemptions_count"] = 0
            self.customer_info["max_number_allowed_shares"] = 0
            self.customer_info["total_shares"] = len(self.shared_offers_send)
            self.customer_info["is_phone_verified"] = user_info.get('is_phone_verified')
            self.customer_info["verification_state"] = user_info.get('verification_state')
            self.customer_info['is_demographics_updated'] = int(
                bool(
                    user_info['gender'] and
                    user_info['nationality'] and
                    user_info['birthdate']
                )
            )

    def get_all_active_offers(self):
        # Get the array of all active offers against this merchant
        self.offers, self.outlet_ids_having_offers = \
            self.offer_repo.find_by_outlets_vc01(
                outlet_ids=self.outlet_ids,
                locale=self.locale,
                customer=self.customer,
                return_outlet_ids=True
            )

    def get_outlets_present_in_offer_list(self):
        for outlet in self.outlets:
            outlet['tripadvisor_id'] = int(outlet['tripadvisor_id'])
            if outlet['id'] in self.outlet_ids_having_offers:
                self.outlets_filtered.append(outlet)

    def set_offer_currency(self, offer):
        if self.currency.lower() == offer['local_currency'].lower() and \
                offer.get('savings_estimate_local_currency'):
            offer['savings_estimate'] = offer['savings_estimate_local_currency']
        else:
            offer['savings_estimate'] = self.currency_converter.get_conversion_rate(
                offer['savings_estimate'],
                'AED',
                self.currency
            )

    def process_offers(self):
        for offer in self.offers:
            shared_send_count = 0
            shared_receive_count = 0
            offer['shared_send_count'] = shared_send_count
            offer['shared_receive_count'] = shared_receive_count
            offer['shared_redemptions_count'] = 0
            offer['is_bundled_for_location'] = 0
            offer['times_bundled'] = 0
            offer['original_quantity'] = offer['quantity']
            offer['quantity'] = offer['quantity_purchased']
            offer['savings_estimate_aed'] = offer['savings_estimate']
            if (
                self.currency.lower() == offer['local_currency'].lower() and
                offer['savings_estimate_local_currency'] and
                offer['savings_estimate_local_currency'] > 0
            ):
                offer['savings_estimate'] = offer['savings_estimate_local_currency']
            else:
                offer['savings_estimate'] = self.currency_converter.get_conversion_rate(
                    offer['savings_estimate'],
                    'AED',
                    self.currency
                )

            offer['offer_detail'] = offer['details']
            offer['voucher_details'] = []
            offer['voucher_rules_of_use'] = []
            if not offer.get('voucher_type'):
                offer['voucher_type'] = 1
            offer['message'] = OfferManager().get_message_for_offer_type(
                self.locale, offer.get('voucher_type'), offer['spend'], offer['reward'], offer['percentage_off']
            )

            offer['voucher_type'] = offer.get('voucher_type', 1)

            if offer['voucher_type']:
                voucher_type_details = OfferManager().get_voucher_type_details(
                    offer['voucher_type'],
                    offer['category'],
                    self.locale,
                    False
                )

                if voucher_type_details:
                    voucher_type_details['title'] = offer['message']
                    offer['voucher_details'].append(voucher_type_details)

            if offer.get('voucher_restriction1') and offer.get('voucher_restriction1') > 0:
                voucher_restriction1_details = OfferManager().get_voucher_restriction_details(
                    offer['voucher_restriction1'],
                    offer['category'],
                    self.locale
                )
                if voucher_restriction1_details:
                    offer['voucher_details'].append(voucher_restriction1_details)

            if offer.get('voucher_restriction2') and offer['voucher_restriction2'] > 0:
                voucher_restriction2_details = OfferManager().get_voucher_restriction_details(
                    offer['voucher_restriction2'],
                    offer['category'],
                    self.locale
                )
                if voucher_restriction2_details:
                    offer['voucher_details'].append(voucher_restriction2_details)

            if offer.get("voucher_restrictions"):
                offer['voucher_rules_of_use'].append(offer["voucher_restrictions"])

            #  quantity to display in mobile apps
            if offer['type'] == OfferRepository.TYPE_MEMBER:
                offer['quantity_display'] = offer['original_quantity']
            else:
                if offer.get('is_purchased'):
                    offer['quantity_display'] = offer['quantity_purchased']
                else:
                    offer['quantity_display'] = offer['original_quantity']

            manipulated_skus = []
            for sku in offer['product_sku']:
                if sku[0].upper() == "L" or sku[0].upper() == "C":
                    manipulated_skus.append("D{}".format(sku))
                else:
                    manipulated_skus.append(sku)

            offer['product_sku'] = manipulated_skus
            offer['valid_from_date'] = get_formated_date(offer['valid_from_date'])
            offer['expiration_date'] = get_formated_date(offer['expiration_date'])

    def prepare_merchant_object(self):
        self.merchant['outlets'] = self.outlets_filtered
        self.merchant['offers'] = self.offers
        self.merchant['customer'] = self.customer_info

    def prepare_response(self):
        self.response = {
            'success': True,
            'message': 'success',
            'data': self.merchant,
            'code': 0
        }
        self.send_response_flag = True
        self.status_code = codes.OK

    def process_request(self, *args, **kwargs):
        self.initialize_repos()
        self.parse_api_params()
        self.load_customer()
        self.initialze_local_variables()
        self.load_products()
        self.get_merchant(*args, **kwargs)
        if self.is_send_response_flag_on():
            return

        self.get_merchant_attributes(**kwargs)
        self.get_active_outlets(**kwargs)
        self.get_all_active_offers()
        self.get_outlets_present_in_offer_list()
        self.load_customer_object()
        self.process_offers()
        self.prepare_merchant_object()
        self.prepare_response()


class RewardsMerchantNameApi(BaseGetResource):
    """
    This class contains get_merchant_name endpoint
    """
    __author__ = 'Arslan'

    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='merchants_api/rewards_merchants_api.log',
        ),
        'name': 'rewards_merchants_api'
    }
    request_parser = merchant_name_parser
    connections_names = ['default', 'consolidation']

    def populate_request_arguments(self):
        self.merchant_id = self.request_args.get('merchant_id')
        self.offer_id = self.request_args.get('offer_id')
        self.language = self.request_args.get('language ')

    def initialize_repos(self):
        """
        This method initializes repositories instances
        """
        self.offer_slice_active = OfferSliceActiveRepository()
        self.merchants_repo_instance = MerchantRepository()

    def validate_params(self):
        if not self.merchant_id and not self.offer_id:
            self.status_code = codes.INTERNAL_SERVER_ERROR
            self.set_response({'message': 'No result was found'}, codes.INTERNAL_SERVER_ERROR)

    def get_merchant_and_offer_names(self):
        self.merchant_name = self.merchants_repo_instance.find_name_by_id(self.merchant_id)
        self.offer_name = self.offer_slice_active.find_name_by_id(self.offer_id)

    def prepare_response(self):
        self.response = {
            'data': {
                'merchant_name': self.merchant_name.get('name'),
                'offer_name': self.offer_name.get('name')
            },
            'success': True,
            'message': 'success'
        }
        self.status_code = codes.OK

    def process_request(self, *args, **kwargs):
        self.populate_request_arguments()
        self.initialize_repos()
        self.validate_params()
        if self.is_send_response_flag_on():
            return
        self.get_merchant_and_offer_names()
        self.prepare_response()
        self.set_response(self.response, codes.OK)
