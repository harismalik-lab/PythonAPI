"""
Routing for version 6.12
"""
from routing.v_610 import RoutingV610, RoutingVo610
from web_api.api_v612.cashless_re_order_validation.api import CashlessReOrderValidation
from web_api.api_v612.delivery_statuses.api import CurrentOrderStatusApiV612
from web_api.api_v612.home.api import HomeApiV612
from web_api.api_v612.merchant.api import MerchantApiV612
from web_api.api_v612.pending_order_status.api import GetPendingOrderStatusApiV612
from web_api.api_v612.pings_history.api import PingHistory
from web_api.api_v612.pings_recall.api import PingRecall
from web_api.api_v612.table_reservation_cancellation.api import TableReservationCancellationApi
from web_api.api_v612.verify_model_api.api import QuiqupStatusUpdateApi


class RoutingV612(RoutingV610):
    api_version = '612'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['table_reservation_cancellation_api'] = {'view': TableReservationCancellationApi,
                                                                         'url': '/reservation/cancel'}
        self.routing_collection['home'] = {'view': HomeApiV612, 'url': '/home'}
        self.routing_collection['merchant'] = {'view': MerchantApiV612, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['pending-order-status'] = {'view': GetPendingOrderStatusApiV612,
                                                           'url': '/cashless/pending_order_status'}
        self.routing_collection['cashless-re-order-validation'] = {
            'view': CashlessReOrderValidation, 'url': '/cashless/re-order/validation'
        }
        self.routing_collection['order-current-status'] = {
            'view': CurrentOrderStatusApiV612, 'url': '/cashless/order_current_status'
        }
        self.routing_collection['pings-history'] = {
            'view': PingHistory, 'url': '/pings/history'
        }
        self.routing_collection['ping-recall'] = {
            'view': PingRecall, 'url': '/pings/recall'
        }
        self.routing_collection['web_hook_quiq_up'] = {
            'view': QuiqupStatusUpdateApi, 'url': '/webhooks/webhook-job'
        }


class RoutingVo612(RoutingVo610):
    api_version = 'o612'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
