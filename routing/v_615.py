"""
Routing collection V615
"""
from routing.v_614 import RoutingV614, RoutingVo614
from web_api.api_v615.api_rules.api import ApiRules
from web_api.api_v615.change_password.api import ChangePassword
from web_api.api_v615.configs.api import CheersConfigsApiV615, ConfigsApiV615
from web_api.api_v615.filters.api import FiltersApiV615
from web_api.api_v615.get_user_actions.api import (
    GetUserApiV615, GetUserProfileApiV615, OfflineGetUserProfileApiV615, UserPurchasesApiV615
)
from web_api.api_v615.get_user_friends_ranking.api import GetUserFriendsRankingApiV615
from web_api.api_v615.merchant_api.api import MerchantApiV615
from web_api.api_v615.merchant_products.api import MerchantProductsApi
from web_api.api_v615.products_history.api import ProductsHistoryApi
from web_api.api_v615.profile_settings.api import ProfileSettingsApi
from web_api.api_v615.sign_in.api import LoginUserApiV615
from web_api.api_v615.sign_up.api import SignUpApiV615
from web_api.api_v615.user_products.api import UserProductsApi


class RoutingV615(RoutingV614):
    api_version = '615'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['merchant'] = {
            'view': MerchantApiV615, 'url': '/merchants/<int:merchant_id>'
        }
        self.routing_collection['sign-up'] = {'view': SignUpApiV615, 'url': '/users'}
        self.routing_collection['sessions'] = {'view': LoginUserApiV615, 'url': '/sessions'}
        self.routing_collection['configs'] = {'view': ConfigsApiV615, 'url': '/configs'}
        self.routing_collection['cheers_configs'] = {'view': CheersConfigsApiV615, 'url': '/configurations/cheers'}
        self.routing_collection['filters'] = {'view': FiltersApiV615, 'url': '/filters'}
        self.routing_collection['get-user-friends-ranking'] = {
            'view': GetUserFriendsRankingApiV615, 'url': '/user/friends/ranking'
        }
        self.routing_collection['get-user-profile'] = {'view': GetUserProfileApiV615, 'url': '/user/get/profile'}
        self.routing_collection['get-user'] = {'view': GetUserApiV615, 'url': '/user/<int:user_id>'}
        self.routing_collection['user-purchases'] = {
            'view': UserPurchasesApiV615, 'url': '/users/<int:user_id>/purchases'
        }
        self.routing_collection['get-api-rules'] = {'view': ApiRules, 'url': '/rules'}
        self.routing_collection['change-password'] = {'view': ChangePassword, 'url': '/change/password'}
        # this will be removed in future. As this does not match with pattern.
        self.routing_collection['change_password'] = {'view': ChangePassword, 'url': '/change_password'}
        self.routing_collection['user_products'] = {'view': UserProductsApi, 'url': '/user/products'}
        self.routing_collection['profile_settings'] = {'view': ProfileSettingsApi, 'url': '/profile/settings'}
        self.routing_collection['product_history'] = {'view': ProductsHistoryApi, 'url': '/user/products/history'}
        self.routing_collection['merchant_products'] = {'view': MerchantProductsApi, 'url': '/user/products/merchant'}


class RoutingVo615(RoutingVo614):
    api_version = 'o615'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['get-user-profile'] = {'view': OfflineGetUserProfileApiV615, 'url': '/user/get/profile'}
