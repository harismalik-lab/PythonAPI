from analytics_api.api import RedemptionHistoryApi, RedemptionSummaryApi
from app_configurations.settings import api_analytics_prefix
from offline_api.get_user_actions.get_user_actions_api import (
    OfflineGetUserApi, OfflineGetUserFriendsRankingApi, OfflineGetUserProductsApi, OfflineGetUserProfileApi
)
from offline_api.offline_reset_password.api import OfflineResetPasswordApi
from offline_api.post_user_actions.post_user_actions_api import (
    OfflinePostUserApi, OfflinePostUserAuthenticateApi, OfflinePostUserLanguagesApi,
    OfflinePostUserMagentoAutoLoginTokenApi, OfflinePostUserProfileApi, OfflineUserUpdateDemographicStateApi
)
from offline_api.redemption.api import OfflineRedemptionApi, OfflineRedemptionSyncApi
from offline_api.sharing_offine.api import (
    OfflineGetSharingPendingApi, OfflineGetSharingReceivedOffersApi, OfflineGetSharingSendOffers,
    OfflinePostSharingAcceptApi, OfflinePostSharingSendApi
)
from offline_api.sign_in.api import OfflineLoginUserApi
from offline_api.sign_up.api import OfflineSignUpApi
from offline_api.smiles_offline.api import OfflineSmilesPurchase
from offline_api.vip_key_validation.api import OfflineVipKeyValidationApi
from rewards_api.vc01.configs_api.api import ConnectConfigsApi
from rewards_api.vc01.country.api import RewardsCountryApi
from rewards_api.vc01.currency.api import RewardsCurrencyApi
from rewards_api.vc01.filters_api.api import RewardsFiltersApi
from rewards_api.vc01.locations_api.api import RewardsLocationApi
from rewards_api.vc01.merchants_api.api import RewardsMerchantApi, RewardsMerchantNameApi
from rewards_api.vc01.outlet.api import RewardsGetTabsAction
from rewards_api.vc01.outlet_api.api import OutletApi as Connect_OutletApi
from rewards_api.vc01.outlet_names_api.api import RewardsOutletNamesApi
from rewards_api.vc01.redemption_api.api import RedemptionProcess as CONNECT_RedemptionProcess
from rewards_api.vr01.sessions_update.api import RewardsSessionsUpdate
from rewards_api.vr01.sign_in.api import RewardsSignInApi
from rewards_api.vr01.sign_out.api import RewardsLogoutApi
from rewards_api.vr01.sign_up.api import RewardsSignUpApi
from rewards_api.vr01.user_actions_api.api import (
    RewardsGetUserApi, RewardsPostUserApi, RewardsPostUserLanguagesApi, RewardsUserSavingsAPI,
    RewardsUserUpdateDemographicStateApi
)
from routing.base_routing import BaseRouting
from web_api.appboy.api import AppboyFeedApi
from web_api.configs.api import CheersConfigsApi, ConfigsApi, ConnectivityConfigsApi
from web_api.country.api import CountryApi
from web_api.cuisines.api import AllCuisinesApi
from web_api.currency.api import CurrencyApi
from web_api.filters.api import FiltersApi
from web_api.get_user_actions.get_user_actions_api import (
    GetUserApi, GetUserFriendsRankingApi, GetUserProductsApi, GetUserProfileApi, GetUserSessionRefreshApi,
    UserPurchasesApi, UserSavingsAPI
)
from web_api.home.api import HomeApi
from web_api.hotel.api import HotelsApi
from web_api.location.api import LocationApi
from web_api.merchants.api import MerchantNameApi, MerchantNamesApi, MerchantOutletsApi, MerchantsApi
from web_api.merchants.es_api import EsMerchantApi
from web_api.outlet.api import OutletApi, OutletNamesApi
from web_api.post_user_actions.post_user_actions_api import (
    PostUserApi, PostUserAuthenticateApi, PostUserLanguagesApi, PostUserMagentoAutoLoginTokenApi, PostUserProfileApi,
    PostUserUnFriendApi, UserUpdateDemographicStateApi
)
from web_api.redemption.api import RedemptionProcess, RedemptionsSyncApi
from web_api.region.api import AllRegionApi
from web_api.sharing.api import (
    GetSharingPendingApi, GetSharingReceivedOffers, GetSharingSendOffers, PostSharingAcceptApi, PostSharingSendApi
)
from web_api.sign_in.api import LoginUserApi
from web_api.sign_out.api import LogoutUserApi
from web_api.sign_up.api import SignUpApi
from web_api.smiles.api import PostSmilesPurchaseApi
from web_api.user_reset_password.api import UserPasswordResetApi
from web_api.vip_key_validation.api import VipKeyValidationApi


