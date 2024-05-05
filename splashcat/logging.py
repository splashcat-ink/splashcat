from django.utils.log import ServerFormatter as DjangoServerFormatter


class ServerFormatter(DjangoServerFormatter):
    def format(self, record):
        msg = super().format(record)
        return f"{record.request.headers.get('User-Agent')} {msg}"
