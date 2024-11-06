"""
Routing for version 6.7
"""
from offline_api.api_v67.delivery_restrict_view.api import OfflineDeliveryRestrictApi
from offline_api.api_v67.home.api import HomeApiVo67
from offline_api.api_v67.merchants.api import MerchantApiVo67
from routing.v_68 import RoutingV68, RoutingVo68
from web_api.api_v67.add_delivery_location.api import AddUserDeliveryLocation
from web_api.api_v67.cancel_order_api.api import OrderCancelledApi
from web_api.api_v67.category_home.api import CategoryHomeScreenV67
from web_api.api_v67.current_order_status_api.api import CurrentOrderStatusApi
from web_api.api_v67.edit_order_api.api import EditOrderApi
from web_api.api_v67.edit_order_status_api.api import OrderEditStatusApi
from web_api.api_v67.get_user_delivery_addresses.api import GetUserDeliveryLocations
from web_api.api_v67.get_user_table_booking.api import UserTableBookings
from web_api.api_v67.home.api import HomeApiV67
from web_api.api_v67.merchant.api import MerchantApiV67
from web_api.api_v67.offer_redeemability.api import OfferRedeemabilityAPI
from web_api.api_v67.order_details_api.api import OrderDetailsApi
from web_api.api_v67.order_history_api.api import OrderHistoryApi
from web_api.api_v67.order_redemption.api import OrderRedemptionAPI
from web_api.api_v67.outlets.api import OutletApiV67
from web_api.api_v67.pending_order_status.api import GetPendingOrderStatusApi
from web_api.api_v67.selected_locations_api.api import SelectedLocationsApi
from web_api.api_v67.update_delivery_location.api import UpdateUserDeliveryLocation
from web_api.api_v67.update_phone_number_api.api import UpdatePhoneNumberApi
from web_api.api_v67.visa.api import VisaValidationStatusApi
from web_api.api_v67.visa.views import VisaAuthStatusAPI, VisaIframeTokenApi


class RoutingV67(RoutingV68):
    api_version = '67'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['cancel-order'] = {'view': OrderCancelledApi,
                                                   'url': '/cashless/cancel_order'}
        self.routing_collection['home'] = {'view': HomeApiV67, 'url': '/home'}
        self.routing_collection['category_home'] = {'view': CategoryHomeScreenV67, 'url': '/categories/home'}
        self.routing_collection['edit-order'] = {'view': EditOrderApi, 'url': '/cashless/edit_order'}
        self.routing_collection['edit-order-status'] = {'view': OrderEditStatusApi, 'url': '/cashless/edit_order_state'}
        self.routing_collection['merchant'] = {'view': MerchantApiV67, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['pending-order-status'] = {'view': GetPendingOrderStatusApi,
                                                           'url': '/cashless/pending_order_status'}
        self.routing_collection['post-user-phone-number'] = {'view': UpdatePhoneNumberApi,
                                                             'url': '/users/update_phone_number'}
        self.routing_collection['post-get-user-delivery-locations'] = {'view': GetUserDeliveryLocations,
                                                                       'url': '/user/delivery_locations'}
        self.routing_collection['post-add-user-delivery-location'] = {'view': AddUserDeliveryLocation,
                                                                      'url': '/user/add_delivery_location'}
        self.routing_collection['post-update-user-delivery-location'] = {'view': UpdateUserDeliveryLocation,
                                                                         'url': '/user/update_delivery_location'}
        self.routing_collection['offer-redeemability'] = {'view': OfferRedeemabilityAPI,
                                                          'url': '/cashless/offer_redeemability'}
        self.routing_collection['order-history'] = {'view': OrderHistoryApi, 'url': '/cashless/order_history'}
        self.routing_collection['outlets'] = {'view': OutletApiV67, 'url': '/outlets'}
        self.routing_collection['order-details'] = {'view': OrderDetailsApi,
                                                    'url': '/cashless/order_details'}
        self.routing_collection['order-current-status'] = {'view': CurrentOrderStatusApi,
                                                           'url': '/cashless/order_current_status'}
        self.routing_collection['order-redemption'] = {'view': OrderRedemptionAPI,
                                                       'url': '/cashless/order_redemption'}
        self.routing_collection['selected-locations'] = {'view': SelectedLocationsApi,
                                                         'url': '/cashless/selected_locations'}
        self.routing_collection['visa-iframe'] = {'view': VisaIframeTokenApi,
                                                  'url': '/visa/iframe'}
        self.routing_collection['visa-iframe-success'] = {'view': VisaAuthStatusAPI,
                                                          'url': '/visa/vces_auth_status'}
        self.routing_collection['visa-validation-status'] = {'view': VisaValidationStatusApi,
                                                             'url': '/visa/vces_validation_status'}
        self.routing_collection['user-table-bookings'] = {'view': UserTableBookings,
                                                          'url': '/user/reservations/history'}


class RoutingVo67(RoutingVo68):
    api_version = 'o67'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['cancel-order'] = {'view': OfflineDeliveryRestrictApi, 'url': '/cashless/cancel_order'}
        self.routing_collection['category_home'] = {'view': CategoryHomeScreenV67, 'url': '/categories/home'}
        self.routing_collection['edit-order'] = {'view': OfflineDeliveryRestrictApi, 'url': '/cashless/edit_order'}
        self.routing_collection['edit-order-status'] = {'view': OrderEditStatusApi, 'url': '/cashless/edit_order_state'}
        self.routing_collection['merchants'] = {'view': MerchantApiVo67, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['home'] = {'view': HomeApiVo67, 'url': '/home'}
        self.routing_collection['pending-order-status'] = {'view': GetPendingOrderStatusApi,
                                                           'url': '/cashless/pending_order_status'}
        self.routing_collection['post-get-user-delivery-locations'] = {'view': GetUserDeliveryLocations,
                                                                       'url': '/user/delivery_locations'}
        self.routing_collection['offer-redeemability'] = {'view': OfferRedeemabilityAPI,
                                                          'url': '/cashless/offer_redeemability'}
        self.routing_collection['order-history'] = {'view': OrderHistoryApi, 'url': '/cashless/order_history'}
        self.routing_collection['outlets'] = {'view': OutletApiV67, 'url': '/outlets'}
        self.routing_collection['order-details'] = {'view': OrderDetailsApi,
                                                    'url': '/cashless/order_details'}
        self.routing_collection['order-current-status'] = {'view': CurrentOrderStatusApi,
                                                           'url': '/cashless/order_current_status'}
        self.routing_collection['order-redemption'] = {'view': OfflineDeliveryRestrictApi,
                                                       'url': '/cashless/order_redemption'}
        self.routing_collection['post-add-user-delivery-location'] = {'view': OfflineDeliveryRestrictApi,
                                                                      'url': '/user/add_delivery_location'}
        self.routing_collection['post-user-phone-number'] = {'view': OfflineDeliveryRestrictApi,
                                                             'url': '/users/update_phone_number'}
        self.routing_collection['post-update-user-delivery-location'] = {'view': OfflineDeliveryRestrictApi,
                                                                         'url': '/user/update_delivery_location'}
        self.routing_collection['selected-locations'] = {'view': SelectedLocationsApi,
                                                         'url': '/cashless/selected_locations'}
