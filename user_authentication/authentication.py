import datetime

from dateutil.parser import parse
from flask import current_app, request
from flask_httpauth import HTTPBasicAuth
from flask_jwt_extended.view_decorators import _decode_jwt_from_request, _load_user, ctx_stack, wraps
from werkzeug.datastructures import Authorization
from werkzeug.exceptions import BadRequest, Forbidden

from common.common_helpers import CommonHelpers, get_current_date_time, get_pre_activated_apps, get_products_ids_list
from common.constants import SESSION_EXPIRED_STATUS_CODE, WHITE_LABEL_COMPANIES_WITH_SKIP_MODE
from common.models.ent_order import EntOrder
from repositories.dm_repositories.dm_devices_repo import DmDevicesRepository
from repositories.merchant_repo import MerchantRepository
from repositories.outlet_repo import OutletRepository
from repositories.product_ent_active_repo import ProductEntActiveRepository
from repositories.session_repo import CustomerProfile, SessionRepository
from repositories.translation_repo import MessageRepository
from repositories.v_65.family_members_repo import FamilyMemberRepository
from repositories.v_65.family_repo import FamilyRepository
from repositories.v_65.session_repo import SessionRepositoryV65
from repositories.wl_customer_repo import CustomerProfileWhiteLabel
from repositories.wl_session_repo import SessionRepositoryWhiteLabel
from user_authentication.dm_token_validation import dm_token_parser
from user_authentication.token_validation import token_parser


class EntertainerForbidden(Forbidden):
    """
    *403* `Forbidden`
    Raise if the user doesn't have the permission for the requested resource
    but was authenticated.
    """
    code = 801


def token_decorator(fn):
    @wraps(fn)
    def validator(self, *args, **kwargs):
        api_version = getattr(request, 'api_version', 64)
        if current_app.config.get('IS_OFFLINE', False):
            if api_version == 64:
                return token_required_offline_v64(fn)(self, *args, **kwargs)
            if 65 <= api_version < 612:
                return token_required_v65_offline(fn)(self, *args, **kwargs)
            if api_version >= 612:
                return token_required_v612_offline(fn)(self, *args, **kwargs)
        elif getattr(self, 'is_delivery_cashless', False):
            if current_app.config.get('BASIC_AUTH_ENABLED', False):
                return delivery_token_required(fn)(self, *args, **kwargs)
            elif current_app.config.get('JWT_TOKEN_ENABLED', False):
                return jwt_token_required_cashless(fn)(self, *args, **kwargs)
        elif getattr(self, 'is_wl', False):
            return token_required_white_label(fn)(self, *args, **kwargs)
        else:
            if api_version == 64:
                return token_required_v64(fn)(self, *args, **kwargs)
            if api_version >= 65 and api_version < 612:
                return token_required_v65(fn)(self, *args, **kwargs)
            if api_version >= 612:
                return token_required_v612(fn)(self, *args, **kwargs)
            return token_required(fn)(self, *args, **kwargs)
    return validator


def delivery_token_required(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)

            session_data = dict()
            session_data['device_id_db'] = 0
            session_data['outlet_db_id'] = 0
            session_data['merchant_db_id'] = 0
            request_args = dm_token_parser.parse_args()
            merchant_sf_id = request_args.get('merchant_sf_id', 0)
            device_id = request_args.get('device_id', 0)
            outlet_sf_id = request_args.get('outlet_sf_id', 0)

            if not merchant_sf_id:
                raise Forbidden(
                    'Request parameter merchant_sf_id is empty.'
                )

            data = dict()
            merchant_repo_instance = MerchantRepository()
            dm_device_repo_instance = DmDevicesRepository()
            outlet_repo_instance = OutletRepository()
            merchant_record = merchant_repo_instance.find_by_sf_id(merchant_sf_id)
            session_data['merchant_db_id'] = merchant_record.get('id', 0)
            if merchant_record:
                if outlet_sf_id:
                    outlet_record = outlet_repo_instance.find_by_sf_id(outlet_sf_id)
                    session_data['outlet_db_id'] = outlet_record.get('id', 0)
                    if not outlet_record:
                        raise Forbidden("No Outlet Found")
                    data['outlet_sf_id'] = outlet_sf_id
                    if outlet_record.get('merchant_id') != merchant_record.get('id'):
                        raise Forbidden("No outlet found for merchant with sf_id:{sf_id}".format(
                            sf_id=merchant_sf_id)
                        )

                data['device_id'] = device_id
                data['merchant_sf_id'] = merchant_sf_id
                if device_id:
                    valid_device = dm_device_repo_instance.find_device_by_filter(_filters=data)
                    if valid_device:
                        session_data['device_id_db'] = valid_device.get('id', 0)
                        if not valid_device.get('is_active', False):
                            raise Forbidden("Device is in-active.")
                    else:
                        raise Forbidden("No Device Found")
                session_data['merchant_sf_id'] = merchant_sf_id
                session_data['device_id'] = device_id
                session_data['outlet_sf_id'] = outlet_sf_id
                ctx_stack.top.session_data = session_data
                return fn(self, *args, **kwargs)
            else:
                raise Forbidden("No Merchant Found")
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper


def get_current_session_info():
    """
    Gets current merchant and device info
    """
    return getattr(ctx_stack.top, 'session_data', {})


def token_required(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid params before calling the actual view.
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)

            session_data = dict()
            request_args = token_parser.parse_args()
            user_id = 0
            session = None
            token = request_args.get('session_token', None)
            session_repo_instance = SessionRepository()
            if token:
                session = session_repo_instance.find_by_token(token)
                if not session:
                    raise Forbidden(
                        'A valid session token is required for this call. - {token} - {url}'.format(
                            token=token,
                            url=str(request.path)
                        )
                    )
                user_id = session.get('customer_id')

            if getattr(self, 'strict_token', False):
                if not token:
                    raise Forbidden(
                        'Request parameter session_token is empty.'
                    )
                if not user_id:
                    raise Forbidden(
                        'User identity is missing.'
                    )

            if token:
                if not user_id:
                    raise Forbidden(
                        'User identity is missing.'
                    )

                user_id = session.get('customer_id', 0)
                api_version = session_repo_instance.get_api_version(request)
                if api_version and session.get('company') != api_version:
                    session_repo_instance.update_api_version(
                        api_version=api_version,
                        session=session
                    )

                cached_on = session.get('date_cached', 0)
                if cached_on == 1 and getattr(self, 'refresh_session', False):
                    if user_id:
                        if 'consolidation' not in self.connections_names:
                            self.connections_names.append('consolidation')
                        CustomerProfile(logger=self.logger).refresh_customer_sessions(session.get('customer_id'))
                        session = session_repo_instance.find_by_token(token)
                session_data = session_repo_instance.get_data(session=session)
                session_data['id'] = session.get('id')
                session_data['session_token'] = session.get('session_token')
                try:
                    session_data['product_ids'] = get_products_ids_list(session.get('product_ids', []))
                except AttributeError:
                    session_data['product_ids'] = []
            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper


