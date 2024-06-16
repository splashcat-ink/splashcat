from django.conf import settings


def share_query_param(request):
    query_value = request.GET.get('share', None)
    if query_value == "":
        query_value = True
    return {
        'share_query_param': query_value,
    }


def nuxt_iframe_host(request):
    return {
        'nuxt_iframe_host': settings.NUXT_IFRAME_HOST,
    }