class Routing_V59(BaseRouting):
    api_version = '59'

    def set_routing_collection(self):
        self.routing_collection = {
            'accept_offer': {'view': PostSharingAcceptApi, 'url': '/sharing/accept'},
            'appboy': {'view': AppboyFeedApi, 'url': '/feed/appboy'},
            'country': {'view': CountryApi, 'url': '/country'},
            'currencies': {'view': CurrencyApi, 'url': '/currencies'},
            'cuisines': {'view': AllCuisinesApi, 'url': '/cuisines'},
            'configs': {'view': ConfigsApi, 'url': '/configs'},
            'connectivity_configs': {'view': ConnectivityConfigsApi, 'url': '/configurations/connectivity'},
            'cheers_configs': {'view': CheersConfigsApi, 'url': '/configurations/cheers'},
            'filters': {'view': FiltersApi, 'url': '/filters'},
            'get-user': {'view': GetUserApi, 'url': '/users/<int:user_id>'},
            'get-user-profile': {'view': GetUserProfileApi, 'url': '/user/profile'},
            'get-user-products': {'view': GetUserProductsApi, 'url': '/user/<int:user_id>/products'},
            'get-user-refresh-session': {'view': GetUserSessionRefreshApi, 'url': '/user/session/refresh'},
            'get-user-friends-ranking': {'view': GetUserFriendsRankingApi, 'url': '/user/friends/ranking'},
            'home': {'view': HomeApi, 'url': '/home'},
            'hotels': {'view': HotelsApi, 'url': '/hotels'},
            'locations': {'view': LocationApi, 'url': '/locations'},
            'merchant': {'view': EsMerchantApi, 'url': '/merchants/<int:merchant_id>'},
            'merchants': {'view': MerchantsApi, 'url': '/merchants'},
            'merchantname': {'view': MerchantNameApi, 'url': '/merchantname'},
            'merchantnames': {'view': MerchantNamesApi, 'url': '/merchantnames'},
            'merchantoutlets': {'view': MerchantOutletsApi, 'url': '/merchantoutlets/<int:merchant_id>'},
            'outlets': {'view': OutletApi, 'url': '/outlets'},
            'outletnames': {'view': OutletNamesApi, 'url': '/outletnames'},
            'passwords': {'view': UserPasswordResetApi, 'url': '/passwords'},
            'pending_offers': {'view': GetSharingPendingApi, 'url': '/sharing/pending'},
            'post-user': {'view': PostUserApi, 'url': '/users/<int:user_id>'},
            'post-user-authenticate': {'view': PostUserAuthenticateApi, 'url': '/user/authenticate'},
            'post-user-languages': {'view': PostUserLanguagesApi, 'url': '/userlanguages'},
            'post-user-magento-auto-login': {'view': PostUserMagentoAutoLoginTokenApi,
                                             'url': '/users/<int:user_id>/magento_autologin_token'},
            'post-user-profile': {'view': PostUserProfileApi, 'url': '/user/profile'},
            'post-user-unfriend': {'view': PostUserUnFriendApi, 'url': '/user/unfriend'},
            'received_offers': {'view': GetSharingReceivedOffers, 'url': '/sharing/receivedoffers'},
            'redemptions': {'view': RedemptionProcess, 'url': '/redemptions'},
            'redemptions-sync': {'view': RedemptionsSyncApi, 'url': '/redemptions/sync'},
            'regions': {'view': AllRegionApi, 'url': '/regions'},
            'sessions': {'view': LoginUserApi, 'url': '/sessions'},
            'session-logout': {'view': LogoutUserApi, 'url': '/session/logout'},
            'send_offer': {'view': PostSharingSendApi, 'url': '/sharing/send'},
            'sign-up': {'view': SignUpApi, 'url': '/users'},
            'smiles_purchase': {'view': PostSmilesPurchaseApi, 'url': '/smiles/purchase'},
            'sent_offers': {'view': GetSharingSendOffers, 'url': '/sharing/sendoffers'},
            'user-purchases': {'view': UserPurchasesApi, 'url': '/users/<int:user_id>/purchases'},
            'user-savings': {'view': UserSavingsAPI, 'url': '/users/<int:user_id>/savings'},
            'update-user-demographic': {'view': UserUpdateDemographicStateApi, 'url': '/user/update/demographic/state'},
            'validate-key': {'view': VipKeyValidationApi, 'url': '/validate/key'}
        }


