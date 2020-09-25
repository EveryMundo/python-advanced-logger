import datetime
import re
from typing import Any

# Try to import the mongodb BSON regex class as an additional regex type
# TODO users should be able to modify RE_TYPE
try:
    from bson import Regex

    RE_TYPE = (re.compile('').__class__, Regex)
except ImportError:
    RE_TYPE = (re.compile('').__class__,)

# Try to import the DjangoJSONEncoder if Django is installed
try:
    from django.core.serializers.json import DjangoJSONEncoder
except ImportError:
    from .django_json_encoder_copy import DjangoJSONEncoder


class AdvancedJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if self._is_regex(o):
            return str(o)
        if isinstance(o, frozenset):
            return str(o)

        return super(AdvancedJSONEncoder, self).default(o)

    @staticmethod
    def _is_regex(a: Any) -> bool:
        return isinstance(a, RE_TYPE)
