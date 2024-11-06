"""
Routing collection v70
"""
from routing.v_615 import RoutingV615, RoutingVo615
from web_api.api_v70.add_delivery_location.api import AddUserDeliveryLocationV70
from web_api.api_v70.assign_pings.api import AssignPings
from web_api.api_v70.cache.api import RemoveCacheAPIView
from web_api.api_v70.configs_api.api import ConfigsApiV70
from web_api.api_v70.current_order_status_v7.api import CurrentOrderStatusApiV70
from web_api.api_v70.dc_marketing.api import DCMarketingApiV70
from web_api.api_v70.family_info_api.api import FamilyInfoApiV70
from web_api.api_v70.family_member_details.api import FamilyMemberDetailsV70
from web_api.api_v70.favourite_add.api import FavouriteAddApi
from web_api.api_v70.favourite_remove.api import FavouriteRemoveApi
from web_api.api_v70.favourites.api import FavouritesApi
from web_api.api_v70.filters_api_v7.api import FiltersApiV70
from web_api.api_v70.get_user_actions.get_user_actions_api import GetUserProfileApiV70
from web_api.api_v70.get_user_delivery_addresses.api import GetUserDeliveryLocationsV70
from web_api.api_v70.get_user_friends_ranking.api import GetUserFriendsRankingApiV70
from web_api.api_v70.get_user_table_booking.api import UserTableBookingsV70
from web_api.api_v70.google_data_get.api import GoogleDataGetApiView
from web_api.api_v70.google_data_update.api import GoogleDataUpdateApiView
from web_api.api_v70.google_reviews.api import GoogleReviewAPI
from web_api.api_v70.home.api import HomeApiV70
from web_api.api_v70.locations_api.api import LocationApiV70
from web_api.api_v70.log_details.api import DetailAPIV70
from web_api.api_v70.merchant_api.api import MerchantApiV70
from web_api.api_v70.merchant_products.api import MerchantProductsApiV70
from web_api.api_v70.merchant_redemption_rating.api import MerchantRedemptionRatingApi
from web_api.api_v70.my_family.api import MyFamilyV70
from web_api.api_v70.on_click_status_update_api.api import OnClickStatusUpdateApi
from web_api.api_v70.order_details_api_v70.api import OrderDetailsApiV70
from web_api.api_v70.orders_history.api import OrderHistoryApiV70
from web_api.api_v70.outlets.api import OutletApiV70
from web_api.api_v70.pending_notifications.api import PendingNotificationsV70
from web_api.api_v70.pending_order_status.api import GetPendingOrderStatusApiV70
from web_api.api_v70.pings_sharing.api import PingsSharingUrl
from web_api.api_v70.post_user_actions.post_user_actions_api import PostUserApiv70
from web_api.api_v70.sharing.api import GetSharingReceivedOffersV70, GetSharingSendOffersV70, PostSharingAcceptApiV70
from web_api.api_v70.sign_in.api import LoginUserApiV70
from web_api.api_v70.sign_up.api import SignUpApiV70
from web_api.api_v70.trial_rules.api import TrialRules
from web_api.api_v70.update_delivery_location.api import UpdateUserDeliveryLocationV70
from web_api.api_v70.update_es_outlets.api import UpdateOutletIndex
from web_api.api_v70.user_products.api import UserProductsApiV70
from web_api.api_v70.validate_email.api import ValidateEmailV70
from web_api.api_v70.wl_promo_codes_history.api import WLPromoCodesHistory
from web_api.api_v70.wl_redemption.api import WLRedemptionAPI