def token_required_offline(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid params before calling the actual view.
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            if not getattr(self, 'required_token', False):
                return fn(self, *args, **kwargs)

            session_data = dict()
            request_args = token_parser.parse_args()
            user_id = request_args.get('__i', 0)
            token = request_args.get('session_token', None)

            if getattr(self, 'strict_token', False):
                if not token:
                    raise Forbidden(
                        'Request parameter session_token is empty.'
                    )
                if not user_id:
                    raise Forbidden(
                        'User identity is missing.'
                    )

            if token:
                if 'default' not in self.connections_names:
                    self.connections_names.append('default')
                self.get_connections()
                session_repo_instance = SessionRepository()
                session = session_repo_instance.find_latest_token_by_user_id(user_id)
                if not session:
                    raise Forbidden(
                        'A valid session token is required for this call. - {token} - {url}'.format(
                            token=token,
                            url=str(request.path)
                        )
                    )
                session_data = session_repo_instance.get_data(session=session)
                session_data['id'] = session.get('id')
                session_data['session_token'] = session.get('session_token')
                try:
                    session_data['product_ids'] = get_products_ids_list(session.get('product_ids', []))
                except AttributeError:
                    session_data['product_ids'] = []
            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            self.close_connections()
    return wrapper


def token_required_v64(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid params before calling the actual view.
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)
            session_data = dict()
            request_args = token_parser.parse_args()
            user_id = 0
            session = None
            token = request_args.get('session_token', None)
            app_version = request_args.get('app_version', '')
            session_repo_instance = SessionRepository()
            if token:
                session = session_repo_instance.find_by_token(token)
                if not session:
                    raise Forbidden(
                        'A valid session token is required for this call. - {token} - {url}'.format(
                            token=token,
                            url=str(request.path)
                        )
                    )
                user_id = session.get('customer_id')

            if getattr(self, 'strict_token', False):
                if not token:
                    raise Forbidden(
                        'Request parameter session_token is empty.'
                    )
                if not user_id:
                    raise Forbidden(
                        'User identity is missing.'
                    )

            if token:
                if not user_id:
                    raise Forbidden(
                        'User identity is missing.'
                    )

                is_app_version_updated = False
                api_version = session_repo_instance.get_api_version(request)
                if app_version and session.get('app_version') != app_version:
                    is_app_version_updated = True
                    session_repo_instance.update_app_version(
                        app_version=app_version,
                        session=session
                    )

                if api_version and session.get('company') != api_version:
                    session_repo_instance.update_api_version(
                        api_version=api_version,
                        session=session
                    )
                customer_repo_instance = CustomerProfile(logger=self.logger)
                customer_profile = customer_repo_instance.load_customer_profile_by_user_id(user_id)
                if is_app_version_updated:
                    customer_profile.update(
                        customer_repo_instance.put_customer_in_trial_membership_if_qualifies_v64(
                            customer_id=user_id,
                            customer_profile=customer_profile
                        )
                    )

                cached_on = session.get('date_cached', 0)
                if (cached_on == 1 or not session.get('product_ids', [])) and getattr(self, 'refresh_session', False):
                    if user_id:
                        if 'consolidation' not in self.connections_names:
                            self.connections_names.append('consolidation')
                        customer_repo_instance.refresh_customer_sessions(session.get('customer_id'))
                        session = session_repo_instance.find_by_token(token)

                session_data['is_using_trial'] = False
                session_data['is_member_on_trail'] = False
                # trails_days_remaining = 0
                # if customer_profile.get('onboarding_startdate'):
                #     trails_days_remaining = customer_repo_instance.get_trial_remaining_days(
                #         customer_profile.get('onboarding_startdate')
                #     )
                is_member_on_trail = all([
                    customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_ONBOARDING,
                    customer_profile.get('onboarding_status') == 1,
                    # trails_days_remaining <= customer_repo_instance.TRIAL_DAYS + 1,
                    # trails_days_remaining > 0,
                    customer_profile.get('onboarding_redemptions_count', 0) < customer_repo_instance.TRAIL_REDEMPTIONS_LIMIT  # noqa
                ])

                if is_member_on_trail:
                    session_data['is_using_trial'] = True
                    session_data['is_member_on_trail'] = True
                # trying to stop the query which is creating row dead-lock for updating ent_customer_profile
                # commented due to migration of system from master-master to master-slave
                # if not is_member_on_trail and customer_profile.get('new_member_group') not in [
                #     customer_repo_instance.MEMBERSTATUS_MEMBER,
                #     customer_repo_instance.MEMBERSTATUS_REPROSPECT
                # ]:
                #     customer_profile.update(customer_repo_instance.update_trial_date(customer_id=user_id))

                session_data['id'] = session.get('id')
                session_data['company'] = session.get('company')
                session_data['customer_id'] = user_id
                session_data['device_key'] = request_args.get('device_key', None)
                session_data['session_token'] = session.get('session_token')
                session_data['onboarding_redemption_limit'] = customer_profile.get('onboarding_redemption_limit')
                session_data['membership_code'] = customer_profile.get('membership_code')
                session_data['member_type'] = customer_repo_instance.get_member_type(
                    customer_profile.get('new_member_group')
                )
                session_data['member_type_id'] = customer_profile.get('new_member_group')
                session_data['onboarding_redemptions_count'] = customer_profile.get('onboarding_redemptions_count', 0)
                try:
                    session_data['product_ids'] = get_products_ids_list(session.get('product_ids', []))
                except AttributeError:
                    session_data['product_ids'] = []
            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper


def token_required_v65(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid params before calling the actual view.
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)

            session_data = dict()
            request_args = token_parser.parse_args()
            user_id = 0
            session = None
            token = request_args.get('session_token', None)
            app_version = request_args.get('app_version', '')
            session_repo_instance = SessionRepositoryV65()
            family_member_repo = FamilyMemberRepository()
            family_repo = FamilyRepository()
            if token:
                session = session_repo_instance.find_by_token(token)
                if not session:
                    data = 'Session has been expired.'
                    self.status_code = 403
                    self.code = 403
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)
                try:
                    session_api_version = int(''.join(filter(str.isdigit, session.get('company', ''))))
                except Exception:
                    session_api_version = 0
                try:
                    if session_api_version < 65:
                        session_repo_instance.remove_session(session_id=session.get('id'))
                        data = "You are logged out.Sign in from latest app."
                        self.status_code = 403
                        self.code = 403
                        self.send_response_flag = True
                        return self.send_response(data, self.status_code)
                except Exception:
                    raise Forbidden
                user_id = session.get('customer_id')

            if getattr(self, 'strict_token', False):
                if not token:
                    data = 'Session has been expired.'
                    self.status_code = 403
                    self.code = 403
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)
                if not user_id:
                    data = 'User identity is missing.'
                    self.status_code = 403
                    self.code = 403
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)

            if token:
                if not user_id:
                    data = 'User identity is missing.'
                    self.status_code = 403
                    self.code = 403
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)

                is_app_version_updated = False
                api_version = session_repo_instance.get_api_version(request)
                if app_version and session.get('app_version') != app_version:
                    session_repo_instance.update_app_version(
                        app_version=app_version,
                        session=session
                    )

                if api_version and session.get('company') != api_version:
                    is_app_version_updated = True
                    session_repo_instance.update_api_version(
                        api_version=api_version,
                        session=session
                    )
                customer_repo_instance = CustomerProfile(logger=self.logger)
                session_data['user_in_family_ever'] = False
                customer_profile = customer_repo_instance.load_customer_profile_by_user_id(user_id)
                user = None
                if customer_profile:
                    user = customer_repo_instance.load_customer_by_id(customer_profile.get('user_id'))
                    if user and user.get('status', -1) == customer_repo_instance.STATUS_BLACKLISTED:
                        data = MessageRepository.user_blacklisted
                        self.status_code = 403
                        self.code = 403
                        self.send_response_flag = True
                        return self.send_response(data, self.status_code)
                if getattr(self, 'family_authentication', False):
                    if is_app_version_updated:
                        user_in_family_ever = family_member_repo.find_family_member(
                            filters={'user_id': user_id},
                            not_equal_filters={'member_since': None}
                        )
                        session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                        if not session_data['user_in_family_ever']:
                            customer_profile.update(
                                customer_repo_instance.put_customer_in_trial_membership_if_qualifies_v64(
                                    customer_id=user_id,
                                    customer_profile=customer_profile
                                )
                            )
                # As now we are blocking all users on register for email validation

                # Check for user email if 24 hours passed and user still not verified the email
                # user_create_time = customer_profile.get('create_time')
                # user_create_time = user_create_time + datetime.timedelta(hours=24)
                # current_time = datetime.datetime.now().replace(microsecond=0)
                # if current_time > user_create_time:

                # Disable Email verification on request by Sir Imtiaz
                # if not user:
                #     user = customer_repo_instance.load_customer_by_id(customer_profile.get('user_id'))
                # from repositories.customer_social_acc_repo import CustomerSocialAccRepository
                # social_customer = CustomerSocialAccRepository().is_exist_old(customer_id=user.get('id'))
                # if not social_customer:
                #     if not user.get('is_email_verified'):
                #         data = {
                #             "resend_invite_section": {
                #                 "title": "Verify your email",
                #                 "message": "Looks like you failed to verify your e-mail address. Please verify "
                #                            "your e-mail address or contact customer services at "
                #                            "customerservice@theentertainerme.com for further help.",
                #                 'email': user.get('email'),
                #                 "button_text": "RESEND"
                #             }
                #         }
                #         data['message'] = data['resend_invite_section']['message']
                #         self.status_code = 403
                #         self.code = 403
                #         self.send_response_flag = True
                #         return self.send_response(data, self.status_code)

                cached_on = session.get('date_cached', 0)
                if cached_on == 1 and getattr(self, 'refresh_session', False):
                    if user_id:
                        if 'consolidation' not in self.connections_names:
                            self.connections_names.append('consolidation')
                        customer_repo_instance.refresh_customer_sessions(session.get('customer_id'))
                        session = session_repo_instance.find_by_token(token)

                session_data['id'] = session.get('id')
                session_data['customer_id'] = user_id
                session_data['app_version'] = app_version
                session_data['company'] = session.get('company')
                session_data['device_key'] = request_args.get('device_key', None)
                session_data['onboarding_redemption_limit'] = customer_profile.get('onboarding_redemption_limit', 0)
                session_data['membership_code'] = customer_profile.get('membership_code')
                session_data['member_type'] = customer_repo_instance.get_member_type(
                    customer_profile.get('new_member_group')
                )
                session_data['member_type_id'] = customer_profile.get('new_member_group')
                session_data['membership_sub_group'] = customer_profile.get(
                    'membership_sub_group',
                    customer_repo_instance.INACTIVE_MEMBERSHIP_SUB_GROUP
                )
                session_data['session_token'] = session.get('session_token')
                session_data['is_member_on_trail'] = False
                session_data['is_using_trial'] = False
                session_data['onboarding_redemptions_count'] = customer_profile.get('onboarding_redemptions_count', 0)
                session_data['user_id'] = user_id
                session_data['email'] = customer_profile.get('email')
                session_data['firstname'] = customer_profile.get('firstname')
                session_data['lastname'] = customer_profile.get('lastname')
                session_data['is_primary'] = False
                session_data['is_user_in_family'] = False
                session_data['family_is_active'] = False
                session_data['family_info'] = {}
                session_data['family_member_info'] = {}
                session_data['primary_member_info'] = {}
                session_data['cheers_product_ids'] = []
                session_data['on_grace_period'] = False
                session_data['is_using_extended_trail'] = False
                session_data['extended_trail_ids'] = []
                session_data['has_epc_order'] = False

                session_data['subscription_expiry'] = CommonHelpers.process_stringified_json(
                    session.get('subscription_expiry'), default={}
                )
                if session.get('extended_trail_group_ids'):
                    session_data['is_using_extended_trail'] = True
                    try:
                        session_data['extended_trail_ids'] = list(
                            filter(None, session.get('extended_trail_group_ids', '').split(','))
                        )
                        if (
                            customer_profile.get('onboarding_enddate') < datetime.datetime.now() and
                            customer_profile.get('onboarding_status') == self.ONBOARDING_INPROGRESS
                        ):
                            session_repo_instance.refresh_session(
                                session_token=token,
                                app_version=app_version,
                                company=session.get('company')
                            )
                    except Exception:
                        pass

                session_data['primary_member_membership_status'] = customer_repo_instance.MEMBERSTATUS_PROSPTECT

                if getattr(self, 'family_authentication', False):
                    family_member_details = family_member_repo.find_family_member(
                        filters={'user_id': user_id, 'status': family_member_repo.ACCEPTED, 'is_active': 1}
                    )
                    session_data['family_member_info'] = family_member_details
                    if family_member_details:
                        family_information = family_repo.find_family(
                            filters={'id': family_member_details.get('family_id', 0)}
                        )
                        session_data['family_info'] = family_information
                        if family_information:
                            primary_user_profile = customer_repo_instance.load_customer_profile_and_user_info_by_id(
                                customer_ids=family_information.get('user_id', 0),
                                single_profile=True,
                                check_black_list_user_status=False
                            )
                            if (
                                primary_user_profile and primary_user_profile.get('status', -1) ==
                                customer_repo_instance.STATUS_BLACKLISTED
                            ):
                                session_data['family_is_active'] = False
                                session_data['is_user_in_family'] = False
                            else:
                                session_data['family_is_active'] = family_information.get('status') in [
                                    family_repo.ACTIVE, family_repo.ON_GRACE_PERIOD
                                ]
                                session_data['is_user_in_family'] = True
                                session_data['membership_sub_group'] = primary_user_profile.get(
                                    'membership_sub_group',
                                    customer_repo_instance.INACTIVE_MEMBERSHIP_SUB_GROUP
                                )
                                session_data['is_primary'] = bool(family_member_details.get('is_primary', False))

                    if customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_MEMBER:
                        session_data['is_primary'] = True
                        session_data['primary_member_membership_status'] = customer_profile.get('new_member_group')

                    if session_data['is_primary']:
                        session_data['primary_member_info'] = family_member_details

                    if not session_data['is_user_in_family']:
                        try:
                            session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                        except NameError:
                            user_in_family_ever = family_member_repo.find_family_member(
                                filters={'user_id': user_id},
                                not_equal_filters={'member_since': None}
                            )
                        session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                        if not session_data['user_in_family_ever']:
                            # trails_days_remaining = 0
                            # if customer_profile.get('onboarding_startdate'):
                            #     trails_days_remaining = customer_repo_instance.get_trial_remaining_days(
                            #         customer_profile.get('onboarding_startdate')
                            #     )
                            session_data['is_using_trial'] = customer_repo_instance.is_customer_on_trail(
                                customer_profile=customer_profile
                            )
                            session_data['is_member_on_trail'] = session_data['is_using_trial']
                        # trying to stop the query which is creating row dead-lock for updating ent_customer_profile
                        # commented due to migration of system from master-master to master-slave
                        # if not session_data['is_member_on_trail'] and customer_profile.get('new_member_group') not in [
                        #     customer_repo_instance.MEMBERSTATUS_MEMBER,
                        #     customer_repo_instance.MEMBERSTATUS_REPROSPECT
                        # ]:
                        #     customer_profile.update(customer_repo_instance.update_trial_date(customer_id=user_id))

                    session_data['product_ids'] = []
                    session_data['owns_cheer_products'] = False
                    try:
                        if session_data['is_primary']:
                            session_data['product_ids'] = get_products_ids_list(session.get('product_ids', []))
                        elif session_data['is_user_in_family'] and not session_data['is_primary']:
                            # if user is some family and not primary
                            primary_family_user_information = family_member_repo.find_family_member(
                                filters={
                                    'is_primary': 1,
                                    'family_id': session_data['family_info'].get('id', 0),
                                    'is_active': 1,
                                    'user_id': session_data['family_info'].get('user_id', 0)
                                }
                            )
                            if primary_family_user_information:
                                session_data['primary_member_info'] = primary_family_user_information
                                primary_user_session_data = session_repo_instance.find_latest_token_by_user_id(
                                    primary_family_user_information.get('user_id', 0),
                                    isactive=False
                                )
                                session_data['product_ids'] = primary_user_session_data.get('product_ids', '').split(',')
                                session_data['subscription_expiry'] = CommonHelpers.process_stringified_json(
                                    primary_user_session_data.get('subscription_expiry'), default={}
                                )
                                cheers_product_ids = ProductEntActiveRepository().get_cheers_product_by_product_ids(
                                    session_data['product_ids'], convert_to_string=True
                                )
                                if cheers_product_ids:
                                    session_data['owns_cheer_products'] = True
                                if not session_data['family_member_info'].get('is_cheers_to_include', False):
                                    session_data['product_ids'] = [_id for _id in session_data['product_ids']
                                                                   if _id not in cheers_product_ids]
                                    session_data['cheers_product_ids'] = cheers_product_ids
                    except AttributeError:
                        session_data['product_ids'] = []

                    if session_data['family_info'].get('status') == family_repo.ACTIVE:
                        if all([
                            session_data['is_user_in_family'],
                            session_data['family_is_active'],
                            session_data['primary_member_info'].get('is_primary', False)
                        ]):
                            primary_customer_profile = customer_repo_instance.load_customer_profile_by_id(
                                session_data['primary_member_info'].get('user_id')
                            )
                            session_data['primary_member_membership_status'] = primary_customer_profile.get('new_member_group')  # noqa : E501
                            if (
                                primary_customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_REPROSPECT  # noqa : E501
                            ):
                                family_data = {'status': family_repo.ON_GRACE_PERIOD}
                                session_data['family_info'].update(
                                    family_repo.update_family(
                                        filters={'id': session_data['family_info'].get('id')},
                                        data=family_data
                                    )
                                )

                    session_data['on_grace_period'] = (
                        session_data['family_info'].get('status') == family_repo.ON_GRACE_PERIOD
                    )
                    session_data['family_expired'] = (
                        session_data['family_info'].get('status') == family_repo.EXPIRED
                    )
                    family_info_update_date = session_data['family_info'].get('date_updated')
                    if isinstance(family_info_update_date, str):
                        family_info_update_date = parse(family_info_update_date)
                    if session_data['family_expired']:
                        family_repo.check_family_expired_and_grace_period(session_data=session_data)
                    if session_data['on_grace_period']:
                        if all([
                            session_data['is_user_in_family'],
                            session_data['family_is_active'],
                            session_data['primary_member_info'].get('is_primary', False),
                            (datetime.datetime.now() - family_info_update_date).days > family_repo.GRACE_PERIOD_EXPIRED_DAYS_LIMIT  # noqa : E501
                        ]):
                            family_repo.check_family_expired_and_grace_period(session_data=session_data)
                            primary_customer_profile = customer_repo_instance.load_customer_profile_by_id(
                                session_data['primary_member_info'].get('user_id')
                            )
                            session_data['primary_member_membership_status'] = primary_customer_profile.get('new_member_group')  # noqa : E501
                            if (
                                primary_customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_REPROSPECT  # noqa : E501
                            ):
                                family_data = {'status': family_repo.EXPIRED, 'is_active': 0}
                                session_data['family_info'].update(
                                    family_repo.update_family(
                                        filters={'id': session_data['family_info'].get('id')},
                                        data=family_data
                                    )
                                )
                                family_member_repo.update_member(
                                    filters={'family_id': session_data['family_info'].get('id')},
                                    data={'is_active': 0}
                                )
                                session_data['family_member_info']['is_active'] = 0
                                session_data['primary_member_info']['is_active'] = 0
                                session_data['is_user_in_family'] = False
                                session_data['family_is_active'] = False
                else:
                    session_data['product_ids'] = []
                    session_data['owns_cheer_products'] = False

                epc_order = EntOrder.get_order(is_epc=True, user_id=user_id)
                if epc_order:
                    session_data['has_epc_order'] = True

            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper


