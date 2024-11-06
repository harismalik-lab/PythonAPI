"""
Contains the routing for version 64
"""
from offline_api.api_v64.redemption.api import OfflineRedemptionApiV64, OfflineRedemptionSyncApiV64
from offline_api.api_v64.sign_in.api import OfflineLoginUserApiV64
from offline_api.api_v64.sign_up.api import OfflineSignUpApiV64
from routing.v_63 import RoutingV63, RoutingVo63
from web_api.api_v64.category_home.api import CategoryHomeScreenV64
from web_api.api_v64.country.api import CountryApiV64
from web_api.api_v64.home.api import HomeApiV64
from web_api.api_v64.kaligo_deeplink_action.api import KaligoDeeplinkApi
from web_api.api_v64.location.api import LocationApiV64
from web_api.api_v64.merchant.api import MerchantApiV64, MerchantsApiV64
from web_api.api_v64.outlets.api import OutletApiV64
from web_api.api_v64.redemption.api import RedemptionProcessV64, RedemptionsSyncApiV64
from web_api.api_v64.sharing.api import PostSharingSendApiV64, GetSharingSendOffersV64, GetSharingReceivedOffersV64
from web_api.api_v64.sign_in.api import LoginUserApiV64
from web_api.api_v64.sign_up.api import SignUpApiV64
from web_api.api_v64.smiles.api import PostSmilesPurchaseApiV64


class RoutingV64(RoutingV63):
    api_version = '64'
    base_url = '/api_entertainer/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['sign-up'] = {'view': SignUpApiV64, 'url': '/users'}
        self.routing_collection['sessions'] = {'view': LoginUserApiV64, 'url': '/sessions'}
        self.routing_collection['redemptions'] = {'view': RedemptionProcessV64, 'url': '/redemptions'}
        self.routing_collection['redemptions-sync'] = {'view': RedemptionsSyncApiV64, 'url': '/redemptions/sync'}
        self.routing_collection['home'] = {'view': HomeApiV64, 'url': '/home'}
        self.routing_collection['merchant'] = {'view': MerchantApiV64, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['merchants'] = {'view': MerchantsApiV64, 'url': '/merchants'}
        self.routing_collection['outlets'] = {'view': OutletApiV64, 'url': '/outlets'}
        self.routing_collection['category_home'] = {'view': CategoryHomeScreenV64, 'url': '/categories/home'}
        self.routing_collection['send_offer'] = {'view': PostSharingSendApiV64, 'url': '/sharing/send'}
        self.routing_collection['sent_offers'] = {'view': GetSharingSendOffersV64, 'url': '/sharing/sendoffers'}
        self.routing_collection['received_offers'] = {'view': GetSharingReceivedOffersV64,
                                                      'url': '/sharing/receivedoffers'}
        self.routing_collection['country'] = {'view': CountryApiV64, 'url': '/country'}
        self.routing_collection['locations'] = {'view': LocationApiV64, 'url': '/locations'}
        self.routing_collection['smiles_purchase'] = {'view': PostSmilesPurchaseApiV64, 'url': '/smiles/purchase'}
        self.routing_collection['deeplink'] = {'view': KaligoDeeplinkApi, 'url': '/kaligo/deeplink'}


class RoutingVo64(RoutingVo63):
    api_version = 'o64'
    base_url = '/api_entertainer/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['category_home'] = {'view': CategoryHomeScreenV64, 'url': '/categories/home'}
        self.routing_collection['country'] = {'view': CountryApiV64, 'url': '/country'}
        self.routing_collection['home'] = {'view': HomeApiV64, 'url': '/home'}
        self.routing_collection['locations'] = {'view': LocationApiV64, 'url': '/locations'}
        self.routing_collection['merchant'] = {'view': MerchantApiV64, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['merchants'] = {'view': MerchantsApiV64, 'url': '/merchants'}
        self.routing_collection['outlets'] = {'view': OutletApiV64, 'url': '/outlets'}
        self.routing_collection['redemptions'] = {'view': OfflineRedemptionApiV64, 'url': '/redemptions'}
        self.routing_collection['redemptions-sync'] = {'view': OfflineRedemptionSyncApiV64, 'url': '/redemptions/sync'}
        self.routing_collection['received_offers'] = {'view': GetSharingReceivedOffersV64,
                                                      'url': '/sharing/receivedoffers'}
        self.routing_collection['sessions'] = {'view': OfflineLoginUserApiV64, 'url': '/sessions'}
        self.routing_collection['sign-up'] = {'view': OfflineSignUpApiV64, 'url': '/users'}
        self.routing_collection['send_offer'] = {'view': PostSharingSendApiV64, 'url': '/sharing/send'}
        self.routing_collection['sent_offers'] = {'view': GetSharingSendOffersV64, 'url': '/sharing/sendoffers'}
        self.routing_collection['smiles_purchase'] = {'view': PostSmilesPurchaseApiV64, 'url': '/smiles/purchase'}
