"""
Base routing file. Includes all the routing information and mapping of urls
"""
from flask import Blueprint, current_app
from flask_restful import Api

from app_configurations.settings import api_prefix
from common import swagger
from common.common_helpers import blue_print_app
from web_api.healt_check_api.api import HealthCheckAPI


class BaseRouting(object):
    api = None
    api_bp = None
    app = None
    api_version = ''
    base_url = api_prefix
    routing_collection = {}
    health_check_path = '/healthcheck'
    health_check_api_name = 'health-check'

    def __init__(self, app=None, name='__main__'):
        self.app = app
        blue_print_version = 'api_v{api_version}_{app}'.format(
            api_version=self.api_version,
            app=blue_print_app()
        )
        self.api_bp = Blueprint(blue_print_version, name)
        if current_app.config.get('IS_SWAGGER_ON', False):
            self.api = swagger.docs(Api(self.api_bp),
                                    description="Entertainer End Points Documentations",
                                    basePath='/',
                                    resourcePath='/',
                                    produces=["application/json"],
                                    api_spec_url='/api/spec',
                                    apiVersion=self.api_version
                                    )
        else:
            self.api = Api(self.api_bp)

        self.api.add_resource(
            HealthCheckAPI(),
            self.health_check_path,
            endpoint=self.health_check_api_name
        )

    def set_routing_collection(self):
        pass

    def update_routing_collection(self):
        pass

    def add_resources(self):
        for api_name, api_info in self.routing_collection.items():
            self.api.add_resource(
                api_info.get('view'),
                api_info.get('url'),
                endpoint=api_name
            )
        self.app.register_blueprint(
            self.api_bp,
            url_prefix="{base_url}/v{api_version}".format(
                base_url=self.base_url,
                api_version=self.api_version
            )
        )

    def map_urls(self):
        self.set_routing_collection()
        self.update_routing_collection()
        self.add_resources()
