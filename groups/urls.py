from django.urls import path

from groups.views import view_group, groups_index, group_admin, answer_join_request, invite_to_group, \
    answer_group_invite, request_join_group, join_group, leave_group, create_group, delete_group

app_name = "groups"
urlpatterns = [
    path("", groups_index, name="index"),
    path("<int:group_id>/", view_group, name="view_group"),
    path("<int:group_id>/admin/", group_admin, name="group_admin"),
    path("<int:group_id>/admin/delete/", delete_group, name="delete_group"),
    path("create/", create_group, name="create_group"),
    path("<int:group_id>/request/", request_join_group, name="request_join_group"),
    path("<int:group_id>/request/answer/", answer_join_request, name="answer_join_request"),
    path("<int:group_id>/invite/", invite_to_group, name="invite_to_group"),
    path("<int:group_id>/invite/answer/", answer_group_invite, name="answer_group_invite"),
    path("<int:group_id>/join/", join_group, name="join_group"),
    path("<int:group_id>/leave/", leave_group, name="leave_group"),
]