def token_required_v612(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid params before calling the actual view.
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)

            session_data = dict()
            request_args = token_parser.parse_args()
            user_id = 0
            session = None
            token = request_args.get('session_token', None)
            app_version = request_args.get('app_version', '')
            session_repo_instance = SessionRepositoryV65()
            family_member_repo = FamilyMemberRepository()
            family_repo = FamilyRepository()
            if token:
                session = session_repo_instance.find_by_token(token)
                if not session:
                    data = 'Session has been expired.'
                    self.status_code = SESSION_EXPIRED_STATUS_CODE
                    self.code = SESSION_EXPIRED_STATUS_CODE
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)
                try:
                    session_api_version = int(''.join(filter(str.isdigit, session.get('company', ''))))
                except Exception:
                    session_api_version = 0
                try:
                    if session_api_version < 65:
                        session_repo_instance.remove_session(session_id=session.get('id'))
                        data = "You are logged out.Sign in from latest app."
                        self.status_code = SESSION_EXPIRED_STATUS_CODE
                        self.code = SESSION_EXPIRED_STATUS_CODE
                        self.send_response_flag = True
                        return self.send_response(data, self.status_code)
                except Exception:
                    raise EntertainerForbidden
                user_id = session.get('customer_id')

            if getattr(self, 'strict_token', False):
                if not token:
                    data = 'Session has been expired.'
                    self.status_code = SESSION_EXPIRED_STATUS_CODE
                    self.code = SESSION_EXPIRED_STATUS_CODE
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)
                if not user_id:
                    data = 'User identity is missing.'
                    self.status_code = SESSION_EXPIRED_STATUS_CODE
                    self.code = SESSION_EXPIRED_STATUS_CODE
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)

            if token:
                if not user_id:
                    data = 'User identity is missing.'
                    self.status_code = SESSION_EXPIRED_STATUS_CODE
                    self.code = SESSION_EXPIRED_STATUS_CODE
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)

                is_app_version_updated = False
                api_version = session_repo_instance.get_api_version(request)
                if app_version and session.get('app_version') != app_version:
                    session_repo_instance.update_app_version(
                        app_version=app_version,
                        session=session
                    )

                if api_version and session.get('company') != api_version:
                    is_app_version_updated = True
                    session_repo_instance.update_api_version(
                        api_version=api_version,
                        session=session
                    )
                customer_repo_instance = CustomerProfile(logger=self.logger)
                session_data['user_in_family_ever'] = False
                customer_profile = customer_repo_instance.load_customer_profile_by_user_id(user_id)
                user = None
                if customer_profile:
                    user = customer_repo_instance.load_customer_by_id(customer_profile.get('user_id'))
                    if user and user.get('status', -1) == customer_repo_instance.STATUS_BLACKLISTED:
                        data = MessageRepository.user_blacklisted
                        self.status_code = SESSION_EXPIRED_STATUS_CODE
                        self.code = SESSION_EXPIRED_STATUS_CODE
                        self.send_response_flag = True
                        return self.send_response(data, self.status_code)
                if getattr(self, 'family_authentication', False):
                    if is_app_version_updated:
                        user_in_family_ever = family_member_repo.find_family_member(
                            filters={'user_id': user_id},
                            not_equal_filters={'member_since': None}
                        )
                        session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                        if not session_data['user_in_family_ever']:
                            customer_profile.update(
                                customer_repo_instance.put_customer_in_trial_membership_if_qualifies_v64(
                                    customer_id=user_id,
                                    customer_profile=customer_profile
                                )
                            )
                # As now we are blocking all users on register for email validation

                # Check for user email if 24 hours passed and user still not verified the email
                # user_create_time = customer_profile.get('create_time')
                # user_create_time = user_create_time + datetime.timedelta(hours=24)
                # current_time = datetime.datetime.now().replace(microsecond=0)
                # if current_time > user_create_time:

                # Disable Email verification on request by Sir Imtiaz
                # if not user:
                #     user = customer_repo_instance.load_customer_by_id(customer_profile.get('user_id'))
                # from repositories.customer_social_acc_repo import CustomerSocialAccRepository
                # social_customer = CustomerSocialAccRepository().is_exist_old(customer_id=user.get('id'))
                # if not social_customer:
                #     if not user.get('is_email_verified'):
                #         data = {
                #             "resend_invite_section": {
                #                 "title": "Verify your email",
                #                 "message": "Looks like you failed to verify your e-mail address. Please verify "
                #                            "your e-mail address or contact customer services at "
                #                            "customerservice@theentertainerme.com for further help.",
                #                 'email': user.get('email'),
                #                 "button_text": "RESEND"
                #             }
                #         }
                #         data['message'] = data['resend_invite_section']['message']
                #         self.status_code = SESSION_EXPIRED_STATUS_CODE
                #         self.code = SESSION_EXPIRED_STATUS_CODE
                #         self.send_response_flag = True
                #         return self.send_response(data, self.status_code)

                cached_on = session.get('date_cached', 0)
                if cached_on == 1 and getattr(self, 'refresh_session', False):
                    if user_id:
                        if 'consolidation' not in self.connections_names:
                            self.connections_names.append('consolidation')
                        customer_repo_instance.refresh_customer_sessions(session.get('customer_id'))
                        session = session_repo_instance.find_by_token(token)

                session_data['id'] = session.get('id')
                session_data['company'] = session.get('company')
                session_data['customer_id'] = user_id
                session_data['device_key'] = request_args.get('device_key', None)
                session_data['onboarding_redemption_limit'] = customer_profile.get('onboarding_redemption_limit', 0)
                session_data['membership_code'] = customer_profile.get('membership_code')
                session_data['member_type'] = customer_repo_instance.get_member_type(
                    customer_profile.get('new_member_group')
                )
                session_data['member_type_id'] = customer_profile.get('new_member_group')
                session_data['session_token'] = session.get('session_token')
                session_data['is_member_on_trail'] = False
                session_data['is_using_trial'] = False
                session_data['onboarding_redemptions_count'] = customer_profile.get('onboarding_redemptions_count', 0)
                session_data['user_id'] = user_id
                session_data['email'] = customer_profile.get('email')
                session_data['firstname'] = customer_profile.get('firstname')
                session_data['lastname'] = customer_profile.get('lastname')
                session_data['is_primary'] = False
                session_data['is_user_in_family'] = False
                session_data['family_is_active'] = False
                session_data['family_info'] = {}
                session_data['family_member_info'] = {}
                session_data['primary_member_info'] = {}
                session_data['cheers_product_ids'] = []
                session_data['on_grace_period'] = False
                session_data['is_using_extended_trail'] = False
                session_data['extended_trail_ids'] = []
                session_data['has_epc_order'] = False
                session_data['subscription_expiry'] = CommonHelpers.process_stringified_json(
                    session.get('subscription_expiry'), default={}
                )
                if session.get('extended_trail_group_ids'):
                    session_data['is_using_extended_trail'] = True
                    try:
                        session_data['extended_trail_ids'] = list(
                            filter(None, session.get('extended_trail_group_ids', '').split(','))
                        )
                        if (
                                customer_profile.get('onboarding_enddate') < datetime.datetime.now() and
                                customer_profile.get('onboarding_status') == self.ONBOARDING_INPROGRESS
                        ):
                            session_repo_instance.refresh_session(
                                session_token=token,
                                app_version=app_version,
                                company=session.get('company')
                            )
                    except Exception:
                        pass

                session_data['primary_member_membership_status'] = customer_repo_instance.MEMBERSTATUS_PROSPTECT

                if getattr(self, 'family_authentication', False):
                    family_member_details = family_member_repo.find_family_member(
                        filters={'user_id': user_id, 'status': family_member_repo.ACCEPTED, 'is_active': 1}
                    )
                    session_data['family_member_info'] = family_member_details
                    if family_member_details:
                        family_information = family_repo.find_family(
                            filters={'id': family_member_details.get('family_id', 0)}
                        )
                        session_data['family_info'] = family_information
                        if family_information:
                            primary_user_profile = customer_repo_instance.load_customer_by_id(
                                family_information.get('user_id', 0)
                            )

                            if (
                                primary_user_profile and primary_user_profile.get('status', -1) ==
                                customer_repo_instance.STATUS_BLACKLISTED
                            ):
                                session_data['family_is_active'] = False
                                session_data['is_user_in_family'] = False
                            else:
                                session_data['family_is_active'] = family_information.get('status') in [
                                    family_repo.ACTIVE, family_repo.ON_GRACE_PERIOD
                                ]
                                session_data['is_user_in_family'] = True
                                session_data['is_primary'] = bool(family_member_details.get('is_primary', False))

                    if customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_MEMBER:
                        session_data['is_primary'] = True
                        session_data['primary_member_membership_status'] = customer_profile.get('new_member_group')

                    if session_data['is_primary']:
                        session_data['primary_member_info'] = family_member_details

                    if not session_data['is_user_in_family']:
                        try:
                            session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                        except NameError:
                            user_in_family_ever = family_member_repo.find_family_member(
                                filters={'user_id': user_id},
                                not_equal_filters={'member_since': None}
                            )
                        session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                        if not session_data['user_in_family_ever']:
                            # trails_days_remaining = 0
                            # if customer_profile.get('onboarding_startdate'):
                            #     trails_days_remaining = customer_repo_instance.get_trial_remaining_days(
                            #         customer_profile.get('onboarding_startdate')
                            #     )
                            session_data['is_using_trial'] = customer_repo_instance.is_customer_on_trail(
                                customer_profile=customer_profile
                            )
                            session_data['is_member_on_trail'] = session_data['is_using_trial']
                        # trying to stop the query which is creating row dead-lock for updating ent_customer_profile
                        # commented due to migration of system from master-master to master-slave
                        # if not session_data['is_member_on_trail'] and customer_profile.get('new_member_group') not in [
                        #     customer_repo_instance.MEMBERSTATUS_MEMBER,
                        #     customer_repo_instance.MEMBERSTATUS_REPROSPECT
                        # ]:
                        #     customer_profile.update(customer_repo_instance.update_trial_date(customer_id=user_id))

                    session_data['product_ids'] = []
                    session_data['owns_cheer_products'] = False
                    try:
                        if session_data['is_primary']:
                            session_data['product_ids'] = get_products_ids_list(session.get('product_ids', []))
                        elif session_data['is_user_in_family'] and not session_data['is_primary']:
                            # if user is some family and not primary
                            primary_family_user_information = family_member_repo.find_family_member(
                                filters={
                                    'is_primary': 1,
                                    'family_id': session_data['family_info'].get('id', 0),
                                    'is_active': 1,
                                    'user_id': session_data['family_info'].get('user_id', 0)
                                }
                            )
                            if primary_family_user_information:
                                session_data['primary_member_info'] = primary_family_user_information
                                primary_user_session_data = session_repo_instance.find_latest_token_by_user_id(
                                    primary_family_user_information.get('user_id', 0),
                                    isactive=False
                                )
                                session_data['product_ids'] = primary_user_session_data.get('product_ids', '').split(',')
                                session_data['subscription_expiry'] = CommonHelpers.process_stringified_json(
                                    primary_user_session_data.get('subscription_expiry'), default={}
                                )
                                cheers_product_ids = ProductEntActiveRepository().get_cheers_product_by_product_ids(
                                    session_data['product_ids'], convert_to_string=True
                                )
                                if cheers_product_ids:
                                    session_data['owns_cheer_products'] = True
                                if not session_data['family_member_info'].get('is_cheers_to_include', False):
                                    session_data['product_ids'] = [_id for _id in session_data['product_ids']
                                                                   if _id not in cheers_product_ids]
                                    session_data['cheers_product_ids'] = cheers_product_ids
                    except AttributeError:
                        session_data['product_ids'] = []

                    if session_data['family_info'].get('status') == family_repo.ACTIVE:
                        if all([
                            session_data['is_user_in_family'],
                            session_data['family_is_active'],
                            session_data['primary_member_info'].get('is_primary', False)
                        ]):
                            primary_customer_profile = customer_repo_instance.load_customer_profile_by_id(
                                session_data['primary_member_info'].get('user_id')
                            )
                            session_data['primary_member_membership_status'] = primary_customer_profile.get('new_member_group')  # noqa : E501
                            if (
                                primary_customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_REPROSPECT  # noqa : E501
                            ):
                                family_data = {'status': family_repo.ON_GRACE_PERIOD}
                                session_data['family_info'].update(
                                    family_repo.update_family(
                                        filters={'id': session_data['family_info'].get('id')},
                                        data=family_data
                                    )
                                )

                    session_data['on_grace_period'] = (
                        session_data['family_info'].get('status') == family_repo.ON_GRACE_PERIOD
                    )
                    session_data['family_expired'] = (
                        session_data['family_info'].get('status') == family_repo.EXPIRED
                    )
                    family_info_update_date = session_data['family_info'].get('date_updated')
                    if isinstance(family_info_update_date, str):
                        family_info_update_date = parse(family_info_update_date)
                    if session_data['family_expired']:
                        family_repo.check_family_expired_and_grace_period(session_data=session_data)
                    if session_data['on_grace_period']:
                        if all([
                            session_data['is_user_in_family'],
                            session_data['family_is_active'],
                            session_data['primary_member_info'].get('is_primary', False),
                            (datetime.datetime.now() - family_info_update_date).days > family_repo.GRACE_PERIOD_EXPIRED_DAYS_LIMIT  # noqa : E501
                        ]):
                            family_repo.check_family_expired_and_grace_period(session_data=session_data)
                            primary_customer_profile = customer_repo_instance.load_customer_profile_by_id(
                                session_data['primary_member_info'].get('user_id')
                            )
                            session_data['primary_member_membership_status'] = primary_customer_profile.get('new_member_group')  # noqa : E501
                            if (
                                primary_customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_REPROSPECT  # noqa : E501
                            ):
                                family_data = {'status': family_repo.EXPIRED, 'is_active': 0}
                                session_data['family_info'].update(
                                    family_repo.update_family(
                                        filters={'id': session_data['family_info'].get('id')},
                                        data=family_data
                                    )
                                )
                                family_member_repo.update_member(
                                    filters={'family_id': session_data['family_info'].get('id')},
                                    data={'is_active': 0}
                                )
                                session_data['family_member_info']['is_active'] = 0
                                session_data['primary_member_info']['is_active'] = 0
                                session_data['is_user_in_family'] = False
                                session_data['family_is_active'] = False
                else:
                    session_data['product_ids'] = []
                    session_data['owns_cheer_products'] = False
                epc_order = EntOrder.get_order(is_epc=True, user_id=user_id)
                if epc_order:
                    session_data['has_epc_order'] = True

            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper


