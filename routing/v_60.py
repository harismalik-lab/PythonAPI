"""
Contains the routes for API version v60
"""
from offline_api.api_v592.app_rate_feedback.api import OfflinePostAppRateApi, OfflinePostAppFeedbackApi
from offline_api.api_v592.configs.api import OfflineConfigsApiV592
from routing.v_592 import Routing_V592
from web_api.api_v60.app_rating.api import PostAppRateApi, PostAppFeedbackApi
from web_api.api_v60.configs.api import ConfigsApiV6, CheersConfigsApiV6
from web_api.api_v60.home.api import HomeApiV6
from web_api.api_v60.filters.api import FiltersApiV6
from web_api.api_v60.merchants.es_api import EsMerchantApiV6
from web_api.api_v60.outlet.api import OutletApiV6


class Routing_V6(Routing_V592):
    api_version = '6'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['home'] = {'view': HomeApiV6, 'url': '/home'}
        self.routing_collection['app-rate'] = {'view': PostAppRateApi, 'url': '/app/rate'}
        self.routing_collection['app-feedback'] = {'view': PostAppFeedbackApi, 'url': '/app/feedback'}
        self.routing_collection['configs'] = {'view': ConfigsApiV6, 'url': '/configs'}
        self.routing_collection['cheers_configs'] = {'view': CheersConfigsApiV6, 'url': '/configurations/cheers'}
        self.routing_collection['merchant'] = {'view': EsMerchantApiV6, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['outlets'] = {'view': OutletApiV6, 'url': '/outlets'}
        self.routing_collection['filters'] = {'view': FiltersApiV6, 'url': '/filters'}


class Routing_Vo6(Routing_V6):
    api_version = 'o6'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['app-rate'] = {'view': OfflinePostAppRateApi, 'url': '/app/rate'}
        self.routing_collection['app-feedback'] = {'view': OfflinePostAppFeedbackApi, 'url': '/app/feedback'}
        self.routing_collection['configs'] = {'view': OfflineConfigsApiV592, 'url': '/configs'}