class Routing_Vo59(Routing_V59):
    api_version = 'o59'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['accept_offer'] = {'view': OfflinePostSharingAcceptApi, 'url': '/sharing/accept'}
        self.routing_collection['get-user'] = {'view': OfflineGetUserApi, 'url': '/users/<int:user_id>'}
        self.routing_collection['get-user-profile'] = {'view': OfflineGetUserProfileApi, 'url': '/user/profile'}
        self.routing_collection['get-user-products'] = {'view': OfflineGetUserProductsApi,
                                                        'url': '/user/<int:user_id>/products'}
        self.routing_collection['get-user-friends-ranking'] = {'view': OfflineGetUserFriendsRankingApi,
                                                               'url': '/user/friends/ranking'}
        self.routing_collection['passwords'] = {'view': OfflineResetPasswordApi, 'url': '/passwords'}
        self.routing_collection['pending_offers'] = {'view': OfflineGetSharingPendingApi, 'url': '/sharing/pending'}
        self.routing_collection['post-user'] = {'view': OfflinePostUserApi, 'url': '/users/<int:user_id>'}
        self.routing_collection['post-user-languages'] = {'view': OfflinePostUserLanguagesApi, 'url': '/userlanguages'}
        self.routing_collection['post-user-authenticate'] = {'view': OfflinePostUserAuthenticateApi,
                                                             'url': '/user/authenticate'}
        self.routing_collection['post-user-magento-auto-login'] = \
            {'view': OfflinePostUserMagentoAutoLoginTokenApi, 'url': '/users/<int:user_id>/magento_autologin_token'}
        self.routing_collection['post-user-profile'] = {'view': OfflinePostUserProfileApi, 'url': '/user/profile'}
        self.routing_collection['received_offers'] = {'view': OfflineGetSharingReceivedOffersApi,
                                                      'url': '/sharing/receivedoffers'}
        self.routing_collection['redemptions'] = {'view': OfflineRedemptionApi, 'url': '/redemptions'}
        self.routing_collection['redemptions-sync'] = {'view': OfflineRedemptionSyncApi, 'url': '/redemptions/sync'}
        self.routing_collection['send_offer'] = {'view': OfflinePostSharingSendApi, 'url': '/sharing/send'}
        self.routing_collection['sent_offers'] = {'view': OfflineGetSharingSendOffers, 'url': '/sharing/sendoffers'}
        self.routing_collection['sessions'] = {'view': OfflineLoginUserApi, 'url': '/sessions'}
        self.routing_collection['session-logout'] = {'view': LogoutUserApi, 'url': '/session/logout'}
        self.routing_collection['sign-up'] = {'view': OfflineSignUpApi, 'url': '/users'}
        self.routing_collection['smiles_purchase'] = {'view': OfflineSmilesPurchase, 'url': '/smiles/purchase'}
        self.routing_collection['update-user-demographic'] = {'view': OfflineUserUpdateDemographicStateApi,
                                                              'url': '/user/update/demographic/state'}
        self.routing_collection['validate-key'] = {'view': OfflineVipKeyValidationApi, 'url': '/validate/key'}


class Routing_V2_Analytics(BaseRouting):
    api_version = '2'
    base_url = api_analytics_prefix

    def set_routing_collection(self):
        self.routing_collection = {
            'summary': {'view': RedemptionSummaryApi, 'url': '/user/redemption/summary'},
            'history': {'view': RedemptionHistoryApi, 'url': '/user/redemption/history'}
        }


class RoutingVrRewards(BaseRouting):
    """
    Routing for rewards api
    """
    api_version = 'r01'

    def set_routing_collection(self):
        self.routing_collection = {
            'configs': {'view': ConnectConfigsApi, 'url': '/configs'},
            'currencies': {'view': RewardsCurrencyApi, 'url': '/currencies'},
            'country': {'view': RewardsCountryApi, 'url': '/country'},
            'filters': {'view': RewardsFiltersApi, 'url': '/filters'},
            'get-user': {'view': RewardsGetUserApi, 'url': '/users/<int:user_id>'},
            'locations': {'view': RewardsLocationApi, 'url': '/locations'},
            'merchantname': {'view': RewardsMerchantNameApi, 'url': '/merchantname'},
            'merchant': {'view': RewardsMerchantApi, 'url': '/merchants/<int:merchant_id>'},
            'outlets': {'view': Connect_OutletApi, 'url': '/outlets'},
            'outletnames': {'view': RewardsOutletNamesApi, 'url': '/outletnames'},
            'post-user': {'view': RewardsPostUserApi, 'url': '/users/<int:user_id>'},
            'post-user-languages': {'view': RewardsPostUserLanguagesApi, 'url': '/userlanguages'},
            'redemptions': {'view': CONNECT_RedemptionProcess, 'url': '/redemptions'},
            'sessions': {'view': RewardsSignInApi, 'url': '/sessions'},
            'sessions-update': {'view': RewardsSessionsUpdate, 'url': '/sessionsupdate'},
            'session-logout': {'view': RewardsLogoutApi, 'url': '/session/logout'},
            'sign-up': {'view': RewardsSignUpApi, 'url': '/users'},
            'tabs': {'view': RewardsGetTabsAction, 'url': '/tabs'},
            'update-user-demographic': {'view': RewardsUserUpdateDemographicStateApi,
                                        'url': '/user/update/demographic/state'},
            'user-savings': {'view': RewardsUserSavingsAPI, 'url': '/users/<int:user_id>/savings'}
        }
