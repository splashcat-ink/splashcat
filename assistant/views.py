# Create your views here.
import json
from io import StringIO, BytesIO

import django_htmx.http
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_POST
from openai import OpenAI

from assistant.forms import CreateThreadForm
from assistant.models import Thread
from battles.models import Battle, Player
from users.models import User, SponsorshipTiers

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def require_s_plus_ponsor(view_func):
    def _wrapper(request, *args, **kwargs):
        user: User = request.user
        if not user.sponsor_tiers[SponsorshipTiers.S_PLUS_PONSOR]:
            return redirect('sponsor')
        return view_func(request, *args, **kwargs)

    return _wrapper


@login_required
@require_s_plus_ponsor
def threads(request):
    user_threads = request.user.thread_set.all()

    return render(request, "assistant/list_threads.html", {
        'threads': user_threads,
    })


@login_required
@require_s_plus_ponsor
def create_thread(request):
    if request.method == "GET":
        form = CreateThreadForm()
        return render(request, "assistant/create_thread.html", {
            'form': form,
        })

    form = CreateThreadForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid create thread form.")

    player_query = Player.objects.select_related(
        "title_adjective__string",
        "title_subject__string",
        "nameplate_background",
        "nameplate_badge_1__description",
        "nameplate_badge_2__description",
        "nameplate_badge_3__description",
        "weapon__name",
        "weapon__sub__name",
        "weapon__special__name",
        "head_gear__gear__name",
        "head_gear__primary_ability__name",
        "head_gear__secondary_ability_1__name",
        "head_gear__secondary_ability_2__name",
        "head_gear__secondary_ability_3__name",
        "clothing_gear__gear__name",
        "clothing_gear__primary_ability__name",
        "clothing_gear__secondary_ability_1__name",
        "clothing_gear__secondary_ability_2__name",
        "clothing_gear__secondary_ability_3__name",
        "shoes_gear__gear__name",
        "shoes_gear__primary_ability__name",
        "shoes_gear__secondary_ability_1__name",
        "shoes_gear__secondary_ability_2__name",
        "shoes_gear__secondary_ability_3__name",
    )
    player_prefetch = Prefetch(
        'teams__players',
        queryset=player_query,
    )

    battles = request.user.battles.select_related("vs_stage__name").prefetch_related("awards__name",
                                                                                     player_prefetch).order_by(
        '-played_time')

    battle_array = []

    battle: Battle
    for battle in battles:
        battle_data = battle.to_gpt_dict()
        battle_array.append(json.dumps(battle_data) + '\n')

    temp_file = StringIO("")
    temp_file.writelines(battle_array)
    temp_file.seek(0)
    temp_file = BytesIO(temp_file.read().encode('utf-8'))

    temp_file.seek(0)

    openai_file = client.files.create(
        file=temp_file,
        purpose='assistants'
    )

    openai_thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": form.cleaned_data['initial_message'],
                "file_ids": [openai_file.id]
            }
        ]
    )
    thread = Thread(creator=request.user, openai_thread_id=openai_thread.id, openai_file_id=openai_file.id)
    thread.save()

    run = client.beta.threads.runs.create(
        thread_id=openai_thread.id,
        assistant_id=settings.OPENAI_ASSISTANT_ID,
    )

    return redirect("assistant:view_thread", thread.id)


@login_required
@require_s_plus_ponsor
def view_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, creator=request.user)
    openai_thread_id = thread.openai_thread_id
    openai_thread_messages = client.beta.threads.messages.list(openai_thread_id, order='asc', limit=100)

    return render(request, "assistant/view_thread.html", {
        'thread': thread,
        'thread_messages': openai_thread_messages,
    })


@login_required
@require_s_plus_ponsor
def get_thread_messages(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, creator=request.user)
    openai_thread_id = thread.openai_thread_id
    openai_thread_messages = client.beta.threads.messages.list(openai_thread_id, order='asc', limit=100)

    latest_run = client.beta.threads.runs.list(
        thread_id=openai_thread_id,
        limit=1,
        order='desc',
    )
    latest_run = latest_run.data[0]
    latest_status = latest_run.status if latest_run else 'completed'

    is_currently_done = latest_status in ['completed', 'expired', 'cancelled', 'failed']

    is_disabling_input = request.GET.get('isDisablingInput', 'False') == 'True'
    if is_disabling_input == is_currently_done:
        response = render(request, "assistant/htmx/thread_container.html",
                          {'thread': thread, 'thread_messages': openai_thread_messages,
                           'message_sending_disabled': not is_currently_done, })

        django_htmx.http.retarget(response, '#entire-thread-container')
        django_htmx.http.reswap(response, 'innerHTML')

        return response

    return render(request, "assistant/htmx/messages_list.html", {
        'thread': thread,
        'thread_messages': openai_thread_messages,
        'message_sending_disabled': not is_currently_done,
        'gpt_processing': not is_currently_done,
    })


@login_required
@require_s_plus_ponsor
@require_POST
def send_message_to_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, creator=request.user)
    openai_thread_id = thread.openai_thread_id
    message = request.POST.get('message')

    client.beta.threads.messages.create(
        thread_id=openai_thread_id,
        content=message,
        role='user',
    )

    run = client.beta.threads.runs.create(
        thread_id=openai_thread_id,
        assistant_id=settings.OPENAI_ASSISTANT_ID,
    )

    openai_thread_messages = client.beta.threads.messages.list(openai_thread_id, order='asc', limit=100)

    return render(request, "assistant/htmx/thread_container.html", {
        'thread': thread,
        'thread_messages': openai_thread_messages,
        'message_sending_disabled': True,
        'gpt_processing': True,
    })
