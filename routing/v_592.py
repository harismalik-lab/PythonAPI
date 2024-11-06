"""
This contains routing for API version v592
"""
from offline_api.api_v592.configs.api import OfflineConfigsApiV592
from offline_api.api_v592.redemption.api import OfflineRedemptionApiV592, OfflineRedemptionSyncApiV592
from offline_api.api_v592.sign_in.api import OfflineLoginUserApiV592
from offline_api.api_v592.sign_out.api import LogoutUserApiV592
from offline_api.api_v592.sign_up.api import OfflineSignUpApiV592
from offline_api.post_user_actions.post_user_actions_api import (OfflinePostUserApi, OfflinePostUserAuthenticateApi,
                                                                 OfflinePostUserLanguagesApi,
                                                                 OfflinePostUserMagentoAutoLoginTokenApi,
                                                                 OfflinePostUserProfileApi,
                                                                 OfflineUserUpdateDemographicStateApi)
from offline_api.sign_up.api import OfflineSignUpApi
from offline_api.vip_key_validation.api import OfflineVipKeyValidationApi
from routing.v_59 import Routing_V59
from web_api.api_v592.get_user_actions.get_user_actions_api import (GetUserApiV592, GetUserFriendsRankingApiV592,
                                                                    GetUserProductsApiV592, GetUserProfileApiV592,
                                                                    UserPurchasesApiV592, UserSavingsAPIV592)
from web_api.api_v592.home.api import HomeApiV592
from web_api.api_v592.merchants.api import MerchantApiV592
from web_api.api_v592.outlet.api import OutletApiV592
from web_api.api_v592.post_user_actions.post_user_actions_api import (PostUserApiV592, PostUserAuthenticateApiV592,
                                                                      PostUserLanguagesApiV592,
                                                                      PostUserMagentoAutoLoginTokenApiV592,
                                                                      PostUserProfileApiV592, PostUserUnFriendApiV592,
                                                                      UserUpdateDemographicStateApiV592)
from web_api.api_v592.sign_in.api import LoginUserApiV592
from web_api.api_v592.sign_up.api import SignUpApiV592
from web_api.api_v592.vip_key_validation.api import VipKeyValidationApiV592
from web_api.api_v592.redemption.api import RedemptionProcessV592, RedemptionsSyncApiV592
from web_api.configs.api import CheersConfigsApi, ConnectivityConfigsApi


class Routing_V592(Routing_V59):
    api_version = '592'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['get-user'] = {'view': GetUserApiV592, 'url': '/users/<int:user_id>'}
        self.routing_collection['get-user-products'] = {'view': GetUserProductsApiV592,
                                                        'url': '/user/<int:user_id>/products'}
        self.routing_collection['get-user-profile'] = {'view': GetUserProfileApiV592, 'url': '/user/profile'}
        self.routing_collection['get-user-friends-ranking'] = {'view': GetUserFriendsRankingApiV592,
                                                               'url': '/user/friends/ranking'}
        self.routing_collection['home'] = {'view': HomeApiV592, 'url': '/home'}
        self.routing_collection['merchant'] = {'view': MerchantApiV592, 'url': '/merchants/<int:merchant_id>'}

        self.routing_collection['outlets'] = {'view': OutletApiV592, 'url': '/outlets'}
        self.routing_collection['post-user'] = {'view': PostUserApiV592, 'url': '/users/<int:user_id>'}
        self.routing_collection['post-user-authenticate'] = {'view': PostUserAuthenticateApiV592,
                                                             'url': '/user/authenticate'}
        self.routing_collection['post-user-languages'] = {'view': PostUserLanguagesApiV592, 'url': '/userlanguages'}
        self.routing_collection['post-user-profile'] = {'view': PostUserProfileApiV592, 'url': '/user/profile'}
        self.routing_collection['post-user-unfriend'] = {'view': PostUserUnFriendApiV592, 'url': '/user/unfriend'}
        self.routing_collection['post-user-magento-auto-login'] = \
            {'view': PostUserMagentoAutoLoginTokenApiV592, 'url': '/users/<int:user_id>/magento_autologin_token'}
        self.routing_collection['sign-up'] = {'view': SignUpApiV592, 'url': '/users'}
        self.routing_collection['user-purchases'] = {'view': UserPurchasesApiV592,
                                                     'url': '/users/<int:user_id>/purchases'}
        self.routing_collection['user-savings'] = {'view': UserSavingsAPIV592, 'url': '/users/<int:user_id>/savings'}
        self.routing_collection['update-user-demographic'] = {'view': UserUpdateDemographicStateApiV592,
                                                              'url': '/user/update/demographic/state'}
        self.routing_collection['sessions'] = {'view': LoginUserApiV592, 'url': '/sessions'}
        self.routing_collection['validate-key'] = {'view': VipKeyValidationApiV592, 'url': '/validate/key'}
        self.routing_collection['merchant'] = {'view': MerchantApiV592, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['redemptions'] = {'view': RedemptionProcessV592, 'url': '/redemptions'}
        self.routing_collection['redemptions-sync'] = {'view': RedemptionsSyncApiV592, 'url': '/redemptions/sync'}


class Routing_Vo592(Routing_V592):
    api_version = 'o592'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['configs'] = {'view': OfflineConfigsApiV592, 'url': '/configs'}
        self.routing_collection['connectivity_configs'] = {'view': ConnectivityConfigsApi, 'url': '/configurations/connectivity'}
        self.routing_collection['cheers_configs'] = {'view': CheersConfigsApi, 'url': '/configurations/cheers'}
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
