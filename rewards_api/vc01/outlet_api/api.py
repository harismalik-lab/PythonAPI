from flask import current_app

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BaseGetResource
from common.common_helpers import CommonHelpers, multi_key_sort
from common.db import CONSOLIDATION, DEFAULT
from repositories.customer_repo import CustomerProfile
from repositories.merchant_repo import MerchantRepository
from repositories.offer_slice_active_repo import OfferSliceActiveRepository
from repositories.outlet_repo import OutletRepository
from repositories.product_ent_active_repo import ProductEntActiveRepository
from repositories.redemption_ent_active_repo import \
    RedemptionEntActiveRepository
from repositories.share_offer_repo import ShareOfferRepository
from repositories.top_up_offer_repo import TopUpOffersRepository
from user_authentication.authentication import get_current_customer

from .validation import outlet_parser


class OutletApi(BaseGetResource):
    backup_request_args_for_exception = False
    request_parser = outlet_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='outlet_api/rewards_outlet_api.log',
        ),
        'name': 'rewards_outlet_api'
    }
    logger = None
    status_code = 200
    required_token = True
    connections_names = [DEFAULT, CONSOLIDATION]

    def is_search_string_found(self, search_in, search_string, is_search_words=False):
        search_string = search_string.strip()
        if not is_search_words:
            return CommonHelpers.is_string_exist(search_in, search_string)
        else:
            search_words = search_string.split(' ')
            for word in search_words:
                trimmed_word = word.strip()
                if trimmed_word and not CommonHelpers.is_string_exist(search_in, trimmed_word):
                    return False
        return True

    def populate_request_arguments(self):
        self.offer_redeemability = self.request_args.get('redeemability').lower().strip()
        self.filter_by_type = self.request_args.get('filter_by_type')
        self.query_type = self.request_args.get('query_type')
        self.query = self.request_args.get('query').lower().strip()
        self.outlet_id = self.request_args.get('outlet_id')
        self.product_sku = self.request_args.get('product_sku')
        self.location_id = self.request_args.get('location_id')
        self.locale = self.request_args.get('language')
        self.offset = self.request_args.get('offset')
        self.billing_country = self.request_args.get('billing_country')
        self.include_featured = self.request_args.get('include_featured')
        self.user_id = self.request_args.get('user_id')
        self.category = self.request_args.get('category')
        self.sub_category_filter = self.request_args.get('sub_category_filter')
        self.cuisine_filter = self.request_args.get('cuisine_filter[]')
        self.filters_selected_for_yes = self.request_args.get('filters_selected_for_yes[]')
        self.filters_selected_for_no = self.request_args.get('filters_selected_for_no[]')
        self.fuzzy = self.request_args.get('fuzzy')
        self.platform = self.request_args.get('__platform')
        self.lat = self.request_args.get('lat')
        self.lng = self.request_args.get('lng')
        self.radius = self.request_args.get('radius')
        self.cuisine = self.request_args.get('cuisine')
        self.sort = self.request_args.get('sort')
        self.neighborhood = self.request_args.get('neighborhood')
        self.mall = self.request_args.get('mall')
        self.hotel = self.request_args.get('hotel')
        self.redeemability_first = self.request_args.get('first_sort_by_redeemability')

    def initialize_class_attributes(self):
        self.disable_fuzzy = False
        self.locale = CommonHelpers.get_locale(self.locale, self.location_id)
        self.outlet_ids = []
        self.top_up_offers = []
        self._fuzzy_search_outlet_ids = []
        self._fuzzy_search_outlet_id_score = []
        self.is_fuzzy_server_down = False
        self.__fuzzy_host = current_app.config['ELASTIC_SEARCH_URL']
        self.limit = CustomerProfile.MAX_OUTLETS
        # get th digital reach featured category
        self.featured_category = ""
        self.featured_merchants = []
        self.is_load_featured_merchants = False
        self.is_customer_own_cheers_for_location = False
        self.search_results = []
        self.final_outlets = []
        self.shared_offers_receive = []
        self.shared_offers_sent = []
        self.shared_offers_received = False
        self.redemptions_quantities = {}
        self.redemptions_quantities_present = False
        self.merchants_ids = []
        self.filtered_outlets = []
        self.offer_redeemability_check = False
        self.isshared = False
        self.tabs = []

    def initialize_repos(self):
        self.customer_profile_class_instance = CustomerProfile(logger=self.logger)
        self.product_ent_class_instance = ProductEntActiveRepository()
        self.redemption_class_instance = RedemptionEntActiveRepository()
        self.offer_ent_class_instance = OfferSliceActiveRepository()
        self.outlet_class_instance = OutletRepository()
        self.merchant_class_instance = MerchantRepository()
        self.top_up_offers_class_instance = TopUpOffersRepository()
        self.shared_class_instance = ShareOfferRepository()

    def load_customer_profile_and_session_data(self):
        """
        Load the customer-profile and customer session_data
        """
        self.is_user_onboard = False
        if self.user_id:
            self.customer_profile = self.customer_profile_class_instance.load_customer_profile_by_user_id(self.user_id)
        else:
            self.customer_profile = {}
        self.customer = get_current_customer()

        if self.customer:
            self.customer_id = self.customer.get('customer_id')
            self.customer['purchased_skus'] = self.customer_profile_class_instance.get_customer_products_vc01(
                self.customer_id
            )
        else:
            self.customer_id = 0
            self.is_user_onboard = False

    def set_empty_response(self):
        self.send_response_flag = True
        self.response = {
            'success': True,
            'message': 'success',
            'data': {
                'search_results': [],
                'featured_merchants': [],
                'outlets': []
            }
        }

    def set_is_customer_own_cheers_for_location(self):
        """
        Set is_customer_own_cheers_for_location flag.
        :return:
        """
        self.is_customer_own_cheers_for_location = self.customer_profile_class_instance. \
            is_customer_own_cheers_for_location(
                purchased_skus=self.customer.get('purchased_skus', []),
                location_id=self.location_id
            )

    def initialize_data_offers(self):
        """
        Set offers data to find offers.
        """
        self.data_offers = dict()
        self.data_offers['isshared'] = self.isshared
        self.data_offers['locale'] = self.locale
        self.data_offers['customer'] = self.customer
        self.data_offers['offer_redeemability'] = self.offer_redeemability
        self.data_offers['product_sku'] = self.product_sku
        self.data_offers['outlet_id'] = self.outlet_id
        self.data_offers['category'] = self.category
        self.data_offers['category_lower_case'] = self.category.lower()
        self.data_offers['location_id'] = self.location_id
        self.data_offers['filter_by_type'] = self.filter_by_type

    def get_offers_from_db(self):
        """
        Get offers from db.
        """
        self.initialize_data_offers()
        self.offers = self.offer_ent_class_instance.find_offers(self.data_offers)

    def get_redemptions_quantities(self):
        """
        Set redemptions quantities.
        """
        if self.customer:
            self.redemptions_quantities = self.redemption_class_instance.get_redeemed_quantities_for_customer_vc01(
                self.customer_id
            )
            self.redemptions_quantities_present = True if len(self.redemptions_quantities) > 0 else False

    def set_offer_related_defaults(self):
        """
        Set offer-related defaults.
        """
        self.outlet_offer_info = {}
        self.query_matched_offers_outlets = []
        self.shared_offer_ids = []
        self.offer_ids_for_customer_redemptions = []
        self.shared_redemptions_count_records = {}
        self.customer_redemptions_records = {}

    def update_query_matched_offers_outlets(self, offer={}):
        """
        Update query_matched_offers_outlets based on fuzzy_search.
        """
        if self.query_type_is_name:
            if self.is_search_string_found(offer.get('offer_name'), self.query, True):
                try:
                    self.query_matched_offers_outlets += map(int, offer.get('outlet_ids').split(','))
                except AttributeError:
                    self.query_matched_offers_outlets.append(int(offer.get('outlet_ids')))

    def initialize_offer_attributes(self):
        """
        Initialize offer_attributes.
        """
        for offer in self.offers:
            offer['expiration_date'] = self.offer_ent_class_instance._fix_expiration_date(
                offer['expiration_date']
            )  # fix offer expiry
            try:
                self.outlet_ids += offer['outlet_ids'].split(',')
            except AttributeError:
                self.outlet_ids.append(str(offer['outlet_ids']))
            self.update_query_matched_offers_outlets(offer=offer)

            if self.customer:
                offer['isshared'] = False
                self.shared_offer_ids.append(offer['id'])
                self.offer_ids_for_customer_redemptions.append(offer['id'])

    def set_customer_redemptions_records(self):
        """
        Set customer_redemptions_records.
        """
        if not self.redemptions_quantities_present:
            self.customer_redemptions_records = self.offer_ent_class_instance.count_offer_redemptions_by_customer_vc01(
                self.customer_id, offer_id=self.offer_ids_for_customer_redemptions, group_by=True
            )

    def set_customer_redemptions(self):
        """
        Set customer-redemptions records it will be used in redeemability calculations.
        """
        if self.customer:
            self.set_customer_redemptions_records()

    def calculate_outlet_attributes_with_offer_for_customer(self, redeemability={}, offer={}, outlet_id=0):
        """
        Set outlet attributes when customer exists.
        """
        # set is_redeemable for the outlet
        try:
            is_redeemable = redeemability['redeemability'] in [
                self.offer_ent_class_instance.REDEEMABLE,
                self.offer_ent_class_instance.REUSABLE
            ]
            if self.outlet_offer_info[outlet_id]['is_redeemable'] < is_redeemable:
                self.outlet_offer_info[outlet_id]['is_redeemable'] = is_redeemable
        except KeyError:
            self.outlet_offer_info[outlet_id] = {}
            self.outlet_offer_info[outlet_id]['is_redeemable'] = is_redeemable

        # set top_offer_redeemability for the outlet
        try:
            if self.outlet_offer_info[outlet_id]['top_offer_redeemability'] < redeemability['redeemability']:
                self.outlet_offer_info[outlet_id]['top_offer_redeemability'] = redeemability['redeemability']
        except KeyError:
            self.outlet_offer_info[outlet_id]['top_offer_redeemability'] = redeemability['redeemability']

        # set top_offer_type for the outlet
        try:
            if self.outlet_offer_info[outlet_id]['top_offer_type'] < offer['type']:
                self.outlet_offer_info[outlet_id]['top_offer_type'] = offer['type']
        except KeyError:
            self.outlet_offer_info[outlet_id]['top_offer_type'] = offer['type']

        # set is_purchased for the outlet
        try:
            if self.outlet_offer_info[outlet_id]['is_purchased'] < offer['is_purchased']:
                self.outlet_offer_info[outlet_id]['is_purchased'] = offer['is_purchased']
        except KeyError:
            self.outlet_offer_info[outlet_id]['is_purchased'] = offer['is_purchased']

        # set is_shared for the outlet
        try:
            if self.outlet_offer_info[outlet_id]['is_shared'] < offer['isshared']:
                self.outlet_offer_info[outlet_id]['is_shared'] = offer['isshared']
        except KeyError:
            self.outlet_offer_info[outlet_id]['is_shared'] = offer['isshared']

    def calculate_outlet_attributes_with_offer(self, offer={}, outlet_id=0):
        """
        Set outlet attributes for skip-mode.
        """
        # set is_redeemable for the outlet
        try:
            self.outlet_offer_info[outlet_id]['is_redeemable'] = False
        except KeyError:
            self.outlet_offer_info[outlet_id] = {}
            self.outlet_offer_info[outlet_id]['is_redeemable'] = False

        # set top_offer_redeemability for the outlet
        self.outlet_offer_info[outlet_id]['top_offer_redeemability'] = self.offer_ent_class_instance.NOT_REDEEMABLE

        # set top_offer_type for the outlet
        self.outlet_offer_info[outlet_id]['top_offer_type'] = offer['type']

        # set is_purchased for the outlet
        self.outlet_offer_info[outlet_id]['is_purchased'] = bool(0)

        # set is_shared for the outlet
        self.outlet_offer_info[outlet_id]['is_shared'] = 0

        # set top_up_offer for the outlet
        self.outlet_offer_info[outlet_id]['top_up_offer'] = 0

    def set_outlet_common_attributes_with_offer(self, offer={}, outlet_id=0):
        # set top_offer_type for the outlet
        try:
            if self.outlet_offer_info[outlet_id]['top_offer_type'] < offer['type']:
                self.outlet_offer_info[outlet_id]['top_offer_type'] = offer['type']
        except KeyError:
            self.outlet_offer_info[outlet_id]['top_offer_type'] = offer['type']

    def update_offer_attributes(self):
        """
        Update different offer-attributes.
        """
        for offer in self.offers:
            if self.customer:
                redeemability = self.offer_ent_class_instance.calculate_offer_redeemability_for_customer_vc01(
                    offer=offer,
                    customer=self.customer,
                    redemptions_quantities=self.redemptions_quantities,
                    offer_redeemability=self.offer_redeemability,
                    customer_redemptions_records=self.customer_redemptions_records,
                    outlets=True
                )
                offer['redeemability'] = redeemability['redeemability']
                offer['times_redeemed'] = redeemability['times_redeemed']
                offer['is_purchased'] = redeemability.get('is_purchased', False)

            try:
                outlet_ids = map(int, filter(None, offer.get('outlet_ids').split(',')))
            except AttributeError:
                outlet_ids = [offer['outlet_ids']]

            for outlet_id in outlet_ids:
                if self.customer:
                    self.calculate_outlet_attributes_with_offer_for_customer(
                        redeemability=redeemability,
                        offer=offer,
                        outlet_id=outlet_id
                    )
                else:
                    self.calculate_outlet_attributes_with_offer(offer=offer, outlet_id=outlet_id)
                self.set_outlet_common_attributes_with_offer(offer=offer, outlet_id=outlet_id)

    def update_outlets(self):
        """
        Update outlet-data.
        """
        self.outlet_ids = list(set(list(filter(None, self.outlet_ids))))  # remove empty elements and duplicates
        self.merchant_criteria = {
            'lat': self.lat,
            'lng': self.lng,
            'radius': self.radius,
            'category': self.category,
            'cuisine': self.cuisine,
            'sort': self.sort,
            'query': self.query,
            'query_type': self.query_type,
            'neighborhood': self.neighborhood,
            'mall': self.mall,
            'hotel': self.hotel,
            'billing_country': self.billing_country,
            'outlet_ids': self.outlet_ids,
            'sub_category_filter': self.sub_category_filter,
            'cuisine_filter': self.cuisine_filter,
            'filters_selected_for_yes': self.filters_selected_for_yes,
            'filters_selected_for_no': self.filters_selected_for_no
        }
        self.outlets = self.outlet_class_instance.find_by_criteria_merchant_attributes_vc01(
            merchant_criteria=self.merchant_criteria, locale=self.locale
        )
        self.outlet_ids = []
        self.offers = []

    def calculate_top_offer_redeemability(self, outlet={}):
        """
        Calculate top_offer_redeemability of offer.
        """
        if self.offer_redeemability == self.offer_ent_class_instance.Redeemability_not_redeemable:
            outlet_offer_info = self.outlet_offer_info[outlet['id']]
            if outlet_offer_info['top_offer_redeemability'] == self.offer_ent_class_instance.NOT_REDEEMABLE:
                self.outlet_offer_info[outlet['id']]['top_offer_redeemability'] = self.offer_ent_class_instance.NOT_REDEEMABLE

    def update_outlet_attributes_and_final_outlets(self, outlet={}, outlet_offer_info={}):
        if not outlet_offer_info:
            outlet_offer_info = self.outlet_offer_info[outlet['id']]

        outlet['is_redeemable'] = outlet_offer_info['is_redeemable']
        outlet['top_offer_type'] = outlet_offer_info['top_offer_type']
        outlet['top_offer_redeemability'] = outlet_offer_info['top_offer_redeemability']
        outlet['is_purchased'] = bool(outlet_offer_info['is_purchased'])
        outlet['is_shared'] = outlet_offer_info['is_shared']
        outlet['is_more_sa'] = 0

        self.final_outlets.append(outlet)

    def process_outlets_if_no_customer(self):
        """
        Process outlets in-case if customer is not available..
        """
        for outlet in self.outlets:
            if self.filter_outlet_by_query(outlet=outlet):
                continue
            outlet_offer_info = self.outlet_offer_info[outlet['id']]
            outlet_offer_info['top_offer_redeemability'] = 0
            self.update_outlet_attributes_and_final_outlets(outlet=outlet, outlet_offer_info=outlet_offer_info)

    def filter_outlet_by_query(self, outlet={}):
        """
        Filter outlet based on merchant_name using query.
        :param outlet: outlet instance
        :return: bool
        """
        if self.query_type_is_name:
            if not self.is_search_string_found(outlet.get('merchant_name'), self.query, True) \
                    and outlet.get('id') not in self.query_matched_offers_outlets:
                return True
        return False

    def process_outlets_if_customer(self):
        """
        Process outlet when customer is available..
        """
        for outlet in self.outlets:

            self.calculate_top_offer_redeemability(outlet=outlet)
            outlet_offer_info = self.outlet_offer_info[outlet['id']]
            # There are no "Active" Offers of any sort for this Outlet
            # It should never show up in the response
            if outlet_offer_info['top_offer_redeemability'] in [None, -1]:
                continue

            if self.filter_outlet_by_query(outlet):
                continue

            # The redeemability filter is only valid for logged in customers
            # If the top Offer's redeemability doesn't match the filter, we discard the Outlet
            if self.offer_redeemability != self.offer_ent_class_instance.Redeemability_all:
                if self.offer_redeemability == self.offer_ent_class_instance.Redeemability_redeemable_reusable:
                    if outlet_offer_info['top_offer_redeemability'] not in [
                        self.offer_ent_class_instance.REDEEMABLE,
                        self.offer_ent_class_instance.REUSABLE
                    ]:
                        continue
                if self.offer_redeemability == self.offer_ent_class_instance.Redeemability_reusable \
                        and outlet_offer_info['top_offer_redeemability'] != self.offer_ent_class_instance.REUSABLE:
                    continue
                if self.offer_redeemability == self.offer_ent_class_instance.Redeemability_not_redeemable \
                        and outlet_offer_info['top_offer_redeemability'] != self.offer_ent_class_instance.NOT_REDEEMABLE:
                    continue
                if self.offer_redeemability == self.offer_ent_class_instance.Redeemability_redeemable \
                        and outlet_offer_info['top_offer_redeemability'] != self.offer_ent_class_instance.REDEEMABLE:
                    continue
                if self.offer_redeemability == self.offer_ent_class_instance.Redeemability_redeemed \
                        and outlet_offer_info['top_offer_redeemability'] != self.offer_ent_class_instance.REDEEMED:
                    continue
            self.update_outlet_attributes_and_final_outlets(outlet=outlet, outlet_offer_info=outlet_offer_info)

    def set_query_type_is_name(self):
        """
        Set query_type_is_name on when query_type is name.
        """
        self.query_type_is_name = False
        if self.query and self.query_type == 'name':
            self.query_type_is_name = True

    def process_outlets(self):
        """
        Process outlets.
        """
        if self.customer:
            self.process_outlets_if_customer()
        else:
            self.process_outlets_if_no_customer()

    def default_sort_final_outlets(self):
        """
        Finale-outlets default sort.
        """
        if self.redeemability_first:
            self.final_outlets = multi_key_sort(
                self.final_outlets,
                ['-top_offer_redeemability', 'distance', 'merchant_name']
            )
        else:
            self.final_outlets = multi_key_sort(
                self.final_outlets,
                ['distance', 'merchant_name', '-top_offer_redeemability']
            )

    def aplha_sort_final_outlets(self):
        """
        Finale-outlets alpha sort.
        """
        if self.redeemability_first:
            self.final_outlets = multi_key_sort(
                self.final_outlets,
                ['-top_offer_redeemability', 'merchant_name']
            )
        else:
            self.final_outlets = multi_key_sort(
                self.final_outlets,
                ['merchant_name', '-top_offer_redeemability']
            )

    def final_outlets_sort(self):
        """
        Sort the final outlets based on sort param.
        """
        self.sort_type = self.sort
        if self.sort_type == 'default':
            self.default_sort_final_outlets()
        elif self.sort_type == 'alpha':
            self.aplha_sort_final_outlets()

    def process_final_outlets(self):
        """
        Sort Final outlets
        """
        self.final_outlets_sort()

    def update_search_results_neighborhoods(self):
        """
        Update the search results with country areas.
        """
        if self.query:
            self.neighborhoods = self.outlet_class_instance.get_country_areas_vc01(
                location_id=self.location_id,
                locale=self.locale,
                search_keyword=self.query,
                category=self.category,
                product_sku=self.customer.get('purchased_skus', [])
            )
            for neighborhood in self.neighborhoods:
                self.search_results.append({
                    'type': 'neighborhood',
                    'name': neighborhood['name'],
                    'value': neighborhood['value'],
                    'icon': 'https://s3-us-west-2.amazonaws.com/ent-search-results/neighbourhood.png'
                })

    def update_search_results_hotel_and_malls(self):
        """
        Update the search results with country hotels and malls.
        """
        if self.category.lower() != 'travel':
            if self.query:
                self.hotels = self.outlet_class_instance.get_country_hotels_vc01(
                    locale=self.locale,
                    search_keyword=self.query,
                    product_sku=self.customer.get('purchased_skus', [])
                )
                for hotel in self.hotels:
                    self.search_results.append({
                        'type': 'hotel',
                        'name': hotel['name'],
                        'value': hotel['value'],
                        'icon': 'https://s3-us-west-2.amazonaws.com/ent-search-results/hotel.png'
                    })

                self.malls_list = self.outlet_class_instance.get_attribute_values_vc01(
                    'mall',
                    location_id=self.location_id,
                    locale=self.locale,
                    search_keyword=self.query,
                    category=self.category,
                    product_sku=self.customer.get('purchased_skus', [])
                )
                for mall in self.malls_list:
                    self.search_results.append({
                        'type': 'mall',
                        'name': mall,
                        'value': mall,
                        'icon': 'https://s3-us-west-2.amazonaws.com/ent-search-results/mall.png'
                    })

    def update_search_results(self):
        """
        Update the search-results.
        """
        if self.offset == 0:
            self.update_search_results_neighborhoods()
            self.update_search_results_hotel_and_malls()

    def process_offers(self):
        """
        Process offers.
        """
        if self.offers:
            self.set_query_type_is_name()
            self.get_redemptions_quantities()
            self.set_offer_related_defaults()
            self.initialize_offer_attributes()
            self.set_customer_redemptions()
            self.update_offer_attributes()
            self.update_outlets()
            self.process_outlets()
            self.process_final_outlets()
            self.update_search_results()

    def prepare_outlet_chunks_to_return(self):
        """
        Pagination of final-outlets.
        """
        end = self.limit + self.offset
        self.__outlets_chunk_to_return = self.final_outlets[self.offset:None if self.limit <= 0 else end]

    def get_tabs(self):
        if not self.offset and not self.filter_by_type:
            self.tabs = self.customer_profile_class_instance.get_tabs_vc01(self.customer.get('purchased_skus', []), self.locale)

    def prepare_filtered_final_outlets(self):
        """
        Filter final-outlets.
        """
        self.get_tabs()
        self.filtered_outlets = self.__outlets_chunk_to_return

    def prepare_response(self):
        """
        Prepare http response to send.
        """
        self.outlet_response = {
            'search_results': self.search_results,
            'featured_merchants': self.featured_merchants,
            'outlets': self.filtered_outlets,
            'limit': self.limit,
            'tabs': self.tabs
        }
        self.set_response({
            'data': self.outlet_response,
            'message': 'success',
            'success': True
        })

    def process_request(self):
        self.initialize_class_attributes()
        self.initialize_repos()
        self.load_customer_profile_and_session_data()
        if self.is_send_response_flag_on():
            return
        self.get_offers_from_db()
        self.process_offers()
        self.prepare_outlet_chunks_to_return()
        self.prepare_filtered_final_outlets()
        self.prepare_response()
