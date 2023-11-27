import base64

import openai
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from openai.types.beta.threads.message_content_image_file import ImageFile

register = template.Library()

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)


@register.simple_tag(takes_context=True)
def get_openai_image(context, image: ImageFile):
    file = client.files.content(image.file_id)
    base64_image = base64.b64encode(file.content).decode('ascii')
    return mark_safe(f'<img src="data:image/png;base64,{base64_image}" class="w-full max-w-fit aspect-auto">')
