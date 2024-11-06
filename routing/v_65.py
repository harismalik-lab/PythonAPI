"""
Routing for version 6.5
"""
from offline_api.api_v65.family_member_details.api import OfflineFamilyMemberDetails
from offline_api.api_v65.family_pending_invites.api import OfflinePendingInvites
from offline_api.api_v65.family_restrict_view.api import OfflineFamilyRestrict
from offline_api.api_v65.home.api import HomeApiVo65
from offline_api.api_v65.merchants.api import MerchantApiVo65
from offline_api.api_v65.my_family.api import OfflineMyFamily
from offline_api.api_v65.redemption.api import OfflineRedemptionApiV65, OfflineRedemptionSyncApiV65
from offline_api.api_v65.resend_email_api.api import OfflineResendEmailApi
from offline_api.api_v65.sing_in.api import OfflineLoginUserApiV65
from offline_api.offline_reset_password.api import OfflineResetPasswordApi
from routing.v_64 import RoutingV64, RoutingVo64
from web_api.api_v65.add_family_member.api import AddFamilyMember
from web_api.api_v65.apm_test.api import ApmTestApi
from web_api.api_v65.category_home.api import CategoryHomeScreenV65
from web_api.api_v65.configs.api import ConfigsApiV65
from web_api.api_v65.edit_family_member.api import EditFamilyMember
from web_api.api_v65.family_accept_invitation.api import AcceptInvitation
from web_api.api_v65.family_cancel_invitation.api import CancelInvitation
from web_api.api_v65.family_member_cheers_update.api import EditFamilyMemberCheers
from web_api.api_v65.family_member_details.api import FamilyMemberDetails
from web_api.api_v65.family_pending_invites.api import PendingInvites
from web_api.api_v65.family_reactivate.api import FamilyReactivate
from web_api.api_v65.family_remove_member.api import RemoveFamilyMember
from web_api.api_v65.family_resend_invitation.api import ResendInvitation
from web_api.api_v65.get_user.api import GetUserApiV65
from web_api.api_v65.get_user_friends_ranking.api import GetUserFriendsRankingApiV65
from web_api.api_v65.home.api import HomeApiV65
from web_api.api_v65.hotles_enquiry_api.api import HotelsBookingApi
from web_api.api_v65.kaligo_deeplink_action.api import KaligoDeeplinkApiV65
from web_api.api_v65.leave_family.api import LeaveFamily
from web_api.api_v65.merchant.api import MerchantApiV65
from web_api.api_v65.my_family.api import MyFamily
from web_api.api_v65.outlets.api import OutletApiV65
from web_api.api_v65.password_reset.api import UserPasswordResetApiV65
from web_api.api_v65.redemption.api import RedemptionProcessV65, RedemptionsSyncApiV65
from web_api.api_v65.resend_email_api.api import ResendEmailApi
from web_api.api_v65.send_email_token.api import PasswordResetSendEmailApi
from web_api.api_v65.sharing.api import GetSharingReceivedOffersV65, GetSharingSendOffersV65, PostSharingSendApiV65
from web_api.api_v65.sign_in.api import LoginUserApiV65
from web_api.api_v65.sign_up.api import SignUpApiV65
from web_api.api_v65.smiles.api import PostSmilesPurchaseApiV65
from web_api.api_v65.user_profile.api import GetUserProfileApiV65
from web_api.api_v65.user_refresh_session.api import GetUserSessionRefreshApiV65
from web_api.api_v65.web_sign_in_api.api import WebLoginV65


