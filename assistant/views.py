# Create your views here.

import django_htmx.http
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, get_object_or_404, render
from django.views.decorators.http import require_POST
from openai import OpenAI

from assistant import orchestrator
from assistant.forms import CreateThreadForm
from assistant.models import Thread
from battles.models import Battle, BattleGroup
from users.models import User, SponsorshipTiers

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def require_sponsor_tier(view_func):
    def _wrapper(request, *args, **kwargs):
        user: User = request.user
        if not user.sponsor_tiers[SponsorshipTiers.X_PONSOR]:
            return redirect('sponsor')
        return view_func(request, *args, **kwargs)

    return _wrapper


@login_required
@require_sponsor_tier
def threads(request):
    user_threads = request.user.thread_set.order_by('-created_date')

    return render(request, "assistant/list_threads.html", {
        'threads': user_threads,
    })


@login_required
@require_sponsor_tier
@transaction.atomic
def create_thread(request, app_label=None, model_name=None, object_id=None):
    found_object: None = None
    if app_label:
        if not model_name and not object_id:
            return HttpResponseNotFound()
        content_type = ContentType.objects.get(app_label__iexact=app_label, model__iexact=model_name)
        found_object = content_type.get_object_for_this_type(pk=object_id)

        if content_type.model_class() is Battle:
            found_object: Battle
            if found_object.uploader_id != request.user.id:
                return HttpResponseBadRequest()
        elif content_type.model_class() is BattleGroup:
            found_object: BattleGroup
            if found_object.creator_id != request.user.id:
                return HttpResponseBadRequest()
        else:
            return HttpResponseBadRequest()

    if request.method == "GET":
        form = CreateThreadForm()
        return render(request, "assistant/create_thread.html", {
            'form': form,
        })

    form = CreateThreadForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest("Invalid create thread form.")

    openai_thread = client.beta.threads.create()
    thread = Thread(creator=request.user, openai_thread_id=openai_thread.id, status=Thread.Status.PENDING,
                    initial_message=form.cleaned_data['initial_message'])
    if found_object:
        thread.content_object = found_object
    thread.save()

    machine_id = orchestrator.schedule_machine(thread)

    thread.runner_machine_id = machine_id
    thread.save()

    return redirect("assistant:view_thread", thread.id)


@login_required
@require_sponsor_tier
def view_thread(request, thread_id):
    if request.user.is_superuser:
        thread = get_object_or_404(Thread, id=thread_id)
    else:
        thread = get_object_or_404(Thread, id=thread_id, creator=request.user)
    openai_thread_id = thread.openai_thread_id
    openai_thread_messages = client.beta.threads.messages.list(openai_thread_id, order='asc', limit=100)

    return render(request, "assistant/view_thread.html", {
        'thread': thread,
        'thread_messages': openai_thread_messages,
    })


@login_required
@require_sponsor_tier
def get_thread_messages(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id, creator=request.user)
    openai_thread_id = thread.openai_thread_id
    openai_thread_messages = client.beta.threads.messages.list(openai_thread_id, order='asc', limit=100)

    latest_run = client.beta.threads.runs.list(
        thread_id=openai_thread_id,
        limit=1,
        order='desc',
    )
    latest_run = latest_run.data[0] if len(latest_run.data) > 0 else None
    latest_status = latest_run.status if latest_run else 'completed'

    is_currently_done = latest_status in ['completed', 'expired', 'cancelled',
                                          'failed'] and thread.status != thread.Status.PENDING

    is_disabling_input = request.GET.get('isDisablingInput', 'False') == 'True'
    if is_disabling_input == is_currently_done:
        response = render(request, "assistant/htmx/thread_container.html",
                          {'thread': thread, 'thread_messages': openai_thread_messages,
                           'message_sending_disabled': not is_currently_done, })

        django_htmx.http.retarget(response, '#entire-thread-container')
        # noinspection PyTypeChecker
        # morph:innerHTML is allowed, just part of an extension
        django_htmx.http.reswap(response, 'morph:innerHTML')

        return response

    return render(request, "assistant/htmx/messages_list.html", {
        'thread': thread,
        'thread_messages': openai_thread_messages,
        'message_sending_disabled': not is_currently_done,
        'gpt_processing': not is_currently_done,
    })


@login_required
@require_sponsor_tier
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
