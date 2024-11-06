"""
Routing collection V613
"""

from routing.v_612 import RoutingV612, RoutingVo612
from web_api.api_v612.verify_model_api.api import QuiqupStatusUpdateApi
from web_api.api_v613.category_home.api import CategoryHomeScreenV613
from web_api.api_v613.configs.api import ConfigsApiV613
from web_api.api_v613.current_order_status.api import CurrentOrderStatusApiV613
from web_api.api_v613.filters.api import FiltersApiV613
from web_api.api_v613.merchant.api import MerchantApiV613
from web_api.api_v613.outlet_online_state.api import OutletOnlineState
from web_api.api_v613.outlets.api import OutletApiV613


class RoutingV613(RoutingV612):
    api_version = '613'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['order-current-status'] = {
            'view': CurrentOrderStatusApiV613, 'url': '/cashless/order_current_status'
        }
        self.routing_collection['quiqup-status-update'] = {
            'view': QuiqupStatusUpdateApi, 'url': '/webhooks/quiqup_status_update'
        }
        self.routing_collection['merchant'] = {
            'view': MerchantApiV613, 'url': '/merchants/<int:merchant_id>'
        }
        self.routing_collection['outlets'] = {'view': OutletApiV613, 'url': '/outlets'}
        self.routing_collection['outlet-online-status'] = {'view': OutletOnlineState, 'url': '/outlet_online_state'}
        self.routing_collection['filters'] = {'view': FiltersApiV613, 'url': '/filters'}
        self.routing_collection['category_home'] = {'view': CategoryHomeScreenV613, 'url': '/categories/home'}
        self.routing_collection['configs'] = {'view': ConfigsApiV613, 'url': '/configs'}


class RoutingVo613(RoutingVo612):
    api_version = 'o613'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