def token_required_offline_v64(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid params before calling the actual view.
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        try:
            if not getattr(self, 'required_token', False):
                return fn(self, *args, **kwargs)

            session_data = dict()
            request_args = token_parser.parse_args()
            user_id = 0
            session = None
            token = request_args.get('session_token', None)
            session_repo_instance = SessionRepository()
            if token:
                session = session_repo_instance.find_by_token(token)
                if not session:
                    raise Forbidden(
                        'A valid session token is required for this call. - {token} - {url}'.format(
                            token=token,
                            url=str(request.path)
                        )
                    )
                user_id = session.get('customer_id')

            if getattr(self, 'strict_token', False):
                if not token:
                    raise Forbidden(
                        'Request parameter session_token is empty.'
                    )
                if not user_id:
                    raise Forbidden(
                        'User identity is missing.'
                    )

            if token:
                if not user_id:
                    raise Forbidden(
                        'User identity is missing.'
                    )
                customer_repo_instance = CustomerProfile(logger=self.logger)
                customer_profile = customer_repo_instance.load_customer_profile_by_user_id(user_id)
                session_data['id'] = session.get('id')
                session_data['company'] = session.get('company')
                session_data['customer_id'] = user_id
                session_data['session_token'] = session.get('session_token')
                session_data['onboarding_redemption_limit'] = customer_profile.get('onboarding_redemption_limit')
                session_data['membership_code'] = customer_profile.get('membership_code')
                session_data['member_type'] = customer_repo_instance.get_member_type(
                    customer_profile.get('new_member_group')
                )
                session_data['member_type_id'] = customer_profile.get('new_member_group')
                session_data['onboarding_redemptions_count'] = customer_profile.get('onboarding_redemptions_count', 0)
                session_data['is_using_trial'] = False
                session_data['is_member_on_trail'] = False

                # trails_days_remaining = 0
                # if customer_profile.get('onboarding_startdate'):
                #     trails_days_remaining = customer_repo_instance.get_trial_remaining_days(
                #         customer_profile.get('onboarding_startdate')
                #     )
                is_member_on_trail = all([
                    customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_ONBOARDING,
                    customer_profile.get('onboarding_status') == 1,
                    # trails_days_remaining <= customer_repo_instance.TRIAL_DAYS + 1,
                    # trails_days_remaining > 0,
                    customer_profile.get('onboarding_redemptions_count', 0) < customer_repo_instance.TRAIL_REDEMPTIONS_LIMIT  # noqa : E501
                ])

                if is_member_on_trail:
                    session_data['is_using_trial'] = True
                    session_data['is_member_on_trail'] = True

                if not is_member_on_trail and customer_profile.get('new_member_group') not in [
                    customer_repo_instance.MEMBERSTATUS_MEMBER,
                    customer_repo_instance.MEMBERSTATUS_REPROSPECT
                ]:
                    changes = dict()
                    changes['onboarding_status'] = 2
                    changes['member_group'] = CustomerProfile.MEMBERSTATUS_PROSPTECT
                    changes['new_member_group'] = CustomerProfile.MEMBERSTATUS_PROSPTECT
                    changes['onboarding_status'] = CustomerProfile.ONBOARDING_FINISHED
                    changes['onboarding_enddate'] = get_current_date_time()
                    changes['member_type'] = customer_repo_instance.get_member_type(
                        customer_profile.get('new_member_group')
                    )
                    customer_profile.update(changes)
                    session_data.update(changes)
                try:
                    session_data['product_ids'] = get_products_ids_list(session.get('product_ids', []))
                except AttributeError:
                    session_data['product_ids'] = []
            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            self.close_connections()

    return wrapper


def token_required_v65_offline(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid params before calling the actual view.
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)

            session_data = dict()
            request_args = token_parser.parse_args()
            user_id = 0
            session = None
            token = request_args.get('session_token', None)
            session_repo_instance = SessionRepositoryV65()
            family_member_repo = FamilyMemberRepository()
            family_repo = FamilyRepository()
            if token:
                session = session_repo_instance.find_by_token(token)
                if not session:
                    data = "Session has been expired."
                    self.status_code = 403
                    self.code = 403
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)
                try:
                    session_api_version = int(session.get('company', '')[-2:])
                except Exception:
                    session_api_version = 0
                try:
                    if session_api_version < 65:
                        session_repo_instance.remove_session(session_id=session.get('id'))
                        data = "You are logged out.Sign in from latest app."
                        self.status_code = 403
                        self.code = 403
                        self.send_response_flag = True
                        return self.send_response(data, self.status_code)
                except Exception:
                    raise Forbidden
                user_id = session.get('customer_id')

            if getattr(self, 'strict_token', False):
                if not token:
                    data = 'Session has been expired.'
                    self.status_code = 403
                    self.code = 403
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)
                if not user_id:
                    data = 'User identity is missing.'
                    self.status_code = 403
                    self.code = 403
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)

            if token:
                if not user_id:
                    data = 'User identity is missing.'
                    self.status_code = 403
                    self.code = 403
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)

                customer_repo_instance = CustomerProfile(logger=self.logger)
                session_data['user_in_family_ever'] = False
                customer_profile = customer_repo_instance.load_customer_profile_by_user_id(user_id)
                user_in_family_ever = family_member_repo.find_family_member(
                    filters={'user_id': user_id},
                    not_equal_filters={'member_since': None}
                )
                session_data['user_in_family_ever'] = len(user_in_family_ever) > 0

                # Disable Email verification on request by Sir Imtiaz
                # Check for user email if 24 hours passed and user still not verified the email
                # user_create_time = customer_profile.get('create_time')
                # user_create_time = user_create_time + datetime.timedelta(hours=24)
                # current_time = datetime.datetime.now().replace(microsecond=0)
                # if current_time > user_create_time:
                #     user = customer_repo_instance.load_customer_by_id(customer_profile.get('user_id'))
                #     from repositories.customer_social_acc_repo import CustomerSocialAccRepository
                #     social_customer = CustomerSocialAccRepository().is_exist_old(customer_id=user.get('id'))
                #     if not social_customer:
                #         if not user.get('is_email_verified'):
                #             data = {
                #                 "resend_invite_section": {
                #                     "title": "Verify your email",
                #                     "message": "Looks like you failed to verify your e-mail address. Please verify "
                #                                "your e-mail address or contact customer services at "
                #                                "customerservice@theentertainerme.com for further help.",
                #                     'email': user.get('id'),
                #                     "button_text": "RESEND"
                #                 }
                #             }
                #             data['message'] = data['resend_invite_section']['message']
                #             self.status_code = 403
                #             self.code = 403
                #             self.send_response_flag = True
                #             return self.send_response(data, self.status_code)

                session_data['id'] = session.get('id')
                session_data['company'] = session.get('company')
                session_data['customer_id'] = user_id
                session_data['session_token'] = session.get('session_token')
                session_data['is_member_on_trail'] = False
                session_data['is_using_trial'] = False
                session_data['onboarding_redemptions_count'] = customer_profile.get('onboarding_redemptions_count', 0)
                session_data['user_id'] = user_id
                session_data['firstname'] = customer_profile.get('firstname')
                session_data['lastname'] = customer_profile.get('lastname')
                session_data['is_primary'] = False
                session_data['is_user_in_family'] = False
                session_data['family_is_active'] = False
                session_data['family_info'] = {}
                session_data['family_member_info'] = {}
                session_data['primary_member_info'] = {}
                session_data['cheers_product_ids'] = []
                session_data['on_grace_period'] = False

                session_data['member_type_id'] = customer_profile.get('new_member_group')
                session_data['primary_member_membership_status'] = customer_repo_instance.MEMBERSTATUS_PROSPTECT
                family_member_details = family_member_repo.find_family_member(
                    filters={'user_id': user_id, 'status': family_member_repo.ACCEPTED, 'is_active': 1}
                )
                session_data['family_member_info'] = family_member_details
                if family_member_details:
                    family_information = family_repo.find_family(
                        filters={'id': family_member_details.get('family_id', 0), 'is_active': 1}
                    )
                    session_data['family_info'] = family_information
                    if family_information:
                        session_data['family_is_active'] = family_information.get('status') in [
                            family_repo.ACTIVE, family_repo.ON_GRACE_PERIOD
                        ]
                        session_data['is_user_in_family'] = True
                        session_data['is_primary'] = bool(family_member_details.get('is_primary', False))

                if customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_MEMBER:
                    session_data['is_primary'] = True
                    session_data['primary_member_membership_status'] = customer_profile.get('new_member_group')

                if session_data['is_primary']:
                    session_data['primary_member_info'] = family_member_details

                if not session_data['is_user_in_family']:
                    try:
                        session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                    except NameError:
                        user_in_family_ever = family_member_repo.find_family_member(
                            filters={'user_id': user_id},
                            not_equal_filters={'member_since': None}
                        )
                    session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                    if not session_data['user_in_family_ever']:
                        # trails_days_remaining = 0
                        # if customer_profile.get('onboarding_startdate'):
                        #     trails_days_remaining = customer_repo_instance.get_trial_remaining_days(
                        #         customer_profile.get('onboarding_startdate')
                        #     )
                        is_member_on_trail = all([
                            customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_ONBOARDING,
                            # trails_days_remaining <= customer_repo_instance.TRIAL_DAYS + 1,
                            # trails_days_remaining > 0,
                            customer_profile.get('onboarding_redemptions_count', 0) < customer_repo_instance.TRAIL_REDEMPTIONS_LIMIT  # noqa : E501
                        ])
                        if is_member_on_trail and customer_profile.get('onboarding_status') == 1:
                            session_data['is_using_trial'] = True
                            session_data['is_member_on_trail'] = True
                        if not session_data['is_member_on_trail'] and customer_profile.get('new_member_group') not in [
                            customer_repo_instance.MEMBERSTATUS_MEMBER,
                            customer_repo_instance.MEMBERSTATUS_REPROSPECT
                        ]:
                            changes = dict()
                            changes['onboarding_status'] = 2
                            changes['member_group'] = CustomerProfile.MEMBERSTATUS_PROSPTECT
                            changes['new_member_group'] = CustomerProfile.MEMBERSTATUS_PROSPTECT
                            changes['onboarding_status'] = CustomerProfile.ONBOARDING_FINISHED
                            changes['onboarding_enddate'] = get_current_date_time()
                            customer_profile.update(changes)

                session_data['product_ids'] = []
                session_data['owns_cheer_products'] = False
                try:
                    if session_data['is_primary']:
                        session_data['product_ids'] = get_products_ids_list(session.get('product_ids', []))
                    elif session_data['is_user_in_family'] and not session_data['is_primary']:
                        # if user is some family and not primary
                        primary_family_user_information = family_member_repo.find_family_member(
                            filters={
                                'is_primary': 1,
                                'family_id': session_data['family_info'].get('id', 0),
                                'is_active': 1,
                                'user_id': session_data['family_info'].get('user_id', 0)
                            }
                        )
                        cheers_product_ids = ProductEntActiveRepository().get_cheers_product_by_product_ids(
                            session_data['product_ids'], convert_to_string=True
                        )
                        if cheers_product_ids:
                            session['owns_cheer_products'] = True
                        if primary_family_user_information:
                            session_data['primary_member_info'] = primary_family_user_information
                            primary_user_session_data = session_repo_instance.find_latest_token_by_user_id(
                                primary_family_user_information.get('user_id', 0),
                                isactive=False
                            )
                            session_data['product_ids'] = primary_user_session_data.get('product_ids', '').split(',')
                            cheers_product_ids = ProductEntActiveRepository().get_cheers_product_by_product_ids(
                                session_data['product_ids'], convert_to_string=True
                            )
                            if cheers_product_ids:
                                session_data['owns_cheer_products'] = True
                            if not session_data['family_member_info'].get('is_cheers_to_include', False):
                                session_data['product_ids'] = list(
                                    set(session_data['product_ids']) - set(cheers_product_ids)
                                )
                                session_data['cheers_product_ids'] = cheers_product_ids
                except AttributeError:
                    session_data['product_ids'] = []

                if session_data['family_info'].get('status') == family_repo.ACTIVE:
                    if all([
                        session_data['is_user_in_family'],
                        session_data['family_is_active'],
                        not session_data['product_ids']
                    ]):
                        primary_customer_profile = customer_repo_instance.load_customer_profile_by_id(
                            session_data['primary_member_info'].get('user_id')
                        )
                        session_data['primary_member_membership_status'] = primary_customer_profile.get('new_member_group')  # noqa : E501
                        if (
                            primary_customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_REPROSPECT  # noqa : E501
                        ):
                            family_data = {'status': family_repo.ON_GRACE_PERIOD}
                            session_data['family_info'].update(family_data)

                session_data['on_grace_period'] = session_data['family_info'].get('status') == family_repo.ON_GRACE_PERIOD  # noqa
                if session_data['on_grace_period']:
                    if all([
                        session_data['is_user_in_family'],
                        session_data['family_is_active'],
                        not session_data['product_ids'],
                        (datetime.datetime.now() - session_data['family_info'].get('date_updated')).days > family_repo.GRACE_PERIOD_EXPIRED_DAYS_LIMIT  # noqa : E501
                    ]):
                        self.family_repo.check_family_expired_and_grace_period(session_data=session_data)
                        primary_customer_profile = customer_repo_instance.load_customer_profile_by_id(
                            session_data['primary_member_info'].get('user_id')
                        )
                        session_data['primary_member_membership_status'] = primary_customer_profile.get('new_member_group')  # noqa : E501
                        if (
                            primary_customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_REPROSPECT  # noqa : E501
                        ):
                            family_data = {'status': family_repo.EXPIRED, 'is_active': 0}
                            family_member_repo.update_member(
                                filters={'family_id': session_data['family_info'].get('id')},
                                data={'is_active': 0}
                            )
                            session_data['family_info'].update(family_data)
                            session_data['family_member_info']['is_active'] = 0
                            session_data['primary_member_info']['is_active'] = 0
                            session_data['is_user_in_family'] = False
                            session_data['family_is_active'] = False

            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper


