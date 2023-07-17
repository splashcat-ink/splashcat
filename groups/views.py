from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django_htmx.http import HttpResponseClientRedirect

from battles.models import Battle
from groups.forms import GroupAdminForm, GroupInviteForm
from groups.models import Group, Membership
from users.models import User


# Create your views here.

def groups_index(request):
    # discovery of new groups and links to joined groups
    user: User = request.user
    member_groups = user.get_groups() if user.is_authenticated else None
    random_public_groups = Group.objects.filter(privacy_level=Group.PrivacyLevels.PUBLIC).order_by('?')[:24]
    pending_invites = user.pending_group_invites.all() if user.is_authenticated else None
    return render(request, 'groups/index.html', {
        'member_groups': member_groups,
        'random_public_groups': random_public_groups,
        'pending_invites': pending_invites,
    })


def view_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    group_all_members = list(group.members.all()) + [group.owner]
    group_recent_battles = Battle.objects.with_prefetch().filter(uploader__in=group_all_members).order_by(
        "-played_time")[:16]
    is_group_member = request.user.is_authenticated and request.user in group_all_members

    battles = Battle.objects.filter(uploader__in=group_all_members)

    win_count = battles.filter(judgement='WIN').count()
    lose_count = battles.exclude(judgement__in=['WIN', 'DRAW']).count()
    win_rate = win_count / (win_count + lose_count) * 100 if win_count + lose_count else 0

    return render(request, 'groups/view.html', {
        'group': group,
        'group_recent_battles': group_recent_battles,
        'is_group_member': is_group_member,
        'win_count': win_count,
        'lose_count': lose_count,
        'win_rate': win_rate,
    })


def group_admin(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if group.owner != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = GroupAdminForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, 'Group settings updated.')
            return redirect('groups:view_group', group_id=group_id)
    else:
        form = GroupAdminForm(instance=group)
    group_invite_form = GroupInviteForm()
    return render(request, 'groups/admin/index.html', {
        'group': group,
        'form': form,
        'group_invite_form': group_invite_form,
    })


def create_group(request):
    if request.method == 'POST':
        form = GroupAdminForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            messages.success(request, 'Group created! Invite some friends to join.')
            return redirect('groups:view_group', group_id=group.pk)
    else:
        form = GroupAdminForm()
    return render(request, 'groups/admin/create.html', {
        'form': form,
    })


@require_POST
def request_join_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.user in group.members.all():
        messages.error(request, 'You are already a member of this group.')
    elif request.user in group.pending_join_requests.all():
        messages.error(request, 'You already have a pending request to join this group.')
    else:
        group.pending_join_requests.add(request.user)
        messages.success(request, 'Request to join group sent.')
    return redirect('groups:view_group', group_id=group_id)


@require_POST
def answer_join_request(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if group.owner != request.user:
        return HttpResponseForbidden()
    answer = request.POST.get('answer')
    split_string = answer.split(';')
    user_id = split_string[0]
    answer = split_string[1]
    user = get_object_or_404(User, pk=user_id)
    if answer == 'accept':
        group.pending_join_requests.remove(user)
        membership = Membership(
            person=user,
            group=group,
        )
        membership.save()
        messages.success(request, f'Accepted {user.username} into the group.')
    elif answer == 'deny':
        group.pending_join_requests.remove(user)
        messages.success(request, f'Rejected {user.username} from the group.')
    return redirect('groups:group_admin', group_id=group_id)


@require_POST
def invite_to_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if group.owner != request.user:
        return HttpResponseForbidden()
    form = GroupInviteForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        user = get_object_or_404(User, username__iexact=username)
        if user in group.members.all():
            messages.error(request, f'{username} is already a member of the group.')
        elif user in group.pending_invites.all():
            messages.error(request, f'{username} already has a pending invite.')
        else:
            group.pending_invites.add(user)
            messages.success(request, f'Invited {username} to the group.')
    return redirect('groups:group_admin', group_id=group_id)


@require_POST
def answer_group_invite(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    user: User = request.user
    answer = request.POST.get('answer')
    if answer == 'accept':
        group.pending_invites.remove(user)
        membership = Membership(
            person=user,
            group=group,
        )
        membership.save()
        messages.success(request, f'Accepted invite to {group.name}.')
    elif answer == 'deny':
        group.pending_invites.remove(user)
        messages.success(request, f'Rejected invite to {group.name}.')
    return redirect('groups:index')


@require_POST
def join_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.user in group.members.all():
        messages.error(request, 'You are already a member of this group.')
    else:
        membership = Membership(
            person=request.user,
            group=group,
        )
        membership.save()
        messages.success(request, f'Joined {group.name}.')
    return redirect('groups:view_group', group_id=group_id)


@require_POST
def leave_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
    elif group.owner == request.user:
        messages.error(request, 'You cannot leave a group you own. Please transfer ownership first.')
    else:
        group.members.remove(request.user)
        messages.success(request, f'Left {group.name}.')
    return HttpResponseClientRedirect(reverse('groups:index'))
