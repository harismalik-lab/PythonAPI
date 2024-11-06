"""
Routing collection v71.
"""
from routing.v_70 import RoutingV70
from web_api.api_v71.bookings_detail.api import BookingsDetail
from web_api.api_v71.bulk_redemption.api import BulkRedemptionProcess
from web_api.api_v71.cancel_bookings.api import BookingCancellationApi
from web_api.api_v71.check_in_details.api import CheckInDetail
from web_api.api_v71.cinema_booking_history.api import CinemaBookingHistory
from web_api.api_v71.configs_api.api import ConfigsApiV71
from web_api.api_v71.home.api import HomeApiV71
from web_api.api_v71.locations.api import LocationsAPIV71
from web_api.api_v71.merchant.api import MerchantAPIV71
from web_api.api_v71.multi_redemptions.api import MultiOrderRedemptionAPI
from web_api.api_v71.offer_redeemability.api import OfferRedeemabilityAPIV71
from web_api.api_v71.order_redemption_v71.api import OrderRedemptionAPIV71
from web_api.api_v71.outlets.api import OutletApiV71
from web_api.api_v71.products_history.api import ProductsHistoryV71
from web_api.api_v71.redeemption_business.api import RedemptionBusiness
from web_api.api_v71.redemption.api import RedemptionProcessV71
from web_api.api_v71.reservations_booking_history.api import ReservationBookingHistory
from web_api.api_v71.user_products.api import UserProductsApiV71


class RoutingV71(RoutingV70):
    api_version = '71'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['check_in_details'] = {'view': CheckInDetail, 'url': '/user/checkin/detail'}
        self.routing_collection['merchant'] = {
            'view': MerchantAPIV71, 'url': '/merchants/<int:merchant_id>'
        }
        self.routing_collection['bookings_detail'] = {
            'view': BookingsDetail, 'url': '/bookings/detail'
        }
        self.routing_collection['bookings_cancel'] = {
            'view': BookingCancellationApi, 'url': '/bookings/cancel'
        }
        self.routing_collection['reservation-booking-history'] = {
            'view': ReservationBookingHistory, 'url': '/reservations/booking/history'
        }
        self.routing_collection['multi-redemption'] = {
            'view': MultiOrderRedemptionAPI, 'url': '/multi/redemptions'
        }
        self.routing_collection['configs'] = {'view': ConfigsApiV71, 'url': '/configs'}
        self.routing_collection['outlets'] = {'view': OutletApiV71, 'url': '/outlets'}
        self.routing_collection['redemptions'] = {'view': RedemptionProcessV71, 'url': '/redemptions'}
        self.routing_collection['redemption-bulk'] = {'view': BulkRedemptionProcess, 'url': '/redemption/bulk'}
        self.routing_collection['redemption-business'] = {'view': RedemptionBusiness, 'url': '/redemption/business'}
        self.routing_collection['home'] = {'view': HomeApiV71, 'url': '/home'}
        self.routing_collection['product_history'] = {'view': ProductsHistoryV71, 'url': '/user/products/history'}
        self.routing_collection['locations'] = {'view': LocationsAPIV71, 'url': '/locations'}
        self.routing_collection['user_products'] = {'view': UserProductsApiV71, 'url': '/user/products'}
        self.routing_collection['offer-redeemability'] = {'view': OfferRedeemabilityAPIV71,
                                                          'url': '/cashless/offer_redeemability'}
        self.routing_collection['cinema-booking-history'] = {'view': CinemaBookingHistory,
                                                             'url': '/cinema_booking_history'}
        self.routing_collection['order-redemption'] = {'view': OrderRedemptionAPIV71,
                                                       'url': '/cashless/order_redemption'}
