"""
Routing collection V614
"""

from routing.v_613 import RoutingV613, RoutingVo613
from web_api.api_v614.merchant.api import MerchantApiV614
from web_api.api_v614.offer_redeemability.api import OfferRedeemabilityAPIV614
from web_api.api_v614.order_picket_up.api import OrderPickedUpAPI
from web_api.api_v614.outlets.api import OutletApiV614
from web_api.api_v614.promo_codes_history.api import PromoCodesHistory
from web_api.api_v614.redemption.api import RedemptionProcessV614
from web_api.api_v614.sign_in.api import LoginUserApiV614


class RoutingV614(RoutingV613):
    api_version = '614'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['sessions'] = {'view': LoginUserApiV614, 'url': '/sessions'}
        self.routing_collection['outlets'] = {'view': OutletApiV614, 'url': '/outlets'}
        self.routing_collection['redemptions'] = {'view': RedemptionProcessV614, 'url': '/redemptions'}
        self.routing_collection['promo-codes-history'] = {'view': PromoCodesHistory, 'url': '/promo_codes_history'}
        self.routing_collection['merchant'] = {
            'view': MerchantApiV614, 'url': '/merchants/<int:merchant_id>'
        }
        self.routing_collection['order-picked-up'] = {
            'view': OrderPickedUpAPI, 'url': '/cashless/order_picked_up'
        }
        self.routing_collection['offer-redeemability'] = {'view': OfferRedeemabilityAPIV614,
                                                          'url': '/cashless/offer_redeemability'}


class RoutingVo614(RoutingVo613):
    api_version = 'o614'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
