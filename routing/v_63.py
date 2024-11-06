"""
Contains the routes for API version v63
"""
from offline_api.api_v592.app_rate_feedback.api import OfflinePostAppRateApi, OfflinePostAppFeedbackApi
from offline_api.api_v592.configs.api import OfflineConfigsApiV592
from offline_api.api_v592.redemption.api import OfflineRedemptionApiV592, OfflineRedemptionSyncApiV592
from offline_api.api_v592.sign_in.api import OfflineLoginUserApiV592
from offline_api.api_v592.sign_out.api import LogoutUserApiV592
from offline_api.api_v592.sign_up.api import OfflineSignUpApiV592
from offline_api.post_user_actions.post_user_actions_api import OfflinePostUserApi, OfflinePostUserLanguagesApi, \
    OfflinePostUserAuthenticateApi, OfflinePostUserMagentoAutoLoginTokenApi, OfflinePostUserProfileApi, \
    OfflineUserUpdateDemographicStateApi
from offline_api.sharing_offine.api import OfflinePostSharingSendApi, OfflinePostSharingAcceptApi
from offline_api.vip_key_validation.api import OfflineVipKeyValidationApi
from routing.v_60 import Routing_V6
from web_api.api_v63.categories_home.api import CategoryHomeScreen
from web_api.api_v63.country.api import CountryApiV63
from web_api.api_v63.merchants.es_api import EsMerchantApiV63
from web_api.api_v63.outlets.api import OutletApiV63
from web_api.api_v63.sharing.api import PostSharingSendApiV63, GetSharingSendOffersV63, GetSharingReceivedOffersV63
from web_api.api_v63.smiles.api import PostSmilesPurchaseApiV63
from web_api.configs.api import ConnectivityConfigsApi
from web_api.api_v60.configs.api import CheersConfigsApiV6


class RoutingV63(Routing_V6):
    api_version = '63'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['category_home'] = {'view': CategoryHomeScreen, 'url': '/categories/home'}
        self.routing_collection['smiles_purchase'] = {'view': PostSmilesPurchaseApiV63, 'url': '/smiles/purchase'}
        self.routing_collection['outlets'] = {'view': OutletApiV63, 'url': '/outlets'}
        self.routing_collection['send_offer'] = {'view': PostSharingSendApiV63, 'url': '/sharing/send'}
        self.routing_collection['sent_offers'] = {'view': GetSharingSendOffersV63, 'url': '/sharing/sendoffers'}
        self.routing_collection['received_offers'] = {'view': GetSharingReceivedOffersV63, 'url': '/sharing/receivedoffers'}
        self.routing_collection['merchant'] = {'view': EsMerchantApiV63, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['country'] = {'view': CountryApiV63, 'url': '/country'}


class RoutingVo63(RoutingV63):
    api_version = 'o63'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['send_offer'] = {'view': OfflinePostSharingSendApi, 'url': '/sharing/send'}
        self.routing_collection['accept_offer'] = {'view': OfflinePostSharingAcceptApi, 'url': '/sharing/accept'}
        self.routing_collection['configs'] = {'view': OfflineConfigsApiV592, 'url': '/configs'}
        self.routing_collection['connectivity_configs'] = {'view': ConnectivityConfigsApi,
                                                           'url': '/configurations/connectivity'}
        self.routing_collection['cheers_configs'] = {'view': CheersConfigsApiV6, 'url': '/configurations/cheers'}
        self.routing_collection['post-user'] = {'view': OfflinePostUserApi, 'url': '/users/<int:user_id>'}
        self.routing_collection['post-user-languages'] = {'view': OfflinePostUserLanguagesApi, 'url': '/userlanguages'}
        self.routing_collection['post-user-authenticate'] = {'view': OfflinePostUserAuthenticateApi,
                                                             'url': '/user/authenticate'}
        self.routing_collection['post-user-magento-auto-login'] = {'view': OfflinePostUserMagentoAutoLoginTokenApi,
                                                                   'url': '/users/<int:user_id>/magento_autologin_token'}
        self.routing_collection['post-user-profile'] = {'view': OfflinePostUserProfileApi, 'url': '/user/profile'}

        self.routing_collection['redemptions'] = {'view': OfflineRedemptionApiV592, 'url': '/redemptions'}
        self.routing_collection['redemptions-sync'] = {'view': OfflineRedemptionSyncApiV592, 'url': '/redemptions/sync'}
        self.routing_collection['sessions'] = {'view': OfflineLoginUserApiV592, 'url': '/sessions'}
        self.routing_collection['session-logout'] = {'view': LogoutUserApiV592, 'url': '/session/logout'}
        self.routing_collection['sign-up'] = {'view': OfflineSignUpApiV592, 'url': '/users'}
        self.routing_collection['update-user-demographic'] = {'view': OfflineUserUpdateDemographicStateApi,
                                                              'url': '/user/update/demographic/state'}
        self.routing_collection['validate-key'] = {'view': OfflineVipKeyValidationApi, 'url': '/validate/key'}
        self.routing_collection['app-rate'] = {'view': OfflinePostAppRateApi, 'url': '/app/rate'}
        self.routing_collection['app-feedback'] = {'view': OfflinePostAppFeedbackApi, 'url': '/app/feedback'}
