# Create your views here.
import json
from io import StringIO, BytesIO

from aiohttp.http_exceptions import HttpBadRequest
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_POST
from openai import OpenAI

from assistant.forms import CreateThreadForm
from assistant.models import Thread
from battles.models import Battle
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


@login_required
@require_s_plus_ponsor
@require_POST
def create_thread(request):
    form = CreateThreadForm(request.POST)
    if not form.is_valid():
        return HttpBadRequest("Invalid create thread form.")

    battles = request.user.battles.with_prefetch().order_by('-played_time')

    battle_array = []

    battle: Battle
    for battle in battles:
        battle_data = battle.to_dict()
        battle_array.append(battle_data)

    json_data = json.dumps(battle_array, indent=4, ensure_ascii=False)

    temp_file = StringIO(json_data)
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
                "content": form.initial_message,
                "file_ids": [openai_file.id]
            }
        ]
    )
    thread = Thread(creator=request.user, openai_thread_id=openai_thread.id, openai_file_id=openai_file.id)
    thread.save()

    return redirect("assistant:view_thread", thread.id)


@login_required
@require_s_plus_ponsor
def view_thread(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, creator=request.user)
    openai_thread_id = thread.openai_thread_id
    openai_thread_messages = client.beta.threads.messages.list(openai_thread_id, order='asc')

    return render('assistant/view_thread.html', {
        'thread': thread,
        'messages': openai_thread_messages,
    })
