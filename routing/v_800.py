"""
Routing collection v800.
"""
from routing.v_71 import RoutingV71
from web_api.api_v800.configs_api.api import ConfigsApiV800
from web_api.api_v800.es_outlets.api import ESOutletApiV800
from web_api.api_v800.home.api import HomeApiV800
from web_api.api_v800.merchant.api import MerchantAPIV800
from web_api.api_v800.no_results_found.api import NoResultsFoundV800
from web_api.api_v800.outlets.api import OutletApiV800
from web_api.api_v800.personalize_home.api import PersonalizeHomeApiV800
from web_api.api_v800.profile_settings.api import ProfileSettingsApiV800
from web_api.api_v800.sign_in.api import LoginUserApiV800
from web_api.api_v800.sign_up.api import SignUpApiV800
from web_api.api_v800.trial_rules.api import TrialRulesV800
from web_api.api_v800.unsubscribe_product.api import UnsubscribeProduct
from web_api.api_v800.user_reset_password.api import UserPasswordResetApiV800


class RoutingV800(RoutingV71):
    api_version = '800'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['home'] = {'view': HomeApiV800, 'url': '/home'}
        self.routing_collection['personalize_home'] = {'view': PersonalizeHomeApiV800, 'url': '/personalize/home'}
        self.routing_collection['no-results-found'] = {'view': NoResultsFoundV800, 'url': '/no-results-found'}
        self.routing_collection['trial-rules'] = {'view': TrialRulesV800, 'url': '/user/trial/rules'}
        self.routing_collection['configs'] = {'view': ConfigsApiV800, 'url': '/configs'}
        self.routing_collection['outlets'] = {'view': OutletApiV800, 'url': '/outlets'}
        self.routing_collection['es_outlets'] = {'view': ESOutletApiV800, 'url': '/es_outlets'}
        self.routing_collection['passwords'] = {'view': UserPasswordResetApiV800, 'url': '/passwords'}
        self.routing_collection['sessions'] = {'view': LoginUserApiV800, 'url': '/sessions'}
        self.routing_collection['profile_settings'] = {'view': ProfileSettingsApiV800, 'url': '/profile/settings'}
        self.routing_collection['sign-up'] = {'view': SignUpApiV800, 'url': '/users'}
        self.routing_collection['merchant'] = {'view': MerchantAPIV800, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['unsubscribe-product'] = {'view': UnsubscribeProduct, 'url': '/unsubscribe/product'}
