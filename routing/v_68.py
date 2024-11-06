"""
Routing for version 6.8
"""
from routing.v_65 import RoutingV65, RoutingVo65
from web_api.api_v68.activate_key.api import ActivateKeyAPI
from web_api.api_v68.country.api import CountryApiV68
from web_api.api_v68.delete_location.api import DeleteLocationApi
from web_api.api_v68.extend_trials.api import ExtendTrialPeriodApi
from web_api.api_v68.merchant.api import MerchantApiV68


class RoutingV68(RoutingV65):
    api_version = '68'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['country'] = {'view': CountryApiV68, 'url': '/country'}
        self.routing_collection['merchant'] = {'view': MerchantApiV68, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['delete-location'] = {'view': DeleteLocationApi,
                                                      'url': '/user/remove_delivery_location'}
        self.routing_collection['extend-trial'] = {'view': ExtendTrialPeriodApi, 'url': '/user/extend_trial'}
        self.routing_collection['branch-io-integrartion'] = {'view': ActivateKeyAPI,
                                                             'url': '/user/activate_key'}


class RoutingVo68(RoutingVo65):
    api_version = 'o68'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['country'] = {'view': CountryApiV68, 'url': '/country'}
        self.routing_collection['merchant'] = {'view': MerchantApiV68, 'url': '/merchants/<int:merchant_id>'}
