"""
Delivery Cashless Admin Configs
"""
import json

from requests import codes

from app_configurations.settings import DELIVERY_LOGS_PATH
from common.base_resource import BaseGetResource
from db_models.delivery_cashless.mongo_models import DeliveryAdminConfigs


class DeviceConfigGet(BaseGetResource):
    """
    This class handles the Device Config get endpoint
    """
    is_delivery_cashless = True
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=DELIVERY_LOGS_PATH,
            file_path='device_config/device_config_get.log'
        ),
        'name': 'device_config_get'
    }

    def process_request(self):
        """
        Get all Admin settings from mongodb.
        """
        config_settings = DeliveryAdminConfigs.objects.filter(
            is_active=True
        ).order_by('order').only("title", "key", "type")
        self.send_response_flag = True
        self.response = {
            'data': json.loads(config_settings.to_json()),
            'success': True,
            'message': 'success'
        }
        self.status_code = codes.OK