class RoutingV65(RoutingV64):
    api_version = '65'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['get-user'] = {'view': GetUserApiV65, 'url': '/users/<int:user_id>'}
        self.routing_collection['member_details'] = {'view': FamilyMemberDetails, 'url': '/family/member_details'}
        self.routing_collection['my_family'] = {'view': MyFamily, 'url': '/family/my_family'}
        self.routing_collection['pending_invites'] = {'view': PendingInvites, 'url': '/family/pending_invites'}
        self.routing_collection['add_member'] = {'view': AddFamilyMember, 'url': '/family/add_member'}
        self.routing_collection['remove_member'] = {'view': RemoveFamilyMember, 'url': '/family/remove_member'}
        self.routing_collection['leave_family'] = {'view': LeaveFamily, 'url': '/family/leave_family'}
        self.routing_collection['edit_member'] = {'view': EditFamilyMember, 'url': '/family/edit_member'}
        self.routing_collection['accept_invitation'] = {'view': AcceptInvitation, 'url': '/family/accept_invitation'}
        self.routing_collection['cancel_invitation'] = {'view': CancelInvitation, 'url': '/family/cancel_invitation'}
        self.routing_collection['resend_invitation'] = {'view': ResendInvitation, 'url': '/family/resend_invitation'}
        self.routing_collection['edit_family_member_cheers'] = {
            'view': EditFamilyMemberCheers,
            'url': '/family/edit_family_member_cheers'
        }
        self.routing_collection['get-user-profile'] = {'view': GetUserProfileApiV65, 'url': '/user/profile'}
        self.routing_collection['reactivate_family'] = {'view': FamilyReactivate, 'url': '/family/reactivate_family'}
        self.routing_collection['redemptions'] = {'view': RedemptionProcessV65, 'url': '/redemptions'}
        self.routing_collection['redemptions-sync'] = {'view': RedemptionsSyncApiV65, 'url': '/redemptions/sync'}
        self.routing_collection['configs'] = {'view': ConfigsApiV65, 'url': '/configs'}
        self.routing_collection['reset-send-email'] = {'view': ResendEmailApi, 'url': '/resend_email'}
        self.routing_collection['reset-password-email'] = {'view': PasswordResetSendEmailApi,
                                                           'url': '/reset_password_email'}
        self.routing_collection['received_offers'] = {'view': GetSharingReceivedOffersV65,
                                                      'url': '/sharing/receivedoffers'}
        self.routing_collection['send_offer'] = {'view': PostSharingSendApiV65, 'url': '/sharing/send'}
        self.routing_collection['sent_offers'] = {'view': GetSharingSendOffersV65, 'url': '/sharing/sendoffers'}
        self.routing_collection['sessions'] = {'view': LoginUserApiV65, 'url': '/sessions'}
        self.routing_collection['web-sessions'] = {'view': WebLoginV65, 'url': '/sessions/web'}
        self.routing_collection['sign-up'] = {'view': SignUpApiV65, 'url': '/users'}
        self.routing_collection['merchant'] = {'view': MerchantApiV65, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['category_home'] = {'view': CategoryHomeScreenV65, 'url': '/categories/home'}
        self.routing_collection['outlets'] = {'view': OutletApiV65, 'url': '/outlets'}
        self.routing_collection['home'] = {'view': HomeApiV65, 'url': '/home'}
        self.routing_collection['get-user-friends-ranking'] = {'view': GetUserFriendsRankingApiV65,
                                                               'url': '/user/friends/ranking'}
        self.routing_collection['get-user-refresh-session'] = {'view': GetUserSessionRefreshApiV65,
                                                               'url': '/user/session/refresh'}
        self.routing_collection['passwords'] = {'view': UserPasswordResetApiV65, 'url': '/passwords'}
        self.routing_collection['smiles_purchase'] = {'view': PostSmilesPurchaseApiV65, 'url': '/smiles/purchase'}
        self.routing_collection['deeplink'] = {'view': KaligoDeeplinkApiV65, 'url': '/kaligo/deeplink'}
        self.routing_collection['hotels-booking'] = {'view': HotelsBookingApi, 'url': '/hotel/enquiry'}
        self.routing_collection['apm-test'] = {'view': ApmTestApi, 'url': '/apm/test'}


class RoutingVo65(RoutingVo64):
    api_version = 'o65'
    base_url = '/et_rs_prd/web'

    def update_routing_collection(self):
        super().update_routing_collection()
        self.routing_collection['member_details'] = {'view': OfflineFamilyMemberDetails, 'url': '/family/member_details'}
        self.routing_collection['merchants'] = {'view': MerchantApiVo65, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['my_family'] = {'view': OfflineMyFamily, 'url': '/family/my_family'}
        self.routing_collection['pending_invites'] = {'view': OfflinePendingInvites, 'url': '/family/pending_invites'}
        self.routing_collection['add_member'] = {'view': OfflineFamilyRestrict, 'url': '/family/add_member'}
        self.routing_collection['remove_member'] = {'view': OfflineFamilyRestrict, 'url': '/family/remove_member'}
        self.routing_collection['leave_family'] = {'view': OfflineFamilyRestrict, 'url': '/family/leave_family'}
        self.routing_collection['edit_member'] = {'view': OfflineFamilyRestrict, 'url': '/family/edit_member'}
        self.routing_collection['accept_invitation'] = {
            'view': OfflineFamilyRestrict,
            'url': '/family/accept_invitation'
        }
        self.routing_collection['cancel_invitation'] = {
            'view': OfflineFamilyRestrict,
            'url': '/family/cancel_invitation'
        }
        self.routing_collection['resend_invitation'] = {
            'view': OfflineFamilyRestrict,
            'url': '/family/resend_invitation'
        }
        self.routing_collection['edit_family_member_cheers'] = {
            'view': OfflineFamilyRestrict,
            'url': '/family/edit_family_member_cheers'
        }
        self.routing_collection['reactivate_family'] = {'view': OfflineFamilyRestrict,
                                                        'url': '/family/reactivate_family'}
        self.routing_collection['redemptions'] = {'view': OfflineRedemptionApiV65, 'url': '/redemptions'}
        self.routing_collection['redemptions-sync'] = {'view': OfflineRedemptionSyncApiV65, 'url': '/redemptions/sync'}
        self.routing_collection['sessions'] = {'view': OfflineLoginUserApiV65, 'url': '/sessions'}
        self.routing_collection['merchant'] = {'view': MerchantApiV65, 'url': '/merchants/<int:merchant_id>'}
        self.routing_collection['category_home'] = {'view': CategoryHomeScreenV65, 'url': '/categories/home'}
        self.routing_collection['outlets'] = {'view': OutletApiV65, 'url': '/outlets'}
        self.routing_collection['home'] = {'view': HomeApiVo65, 'url': '/home'}
        self.routing_collection['passwords'] = {'view': OfflineResetPasswordApi, 'url': '/passwords'}
        self.routing_collection['reset-send-email'] = {'view': OfflineResendEmailApi, 'url': '/resend_email'}
        self.routing_collection['deeplink'] = {'view': KaligoDeeplinkApiV65, 'url': '/kaligo/deeplink'}