class RoutingV70(RoutingV615):
    api_version = '70'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['sign-up'] = {'view': SignUpApiV70, 'url': '/users'}
        self.routing_collection['sessions'] = {'view': LoginUserApiV70, 'url': '/sessions'}
        self.routing_collection['validate-email'] = {'view': ValidateEmailV70, 'url': '/validate/email'}
        self.routing_collection['sent_offers'] = {'view': GetSharingSendOffersV70, 'url': '/sharing/sendoffers'}
        self.routing_collection['received_offers'] = {
            'view': GetSharingReceivedOffersV70, 'url': '/sharing/receivedoffers'
        }
        self.routing_collection['accept_offer'] = {'view': PostSharingAcceptApiV70, 'url': '/sharing/accept'}
        self.routing_collection['member_details'] = {'view': FamilyMemberDetailsV70, 'url': '/family/member_details'}
        self.routing_collection['order-details'] = {'view': OrderDetailsApiV70,
                                                    'url': '/cashless/order_details'}
        self.routing_collection['get-user-friends-ranking'] = {
            'view': GetUserFriendsRankingApiV70,
            'url': '/user/friends/ranking'
        }
        self.routing_collection['home'] = {'view': HomeApiV70, 'url': '/home'}
        self.routing_collection['locations'] = {'view': LocationApiV70, 'url': '/locations'}
        self.routing_collection['configs'] = {'view': ConfigsApiV70, 'url': '/configs'}
        self.routing_collection['order-current-status'] = {
            'view': CurrentOrderStatusApiV70, 'url': '/cashless/order_current_status'
        }
        self.routing_collection['pending-notifications'] = {
            'view': PendingNotificationsV70, 'url': '/pending_notifications'
        }
        self.routing_collection['pending-order-status'] = {'view': GetPendingOrderStatusApiV70,
                                                           'url': '/cashless/pending_order_status'}
        self.routing_collection['order-history'] = {'view': OrderHistoryApiV70, 'url': '/cashless/order_history'}
        self.routing_collection['family-info'] = {'view': FamilyInfoApiV70, 'url': '/family/familyinfo'}
        self.routing_collection['favourite-add'] = {'view': FavouriteAddApi, 'url': '/user/favourite/add'}
        self.routing_collection['favourite-remove'] = {'view': FavouriteRemoveApi, 'url': '/user/favourite/remove'}
        self.routing_collection['favourites'] = {'view': FavouritesApi, 'url': '/user/favourite/list'}
        self.routing_collection['post-user'] = {'view': PostUserApiv70, 'url': '/users/<int:user_id>'}
        self.routing_collection['get-user-profile'] = {'view': GetUserProfileApiV70, 'url': '/user/get/profile'}
        # remove support for '/user/<int:user_id>' as its attributes available in '/user/get/profile' API
        self.routing_collection.pop('get-user', None)
        self.routing_collection['outlets'] = {'view': OutletApiV70, 'url': '/outlets'}
        self.routing_collection['filters'] = {'view': FiltersApiV70, 'url': '/filters'}
        self.routing_collection['trial-rules'] = {'view': TrialRules, 'url': '/user/trial/rules'}
        self.routing_collection['my_family'] = {'view': MyFamilyV70, 'url': '/family/my_family'}
        self.routing_collection['user-table-bookings'] = {
            'view': UserTableBookingsV70, 'url': '/user/reservations/history'
        }
        self.routing_collection['merchant'] = {
            'view': MerchantApiV70, 'url': '/merchants/<int:merchant_id>'
        }
        self.routing_collection['post-get-user-delivery-locations'] = {
            'view': GetUserDeliveryLocationsV70, 'url': '/user/delivery_locations'
        }
        self.routing_collection['post-add-user-delivery-location'] = {
            'view': AddUserDeliveryLocationV70, 'url': '/user/add_delivery_location'
        }
        self.routing_collection['post-update-user-delivery-location'] = {
            'view': UpdateUserDeliveryLocationV70, 'url': '/user/update_delivery_location'
        }
        self.routing_collection['google_reviews'] = {
            'view': GoogleReviewAPI, 'url': '/google/review'
        }
        self.routing_collection['merchant_products'] = {
            'view': MerchantProductsApiV70, 'url': '/user/products/merchant'
        }
        self.routing_collection['user_products'] = {
            'view': UserProductsApiV70, 'url': '/user/products'
        }
        self.routing_collection['quiqup-status-update'] = {
            'view': OnClickStatusUpdateApi, 'url': '/webhooks/on_click_status_update'
        }
        self.routing_collection['clear_cache'] = {
            'view': RemoveCacheAPIView, 'url': '/remove/cache'
        }
        self.routing_collection['assign-pings'] = {
            'view': AssignPings, 'url': '/assign/pings'
        }
        self.routing_collection['wl-redemptions'] = {'view': WLRedemptionAPI, 'url': '/wl/redemptions'}
        self.routing_collection['wl-promo-codes-history'] = {'view': WLPromoCodesHistory, 'url': '/wl/promo_codes_history'}
        self.routing_collection['pings-sharing-url'] = {'view': PingsSharingUrl, 'url': '/pings/sharing/url'}
        self.routing_collection['dc_marketing'] = {'view': DCMarketingApiV70, 'url': '/dc/tiles'}
        self.routing_collection['update-es-outlets'] = {
            'view': UpdateOutletIndex, 'url': '/update/data'
        }
        self.routing_collection['detail'] = {
            'view': DetailAPIV70, 'url': '/detail/'
        }
        self.routing_collection['google_data_update'] = {
            'view': GoogleDataUpdateApiView, 'url': '/outlet/google_data/update/'
        }
        self.routing_collection['google_data_get'] = {
            'view': GoogleDataGetApiView, 'url': '/outlet/google_data/get/'
        }
        self.routing_collection['merchant-redemption-rating'] = {
            'view': MerchantRedemptionRatingApi, 'url': '/redemption/rating'
        }


class RoutingVo70(RoutingVo615):
    api_version = 'o70'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
