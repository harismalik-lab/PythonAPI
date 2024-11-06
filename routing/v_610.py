"""
Routing for version 6.10
"""
from routing.v_67 import RoutingV67, RoutingVo67
from web_api.api_v610.home.api import HomeApiV610
from web_api.api_v610.location.api import LocationApiV610


class RoutingV610(RoutingV67):
    api_version = '610'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['home'] = {'view': HomeApiV610, 'url': '/home'}
        self.routing_collection['locations'] = {'view': LocationApiV610, 'url': '/locations'}


class RoutingVo610(RoutingVo67):
    api_version = 'o610'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['home'] = {'view': HomeApiV610, 'url': '/home'}
        self.routing_collection['locations'] = {'view': LocationApiV610, 'url': '/locations'}
