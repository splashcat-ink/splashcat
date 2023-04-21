from django.db import models


class Color:
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    @staticmethod
    def from_hex(hex_string):
        return Color(
            int(hex_string[0:2], 16),
            int(hex_string[2:4], 16),
            int(hex_string[4:6], 16),
            int(hex_string[6:8], 16),
        )

    @staticmethod
    def from_floating_point_dict(obj):
        # lowercase keys because lean's data uses capital letters while splatnet uses lowercase

        obj = {k.lower(): v for k, v in obj.items()}

        return Color(
            int(obj['r'] * 255),
            int(obj['g'] * 255),
            int(obj['b'] * 255),
            int(obj['a'] * 255),
        )

    def css(self):
        return f'rgba({self.r}, {self.g}, {self.b}, {self.a / 255})'

    def to_hex(self):
        return f'{self.r:02x}{self.g:02x}{self.b:02x}{self.a:02x}'


class ColorField(models.CharField):
    description = "A field that stores a hex string representing RGBA color."

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 8
        super().__init__(*args, **kwargs)

    @staticmethod
    def from_db_value(value, _expression, _connection):
        if value is None:
            return value
        return Color.from_hex(value)

    def to_python(self, value):
        if isinstance(value, Color):
            return value
        if value is None:
            return value
        return Color.from_hex(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return value.to_hex()
