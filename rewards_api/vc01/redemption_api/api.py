import datetime
import uuid

from app_configurations.settings import REWARDS_LOGS_PATH
from common.base_resource import BasePostResource
from common.common_helpers import CommonHelpers
from common.db import CONSOLIDATION, DEFAULT, INFORMATICA
from repositories.coordinate_repo import CoordinateRepository
from repositories.customer_repo import CustomerProfile
from repositories.informatica_mobile_redemption_repo import InformaticaMobileRedemptionRepository
from repositories.merchant_repo import MerchantRepository
from repositories.offer_repo import OfferRepository
from repositories.offer_slice_active_repo import OfferSliceActiveRepository
from repositories.outlet_repo import OutletRepository
from repositories.redemption_repo import RedemptionRepository
from repositories.translation_repo import MessageRepository
from user_authentication.authentication import get_current_customer
from web_api.redemption.background_task import process_records, sync_amazon_from_rackspace

from .validation import redemption_parser


class RedemptionProcess(BasePostResource):
    """
    Implementation: Validate the existence of the offers, the user, the outlet, and whether the offers are
    redeemable by this user at this outlet. From the outlet, merchant information can be retrieved
    and the PIN can then be verified. If all is OK, create a new record in the redemptions table and
    calculate the redemption_code.
    """
    backup_request_args_for_exception = False
    request_parser = redemption_parser
    response = {}
    logger_info = {
        'filename': '{log_path}{file_path}'.format(
            log_path=REWARDS_LOGS_PATH,
            file_path='redemption_api/redemption_vc01_api.log',
        ),
        'name': 'redemption_vc01_api'
    }
    logger = None
    status_code = 422
    connections_names = [DEFAULT, CONSOLIDATION, INFORMATICA]
    required_token = True

    def populate_request_arguments(self):
        """
        :param: offer_id : array=true, requirements="\d+", strict=true, description="Offer IDs that we are redeeming.
         Must belong to same Merchant."
        :param: quantity : array=true, requirements="\d+", default="1", strict=true,
         description="How many of each Offer we are redeeming."
        :param: isshared : strict=false, default="0", description="do you only want shared offers"
        :param: outlet_id : requirements="\d+", strict=true,
         description="the outlet at which the specified offer was redeemed"
        :param: merchant_pin : requirements="\d+", strict=true,
        description="PIN of merchant associated with the specified offer"
        :param: currency : requirements="[A-Z]+", default="USD", description="User currency"
        :param: lng : nullable=true, description="longitude"
        :param: lat : nullable=true, description="latitude")
        :param: is_reattempt : strict=false, requirements="0|1", default="0", description="is_reattempt call"
        :param: transaction_id : strict=false, description="transaction_id"
        :param: product_id : strict=true, description="product_id"
        :param: user_id : requirements="\d+", strict=true, description="the customer that is redeeming the specified offer"
        :param: language : strict=true, requirements="[a-z]+", default="en", description="Response language"
        :param: session_token : strict=true, description="Session token"
        :param: __i : strict=true, requirements="\d+", default="0", description="User id"
        :param: __sid : strict=true, requirements="\d+", default="0", description="Session id
        """
        self.user_id = self.request_args.get('user_id')
        self.offers = self.request_args.get('offer_id', '')
        self.quantities = list(self.request_args.get('quantity'))
        self.outlet_id = self.request_args.get('outlet_id')
        self.merchant_pin = self.request_args.get('merchant_pin', '')
        self.transaction_id = self.request_args.get('transaction_id', '')
        self.locale = self.request_args.get('language', '')
        self.product_id = self.request_args.get('product_id')
        self.locale = CommonHelpers.get_locale(self.locale)
        self.message_locale = CommonHelpers.get_locale_for_messaging(self.locale)
        self.is_shared = self.request_args.get('isshared', False)
        self.session_token = self.request_args.get('session_token')
        self.is_reattempt = self.request_args.get('is_reattempt')
        self.lng = self.request_args.get('lng')
        self.lat = self.request_args.get('lat')

    def load_customer_profile_and_session_data(self):
        """
        Load the customer-profile and customer session_data
        """
        self.customer_profile = self.customer_profile_class_instance.load_customer_profile_by_user_id(self.user_id)
        if self.customer_profile:
            self.customer = get_current_customer()
            if self.user_id != int(self.customer.get('customer_id')):
                self.send_response_flag = True
                self.response = self.message_class_instance.get_message_by_id(14, self.message_locale)
        else:
            self.send_response_flag = True
            self.response = 'No user found.'

    def initialize_class_attributes(self):
        """
        Initialize class atributes
        """
        self.customer_profile_class_instance = CustomerProfile(logger=self.logger)
        self.merchant_class_instance = MerchantRepository()
        self.redemption_class_instance = RedemptionRepository()
        self.offer_entity_class_instance = OfferSliceActiveRepository()
        self.message_class_instance = MessageRepository()
        self.outlet_class_instance = OutletRepository()
        self.offer_class_instance = OfferRepository()
        self.coordinate_repo_instance = CoordinateRepository()
        self.redemption_instance = None
        self.is_on_boarding = False
        self.merchant_ids = []

    def verify_duplicate_transaction(self):
        """
        checking duplication with respect to transaction_id
        :return: http-response with status-code 422 if transaction id already exist.
        """
        if self.transaction_id:
            self.redemption_instance = self.redemption_class_instance.get_reattempt_redemption_info(
                self.customer['customer_id'],
                self.transaction_id
            )
            if self.redemption_instance:
                self.logger.info(
                    'Duplicate redemption found with transaction_id:{transaction_id}.'.format(
                        transaction_id=self.transaction_id
                    )
                )
                self.status_code = 201
                self.send_response_flag = True
                self.response = {
                    'success': True,
                    'message': 'success',
                    'data': {
                        'referenceNo': {
                            'redemption_code': self.redemption_instance.get('code'),
                            'is_average_product_value_exceeded': False,
                            'redemption_id': self.redemption_instance.get('id')
                        }
                    }
                }

    def merchant_verification(self):
        """
        Verify that all offers belong to the same Merchant (i.e. we have one unique Merchant ID)
        :return: http-response with status-code 422 if multiple merchants.
        """
        if len(set(self.merchant_ids)) != 1:
            self.send_response_flag = True
            self.response = self.message_class_instance.get_message_by_id(31, self.message_locale)
            self.logger.info(self.response)

    def verify_merchant_pin(self):
        """
        Verify merchant-pin with user-pin
        :return: http-response with status-code 422 if pin does not matched.
        """
        # Get this Merchant Entity
        self.merchant_instance = self.merchant_class_instance.find(self.merchant_id)
        if self.merchant_instance and int(self.merchant_instance['pin']) != self.merchant_pin:
            self.send_response_flag = True
            self.response = self.message_class_instance.get_message_by_id(32, self.message_locale)
            self.logger.info(self.response)

    def initialize_offers_data(self):
        """
        Get offer_instance from db and check if its exist at given outlet.
        """
        self.offer = self.offer_entity_class_instance.find_by_id(self.offer_id, self.locale, self.customer, active=True)
        self.exists_at_outlet = self.outlet_class_instance.offer_exists_at_outlet(self.offer_id, self.outlet_id)

    def is_offer_exist(self):
        """
        Check if offer exist or not.
        :return: http-response with status-code 422 if offer does not exist.
        """
        if not self.offer:
            self.send_response_flag = True
            self.response = self.message_class_instance.get_message_by_id(25, self.message_locale)
            self.response = self.response.replace('XXX1', self.offer_id)
            self.logger.info(self.response)

    def is_offer_exist_at_outlet(self):
        """
        Verify is offer exist at outlet.
        :return: http-response with status-code 422 if offer does exist at outlet.
        """
        if not self.exists_at_outlet:
            self.send_response_flag = True
            self.response = self.message_class_instance.get_message_by_id(28, self.message_locale)
            self.response = self.response.replace('XXX1', str(self.offer_id))
            self.response = self.response.replace('XXX2', str(self.outlet_id))
            self.logger.info(self.response)

    def validate_offer_id(self):
        """
        Verify valid offer-id.
        :return: http-response with status-code 422 if offer_id is not provided in the request params.
        """
        if not self.offer_id:
            self.send_response_flag = True
            self.response = self.message_class_instance.get_message_by_id(30, self.message_locale)
            self.logger.info(self.response)

    def offers_provided(self):
        """
        Check offers are provided in request params.
        """
        return self.offers and len(self.offers) > 0

    def set_merchant_ids(self):
        """
        Set the merchant ids.
        """
        self.merchant_id = self.offer['merchant_id']
        self.merchant_ids.append(self.merchant_id)

    def process_offers(self):
        """
        process the offers send by user.
        """
        if self.offers_provided():
            for counter, offer_id in enumerate(self.offers):
                try:
                    self.quantities[counter]
                except IndexError:
                    self.quantities[counter] = 1
                self.offer_id = offer_id
                self.validate_offer_id()
                if self.is_send_response_flag_on():
                    return

                self.initialize_offers_data()
                self.is_offer_exist()
                if self.is_send_response_flag_on():
                    return

                self.is_offer_exist_at_outlet()
                if self.is_send_response_flag_on():
                    return
                self.set_merchant_ids()

    def initialize_redemption_data(self, outlet_id, product_id, company, conflict, quantity=1):
        """
        Initialize redemption_data
        """
        self.redemption_instance = dict()
        self.redemption_instance['date_created'] = datetime.datetime.now()
        self.redemption_instance['customer_id'] = self.customer['customer_id']
        self.redemption_instance['offer_id'] = self.offer_id
        self.redemption_instance['quantity'] = quantity
        self.redemption_instance['code'] = ''
        self.redemption_instance['is_shared'] = self.is_shared or False
        self.redemption_instance['outlet_id'] = outlet_id
        self.redemption_instance['transaction_id'] = self.transaction_id
        self.redemption_instance['product_id'] = product_id
        self.redemption_instance['session_token'] = self.session_token
        self.redemption_instance['is_onboarding'] = self.is_on_boarding
        self.redemption_instance['savings_estimate'] = self.offer_entity_instance.get('savings_estimate', 0)
        self.redemption_instance['company'] = company
        self.redemption_instance['root_code'] = self.root_code
        self.redemption_instance['conflict'] = conflict

    def set_company(self):
        """
        Set company-info.
        """
        self.company = 'slice'

    def set_rood_codes(self):
        """
        Get rood codes from db for redemption.
        """
        self.root_code = None
        self.rood_codes_from_offer = self.redemption_class_instance.get_root_code_by_offer_connect(self.offer_id)
        if self.rood_codes_from_offer:
            self.root_code = self.rood_codes_from_offer[0].get("root_code", '')

    def celery_tasks(self, connection=None, backup=False):
        process_records_task_id = 'task_process_records_{redemption_id}_{random}'.format(
            redemption_id=self.redemption_instance['id'],
            random=str(uuid.uuid4())[0:4]
        )
        sync_amazon_from_rackspace_task_id = 'task_sync_amazon_from_rackspace_{redemption_id}_{random}'.format(
            redemption_id=self.redemption_instance['id'],
            random=str(uuid.uuid4())[0:4]
        )
        celery_task_arguments = {'redemption_id': self.redemption_instance['id']}
        if connection and connection.connected:
            process_records.apply_async(
                kwargs=celery_task_arguments,
                connection=connection,
                task_id=process_records_task_id
            )
            sync_amazon_from_rackspace.apply_async(
                kwargs=celery_task_arguments,
                connection=connection,
                task_id=sync_amazon_from_rackspace_task_id
            )
            self.logger.info(
                'Celery task started for redemption_id:{redemption_id}, broker:{uri}, backup:{backup}.'.format(
                    redemption_id=self.redemption_instance.get('id'),
                    uri=connection.as_uri(),
                    backup=str(backup)
                )
            )
        else:
            message = 'Celery task does not started for redemption_id:{redemption_id}.' \
                      'broker:{uri}, backup:{backup}.'.format(redemption_id=self.redemption_instance.get('id'),
                                                              uri=connection.as_uri() if connection else '',
                                                              backup=str(backup)
                                                              )
            back_up_data = dict()
            back_up_data['tasks'] = []
            back_up_data['tasks'].append({
                'task_id': process_records_task_id,
                'kwargs': celery_task_arguments,
                'module': 'web_api.redemption.background_task.process_records',
                'status': False
            })
            back_up_data['tasks'].append({
                'task_id': sync_amazon_from_rackspace_task_id,
                'kwargs': celery_task_arguments,
                'module': 'web_api.redemption.background_task.sync_amazon_from_rackspace',
                'status': False
            })
            self.backup_celery_to_sql_lite(tasks=back_up_data['tasks'])
            self.logger.info(message)

    def insert_new_redemption(self):
        """
        Insert new redemption to db.
        """
        try:
            self.redemption_instance['id'] = self.redemption_class_instance.insert_redemption(
                redemption_data=self.redemption_instance
            )
            self.logger.info('redemption created with id:{id}'.format(id=self.redemption_instance['id']))
        except Exception:
            self.send_response_flag = True
            self.status_code = 500
            self.response = {"msg": "Internal Server Error"}
            self.logger.exception('Failed to save redemption')

    def set_redemption_code(self):
        """
        Set redemption_code.
        """
        self.redemption_instance['code'] = self.redemption_class_instance.generate_redemption_code(
            self.redemption_instance['id']
        )

    def update_redemption_code_to_db(self, table='redemption'):
        """
        Update the redemption db instance with new code.
        """
        try:
            self.redemption_update_fields = {'code': self.redemption_instance['code']}
            self.redemption_class_instance.update_redemption(
                redemption_update_fields=self.redemption_update_fields,
                redemption_id=self.redemption_instance['id'],
                table=table
            )
            self.logger.info('redemption updated with id:{id}'.format(id=self.redemption_instance['id']))
        except Exception:
            self.logger.exception('Failed to update redemption with db.')

    def post_process_redemption(self):
        """
        Update redemption data w.r.t customer.
        """
        self.insert_informatica_table_entry()

    def insert_informatica_table_entry(self):
        """
        Insert an db entry to informatica table for newly redemption.
        """
        self.informatica_data = {
            'id': self.redemption_instance['id'],
            'customer_id': self.redemption_instance['customer_id'],
            'session_token': self.session_token,
            'membership_code': self.customer.get('membership_code', ''),
            'quantity': self.redemption_instance['quantity'],
            'code': self.redemption_instance['code'],
            'date_created': self.redemption_instance['date_created'],
            'offer_sf_id': self.offer_entity_instance['sf_id'],
            'outlet_sf_id': self.outlet_instance.get('sf_id'),
            'merchant_sf_id': self.merchant_instance['sf_id'],
            'root_code': self.redemption_instance['root_code'],
            'processed': False,
            'company': self.company
        }
        InformaticaMobileRedemptionRepository().save(self.informatica_data)

    def build_redemption_response(self):
        self.redemption_response = {
            'redemption_code': self.redemption_instance.get('code'),
            'is_average_product_value_exceeded': False,
            'redemption_id': self.redemption_instance.get('id')
        }
        self.set_response({
            'data': {
                "referenceNo": self.redemption_response
            },
            'message': 'success',
            'success': True,
            'code': 0
        })
        self.status_code = 200

    def setting_logs_and_details(self, outet_id, redemption_id):
        """
        Inserts data in the coordinate
        """
        if self.lng and self.lat:
            data = {
                'lat': self.lat,
                'lng': self.lng,
                'outlet_id': outet_id,
                'redemption_id': redemption_id
            }
            self.coordinate_repo_instance.insert(data=data)

    def process_redemption(self):
        """
        Process redemption
        """
        if self.offers_provided():
            for counter, offer_id in enumerate(self.offers):
                self.offer_id = offer_id
                self.outlet_instance = self.outlet_class_instance.find(self.outlet_id)
                self.offer_entity_instance = self.offer_class_instance.find(self.offer_id)
                self.set_company()
                self.set_rood_codes()
                self.initialize_redemption_data(
                    outlet_id=self.outlet_instance.get('id'),
                    product_id=self.product_id,
                    company=self.company,
                    conflict=len(self.rood_codes_from_offer) > 1,
                    quantity=self.quantities[counter]
                )

                self.insert_new_redemption()
                if self.is_send_response_flag_on():
                    return

                self.set_redemption_code()
                self.update_redemption_code_to_db()
                self.setting_logs_and_details(self.outlet_instance.get('id'), self.redemption_instance['id'])
                self.post_process_redemption()
                self.build_redemption_response()

    def process_request(self):
        """
        Redeem an offer for a user.
        """
        self.initialize_class_attributes()
        self.load_customer_profile_and_session_data()
        if self.is_send_response_flag_on():
            return

        self.verify_duplicate_transaction()
        if self.is_send_response_flag_on():
            return

        self.process_offers()
        if self.is_send_response_flag_on():
            return

        self.merchant_verification()
        if self.is_send_response_flag_on():
            return

        self.verify_merchant_pin()
        if self.is_send_response_flag_on():
            return

        self.process_redemption()
