import os
import sys

import django
from django.conf import settings
from openai import OpenAI

from assistant.data import upload_data_to_openai
from assistant.models import Thread
from splashcat import settings as splashcat_settings

settings.configure(default_settings=splashcat_settings, DEBUG=True)
django.setup()

client = OpenAI(api_key=settings.OPENAI_API_KEY)

thread_id = os.environ.get("TASK_THREAD_ID")

thread = Thread.objects.get(pk=thread_id)
initial_prompt = thread.initial_message

openai_file = upload_data_to_openai(thread.creator)

client.beta.threads.messages.create(
    thread_id=thread.openai_thread_id,
    role='user',
    content=thread.initial_message,
    file_ids=[openai_file.id]
)

client.beta.threads.runs.create(
    thread_id=thread.openai_thread_id,
    assistant_id=settings.OPENAI_ASSISTANT_ID,
)

sys.exit()
