"""
Routing Delivery Cashless
"""
from delivery_cashless_api.v01.delivery_orders_history_api.api import \
    GetOrdersHistoryApi
from delivery_cashless_api.v01.delivery_settings_api.api import \
    DeliverySettingsApi
from delivery_cashless_api.v01.delivery_status_api.api import \
    GetDeliveryAllStatusesApi
from delivery_cashless_api.v01.device_config_get.api import DeviceConfigGet
from delivery_cashless_api.v01.device_config_post.api import \
    NewDeviceRegistration
from delivery_cashless_api.v01.device_online_status.change_device_online_status import (ChangeDeviceOnlineStatus,
                                                                                        PingApi)
from delivery_cashless_api.v01.device_token.api import UpdateDeviceToken
from delivery_cashless_api.v01.get_all_merchants_api.api import \
    GetAllMerchantsApi
from delivery_cashless_api.v01.get_outlet_menu.api import GetOutletMenuAPi
from delivery_cashless_api.v01.managemnet_pin_api.api import ManagementPinApi
from delivery_cashless_api.v01.menu_item_status_api.api import \
    MenuItemStatusApi
from delivery_cashless_api.v01.merchant_login.api import MerchantLoginApi
from delivery_cashless_api.v01.order_accepted.api import OrderAccepted
from delivery_cashless_api.v01.order_cancelled.api import OrderCancelled
from delivery_cashless_api.v01.order_completed.api import OrderCompleted
from delivery_cashless_api.v01.order_details.api import OrderDetailApi
from delivery_cashless_api.v01.order_refund.api import OrderRefund
from delivery_cashless_api.v01.order_rejected.api import OrderRejected
from delivery_cashless_api.v01.web_hook_push_notification.api import WebHookPushNotification
from routing.base_routing import BaseRouting


class DeliveryCashless(BaseRouting):
    """
    Delivery Cashless Routes
    """
    api_version = '1'
    base_url = '/delivery_pos_api'

    def set_routing_collection(self):
        self.routing_collection = {
            'change-device-online-status': {'view': ChangeDeviceOnlineStatus, 'url': '/device_online_status'},
            'change-menu-item-status': {'view': MenuItemStatusApi, 'url': '/change_menu_item_status'},
            'delivery-settings': {'view': DeliverySettingsApi, 'url': '/delivery_settings'},
            'new-device-registration': {'view': NewDeviceRegistration, 'url': '/save_outlet_device_config'},
            'device-config-get': {'view': DeviceConfigGet, 'url': '/device_config'},
            'ping': {'view': PingApi, 'url': '/ping'},
            'get-delivery-all-statuses': {'view': GetDeliveryAllStatusesApi, 'url': '/delivery_statuses'},
            'management-pin': {'view': ManagementPinApi, 'url': '/mgmt_pin'},
            'orders-history': {'view': GetOrdersHistoryApi, 'url': '/orders_history'},
            'order-detail': {'view': OrderDetailApi, 'url' : '/order_detail'},
            'outlet-menu': {'view': GetOutletMenuAPi, 'url': '/outlet_menu'},
            'search-merchants': {'view': GetAllMerchantsApi, 'url': '/search_by_merchants'},
            'order-accepted': {'view': OrderAccepted,'url': '/order_accepted'},
            'order-rejected': {'view': OrderRejected, 'url': '/order_rejected'},
            'order-cancelled': {'view': OrderCancelled, 'url': '/order_cancelled'},
            'order-refund': {'view': OrderRefund, 'url': '/order_refund'},
            'order-completed': {'view': OrderCompleted, 'url': '/order_completed'},
            'change-device-token': {'view': UpdateDeviceToken, 'url': '/update_device_token'},
            'push-notification': {'view': WebHookPushNotification, 'url': '/order_receive_hook'},
            'merchant-login': {'view': MerchantLoginApi, 'url': '/merchant_login'}
        }