def token_required_v612_offline(fn):
    """
    If you decorate a view with this, it will ensure that the requester has a
    valid params before calling the actual view.
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)

            session_data = dict()
            request_args = token_parser.parse_args()
            user_id = 0
            session = None
            token = request_args.get('session_token', None)
            session_repo_instance = SessionRepositoryV65()
            family_member_repo = FamilyMemberRepository()
            family_repo = FamilyRepository()
            if token:
                session = session_repo_instance.find_by_token(token)
                if not session:
                    data = "Session has been expired."
                    self.status_code = SESSION_EXPIRED_STATUS_CODE
                    self.code = SESSION_EXPIRED_STATUS_CODE
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)
                try:
                    session_api_version = int(session.get('company', '')[-2:])
                except Exception:
                    session_api_version = 0
                try:
                    if session_api_version < 65:
                        session_repo_instance.remove_session(session_id=session.get('id'))
                        data = "You are logged out.Sign in from latest app."
                        self.status_code = SESSION_EXPIRED_STATUS_CODE
                        self.code = SESSION_EXPIRED_STATUS_CODE
                        self.send_response_flag = True
                        return self.send_response(data, self.status_code)
                except Exception:
                    raise EntertainerForbidden
                user_id = session.get('customer_id')

            if getattr(self, 'strict_token', False):
                if not token:
                    data = 'Session has been expired.'
                    self.status_code = SESSION_EXPIRED_STATUS_CODE
                    self.code = SESSION_EXPIRED_STATUS_CODE
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)
                if not user_id:
                    data = 'User identity is missing.'
                    self.status_code = SESSION_EXPIRED_STATUS_CODE
                    self.code = SESSION_EXPIRED_STATUS_CODE
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)

            if token:
                if not user_id:
                    data = 'User identity is missing.'
                    self.status_code = SESSION_EXPIRED_STATUS_CODE
                    self.code = SESSION_EXPIRED_STATUS_CODE
                    self.send_response_flag = True
                    return self.send_response(data, self.status_code)

                customer_repo_instance = CustomerProfile(logger=self.logger)
                session_data['user_in_family_ever'] = False
                customer_profile = customer_repo_instance.load_customer_profile_by_user_id(user_id)
                user_in_family_ever = family_member_repo.find_family_member(
                    filters={'user_id': user_id},
                    not_equal_filters={'member_since': None}
                )
                session_data['user_in_family_ever'] = len(user_in_family_ever) > 0

                # Disable Email verification on request by Sir Imtiaz
                # Check for user email if 24 hours passed and user still not verified the email
                # user_create_time = customer_profile.get('create_time')
                # user_create_time = user_create_time + datetime.timedelta(hours=24)
                # current_time = datetime.datetime.now().replace(microsecond=0)
                # if current_time > user_create_time:
                #     user = customer_repo_instance.load_customer_by_id(customer_profile.get('user_id'))
                #     from repositories.customer_social_acc_repo import CustomerSocialAccRepository
                #     social_customer = CustomerSocialAccRepository().is_exist_old(customer_id=user.get('id'))
                #     if not social_customer:
                #         if not user.get('is_email_verified'):
                #             data = {
                #                 "resend_invite_section": {
                #                     "title": "Verify your email",
                #                     "message": "Looks like you failed to verify your e-mail address. Please verify "
                #                                "your e-mail address or contact customer services at "
                #                                "customerservice@theentertainerme.com for further help.",
                #                     'email': user.get('id'),
                #                     "button_text": "RESEND"
                #                 }
                #             }
                #             data['message'] = data['resend_invite_section']['message']
                #             self.status_code = SESSION_EXPIRED_STATUS_CODE
                #             self.code = SESSION_EXPIRED_STATUS_CODE
                #             self.send_response_flag = True
                #             return self.send_response(data, self.status_code)

                session_data['id'] = session.get('id')
                session_data['company'] = session.get('company')
                session_data['customer_id'] = user_id
                session_data['session_token'] = session.get('session_token')
                session_data['is_member_on_trail'] = False
                session_data['is_using_trial'] = False
                session_data['onboarding_redemptions_count'] = customer_profile.get('onboarding_redemptions_count', 0)
                session_data['user_id'] = user_id
                session_data['firstname'] = customer_profile.get('firstname')
                session_data['lastname'] = customer_profile.get('lastname')
                session_data['is_primary'] = False
                session_data['is_user_in_family'] = False
                session_data['family_is_active'] = False
                session_data['family_info'] = {}
                session_data['family_member_info'] = {}
                session_data['primary_member_info'] = {}
                session_data['cheers_product_ids'] = []
                session_data['on_grace_period'] = False

                session_data['member_type_id'] = customer_profile.get('new_member_group')
                session_data['primary_member_membership_status'] = customer_repo_instance.MEMBERSTATUS_PROSPTECT
                family_member_details = family_member_repo.find_family_member(
                    filters={'user_id': user_id, 'status': family_member_repo.ACCEPTED, 'is_active': 1}
                )
                session_data['family_member_info'] = family_member_details
                if family_member_details:
                    family_information = family_repo.find_family(
                        filters={'id': family_member_details.get('family_id', 0), 'is_active': 1}
                    )
                    session_data['family_info'] = family_information
                    if family_information:
                        session_data['family_is_active'] = family_information.get('status') in [
                            family_repo.ACTIVE, family_repo.ON_GRACE_PERIOD
                        ]
                        session_data['is_user_in_family'] = True
                        session_data['is_primary'] = bool(family_member_details.get('is_primary', False))

                if customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_MEMBER:
                    session_data['is_primary'] = True
                    session_data['primary_member_membership_status'] = customer_profile.get('new_member_group')

                if session_data['is_primary']:
                    session_data['primary_member_info'] = family_member_details

                if not session_data['is_user_in_family']:
                    try:
                        session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                    except NameError:
                        user_in_family_ever = family_member_repo.find_family_member(
                            filters={'user_id': user_id},
                            not_equal_filters={'member_since': None}
                        )
                    session_data['user_in_family_ever'] = len(user_in_family_ever) > 0
                    if not session_data['user_in_family_ever']:
                        # trails_days_remaining = 0
                        # if customer_profile.get('onboarding_startdate'):
                        #     trails_days_remaining = customer_repo_instance.get_trial_remaining_days(
                        #         customer_profile.get('onboarding_startdate')
                        #     )
                        is_member_on_trail = all([
                            customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_ONBOARDING,
                            # trails_days_remaining <= customer_repo_instance.TRIAL_DAYS + 1,
                            # trails_days_remaining > 0,
                            customer_profile.get('onboarding_redemptions_count', 0) < customer_repo_instance.TRAIL_REDEMPTIONS_LIMIT  # noqa : E501
                        ])
                        if is_member_on_trail and customer_profile.get('onboarding_status') == 1:
                            session_data['is_using_trial'] = True
                            session_data['is_member_on_trail'] = True
                        if not session_data['is_member_on_trail'] and customer_profile.get('new_member_group') not in [
                            customer_repo_instance.MEMBERSTATUS_MEMBER,
                            customer_repo_instance.MEMBERSTATUS_REPROSPECT
                        ]:
                            changes = dict()
                            changes['onboarding_status'] = 2
                            changes['member_group'] = CustomerProfile.MEMBERSTATUS_PROSPTECT
                            changes['new_member_group'] = CustomerProfile.MEMBERSTATUS_PROSPTECT
                            changes['onboarding_status'] = CustomerProfile.ONBOARDING_FINISHED
                            changes['onboarding_enddate'] = get_current_date_time()
                            customer_profile.update(changes)

                session_data['product_ids'] = []
                session_data['owns_cheer_products'] = False
                try:
                    if session_data['is_primary']:
                        session_data['product_ids'] = get_products_ids_list(session.get('product_ids', []))
                    elif session_data['is_user_in_family'] and not session_data['is_primary']:
                        # if user is some family and not primary
                        primary_family_user_information = family_member_repo.find_family_member(
                            filters={
                                'is_primary': 1,
                                'family_id': session_data['family_info'].get('id', 0),
                                'is_active': 1,
                                'user_id': session_data['family_info'].get('user_id', 0)
                            }
                        )
                        cheers_product_ids = ProductEntActiveRepository().get_cheers_product_by_product_ids(
                            session_data['product_ids'], convert_to_string=True
                        )
                        if cheers_product_ids:
                            session['owns_cheer_products'] = True
                        if primary_family_user_information:
                            session_data['primary_member_info'] = primary_family_user_information
                            primary_user_session_data = session_repo_instance.find_latest_token_by_user_id(
                                primary_family_user_information.get('user_id', 0),
                                isactive=False
                            )
                            session_data['product_ids'] = primary_user_session_data.get('product_ids', '').split(',')
                            cheers_product_ids = ProductEntActiveRepository().get_cheers_product_by_product_ids(
                                session_data['product_ids'], convert_to_string=True
                            )
                            if cheers_product_ids:
                                session_data['owns_cheer_products'] = True
                            if not session_data['family_member_info'].get('is_cheers_to_include', False):
                                session_data['product_ids'] = list(
                                    set(session_data['product_ids']) - set(cheers_product_ids)
                                )
                                session_data['cheers_product_ids'] = cheers_product_ids
                except AttributeError:
                    session_data['product_ids'] = []

                if session_data['family_info'].get('status') == family_repo.ACTIVE:
                    if all([
                        session_data['is_user_in_family'],
                        session_data['family_is_active'],
                        not session_data['product_ids']
                    ]):
                        primary_customer_profile = customer_repo_instance.load_customer_profile_by_id(
                            session_data['primary_member_info'].get('user_id')
                        )
                        session_data['primary_member_membership_status'] = primary_customer_profile.get('new_member_group')  # noqa : E501
                        if (
                            primary_customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_REPROSPECT  # noqa : E501
                        ):
                            family_data = {'status': family_repo.ON_GRACE_PERIOD}
                            session_data['family_info'].update(family_data)

                session_data['on_grace_period'] = session_data['family_info'].get('status') == family_repo.ON_GRACE_PERIOD  # noqa
                if session_data['on_grace_period']:
                    if all([
                        session_data['is_user_in_family'],
                        session_data['family_is_active'],
                        not session_data['product_ids'],
                        (datetime.datetime.now() - session_data['family_info'].get('date_updated')).days > family_repo.GRACE_PERIOD_EXPIRED_DAYS_LIMIT  # noqa : E501
                    ]):
                        self.family_repo.check_family_expired_and_grace_period(session_data=session_data)
                        primary_customer_profile = customer_repo_instance.load_customer_profile_by_id(
                            session_data['primary_member_info'].get('user_id')
                        )
                        session_data['primary_member_membership_status'] = primary_customer_profile.get('new_member_group')  # noqa : E501
                        if (
                            primary_customer_profile.get('new_member_group') == customer_repo_instance.MEMBERSTATUS_REPROSPECT  # noqa : E501
                        ):
                            family_data = {'status': family_repo.EXPIRED, 'is_active': 0}
                            family_member_repo.update_member(
                                filters={'family_id': session_data['family_info'].get('id')},
                                data={'is_active': 0}
                            )
                            session_data['family_info'].update(family_data)
                            session_data['family_member_info']['is_active'] = 0
                            session_data['primary_member_info']['is_active'] = 0
                            session_data['is_user_in_family'] = False
                            session_data['family_is_active'] = False

            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper


def set_customer_and_device_id(customer, device):
    """
    Set customer and device key in session

    :param int customer: Customer id
    :param str device: Device key
    """
    session_data = getattr(ctx_stack.top, 'session_data', {})
    session_data.update({
        'user_id': customer, 'device_key': device
    })
    ctx_stack.top.session_data = session_data


def get_current_customer():
    """
    Return the customer's session-data.
    """
    return getattr(ctx_stack.top, 'session_data', {})


def get_customer_and_device_id():
    """
    Return the customer device id and current user id

    :return tuple (int, str): customer_id and device_key
    """
    return (
        getattr(ctx_stack.top, 'session_data', {}).get('user_id', None),
        getattr(ctx_stack.top, 'session_data', {}).get('device_key', None)
    )


class HTTPBasicAuthEntertainer(HTTPBasicAuth):

    def login_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_app.config.get('BASIC_AUTH_ENABLED', False):
                return f(*args, **kwargs)
            auth = request.authorization
            # To disable basic auth on particular view(s)
            for disabled_view in current_app.config.get('BASIC_AUTH_DISABLED_VIEWS', []):
                if isinstance(args[0], disabled_view):
                    return f(*args, **kwargs)
            # To avoid circular import
            from web_api.sharing.api import PostSharingSendApi
            if isinstance(args[0], PostSharingSendApi):
                return f(*args, **kwargs)
            if auth is None and 'Authorization' in request.headers:
                # Flask/Werkzeug do not recognize any authentication types
                # other than Basic or Digest, so here we parse the header by
                # hand
                try:
                    auth_type, token = request.headers['Authorization'].split(
                        None, 1)
                    auth = Authorization(auth_type, {'token': token})
                except ValueError:
                    # The Authorization header is either empty or has no token
                    pass

            # if the auth type does not match, we act as if there is no auth
            # this is better than failing directly, as it allows the callback
            # to handle special cases, like supporting multiple auth types
            if auth is not None and auth.type.lower() != self.scheme.lower():
                auth = None

            # Flask normally handles OPTIONS requests on its own, but in the
            # case it is configured to forward those to the application, we
            # need to ignore authentication headers and let the request through
            # to avoid unwanted interactions with CORS.
            if request.method != 'OPTIONS':  # pragma: no cover
                if auth and auth.username:
                    password = self.get_password_callback(auth.username)
                else:
                    password = None
                if not self.authenticate(auth, password):
                    # Clear TCP receive buffer of any pending data
                    return self.auth_error_callback()

            return f(*args, **kwargs)
        return decorated

    def sudo_login_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            from app_configurations.security_credentials import SUDO_USER

            auth = request.authorization
            if auth is not None and auth.type.lower() != self.scheme.lower():
                auth = None
            # Flask normally handles OPTIONS requests on its own, but in the
            # case it is configured to forward those to the application, we
            # need to ignore authentication headers and let the request through
            # to avoid unwanted interactions with CORS.
            if request.method == 'POST':  # pragma: no cover
                if auth and auth.username == SUDO_USER:
                    password = self.get_password_callback(auth.username)
                else:
                    password = None
                if self.authenticate(auth, password):
                    return f(*args, **kwargs)
            # Clear TCP receive buffer of any pending data
            return self.auth_error_callback()
        return decorated


def jwt_token_required_cashless(fn):
    """
    If you decorate a vew with this, it will ensure that the requester has a
    valid JWT before calling the actual view. This does not check the freshness
    of the token.
    See also: fresh_jwt_required()
    :param fn: The view function to decorate
    """
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)

            jwt_data = _decode_jwt_from_request(request_type='access')
            ctx_stack.top.jwt = jwt_data
            _load_user(jwt_data['identity'])
            data = jwt_data['identity']
            if data:
                session_data = dict()
                merchant_sf_id = data.get('merchant_sf_id', 0)
                outlet_sf_id = data.get('outlet_sf_id', 0)
                device_id = data.get('device_id', '')
                merchant_repo_instance = MerchantRepository()
                dm_device_repo_instance = DmDevicesRepository()
                outlet_repo_instance = OutletRepository()
                merchant_response = merchant_repo_instance.find_by_sf_id(merchant_sf_id)
                if merchant_response:
                    if outlet_sf_id:
                        outlet = outlet_repo_instance.find_by_sf_id(outlet_sf_id)
                        if not outlet:
                            raise Forbidden("No Outlet Found")
                        data['outlet_sf_id'] = outlet_sf_id

                    data['device_id'] = device_id
                    data['merchant_sf_id'] = merchant_sf_id
                    valid_device_id = dm_device_repo_instance.find_device_by_filter(_filters=data)
                    if valid_device_id:
                        if not valid_device_id.get('is_active', False):
                            raise Forbidden("Device is in-active.")

                        session_data['merchant_sf_id'] = merchant_sf_id
                        session_data['device_id'] = device_id
                        session_data['outlet_sf_id'] = outlet_sf_id
                        ctx_stack.top.session_data = session_data
                        return fn(self, *args, **kwargs)
                    else:
                        raise Forbidden("No Device Found")
                else:
                    raise Forbidden("No Merchant Found")
            else:
                raise Forbidden("Token params are not available")
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper


def token_required_white_label(fn):

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        close_connection = True
        try:
            if not getattr(self, 'required_token', False):
                close_connection = False
                return fn(self, *args, **kwargs)

            # Initialize Repos
            session_repo_instance = SessionRepositoryWhiteLabel()
            customer_repo_instance = CustomerProfileWhiteLabel()

            # Param Fetcher Object
            session_data = dict()
            request_args = token_parser.parse_args()
            session_token = request_args.get('session_token', '')
            app_version = request_args.get('app_version', '')
            company = request_args.get('wlcompany', '')
            user_id = request_args.get('__i', 0)

            try:
                session_id = request_args.get('__sid', 0)
                if company in WHITE_LABEL_COMPANIES_WITH_SKIP_MODE and not session_token:
                    ctx_stack.top.session_data = session_data
                    return fn(self, *args, **kwargs)
                if not session_token:
                    raise Forbidden(
                        'A valid session session_token is required for this call. - {session_token} - {url}'.format(
                            session_token=session_token,
                            url=str(request.path)
                        )
                    )
                if get_pre_activated_apps(company):
                    white_label_key = request_args.get('key', '')
                    if not white_label_key:
                        data = "The imie number is required"
                        self.status_code = 403
                        self.code = 403
                        self.send_response_flag = True
                        return self.send_response(data, self.status_code)
            except Exception:
                data = {}
                self.status_code = 403
                self.code = 403
                self.send_response_flag = True
                return self.send_response(data, self.status_code)

            if session_id:
                # Validate Session Token and populate the request session object
                session = session_repo_instance.find_by_id(company=company, session_id=session_id)
            else:
                session = session_repo_instance.find_by_token(company=company, session_token=session_token)
            if session:
                session_id = session.get('id')
                user_id = session.get('customer_id')

            if any([
                session.get('session_token') != session_token,
                session_id != session.get('id'),
                session.get('customer_id') != user_id
            ]):
                raise Forbidden(
                    'Session is tempered. -> token:{session_token}, user_id:{user_id}, request:{url} '.format(
                        session_token=session_token,
                        user_id=user_id,
                        url=str(request.path)
                    )
                )

            if app_version and session.get('app_version') != app_version:
                session_repo_instance.update_app_version(
                    app_version=app_version,
                    session=session
                )

            cached_on = session.get('date_cached', 0)
            product_ids = session.get('product_ids', '')

            if any([not cached_on, not product_ids]):
                try:
                    # need to be according to white label
                    product_ids = customer_repo_instance.get_customer_products(
                        user_id=user_id,
                        company=company
                    )
                    date_created = datetime.datetime.now()
                    date_created = date_created.replace(tzinfo=datetime.timezone.utc).timestamp()
                    session_repo_instance.update_session_product_ids(
                        session_id=session_id,
                        product_ids=product_ids,
                        date_cached=date_created
                    )
                except Exception:
                    raise
            session_data['id'] = session.get('id')
            session_data['session_token'] = session.get('session_token')
            session_data['is_using_trial'] = False
            session_data['user_id'] = user_id
            session_data['customer_id'] = user_id
            session_data['new_member_group'] = customer_repo_instance.MEMBERSTATUS_PROSPTECT
            if product_ids:
                session_data['new_member_group'] = customer_repo_instance.MEMBERSTATUS_MEMBER
            session_data['member_type_id'] = session_data['new_member_group']
            session_data['member_type'] = customer_repo_instance.get_member_type(session_data['new_member_group'])
            session_data['family_is_active'] = False
            session_data['is_user_in_family'] = False
            session_data['owns_cheer_products'] = False
            session_data['company'] = company
            try:
                session_data['product_ids'] = session.get('product_ids', '').split(',')
            except AttributeError:
                session_data['product_ids'] = []
            ctx_stack.top.session_data = session_data
            return fn(self, *args, **kwargs)
        except BadRequest as bad_request_exception:
            return self.process_bad_request(exception_raised=bad_request_exception)
        except Exception as exception_raised:
            return self.process_request_exception(exception_raised=exception_raised)
        finally:
            if close_connection:
                self.close_connections()
    return wrapper
