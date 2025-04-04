from django.core.serializers.json import DjangoJSONEncoder
from django.utils.duration import duration_iso_string 
from django.utils.functional import Promise 
from django.utils.timezone import is_aware 

import datetime 
import decimal
import uuid 


class JSONEncoder(DjangoJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types, and
    UUIDs.
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            r = o.isoformat() 
            if r.endswith("+00:00"):
                r = r[:-6] + "Z"
            return r 
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r 
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string()
        elif isinstance(o, (decimal.Decimal, uuid.UUID, Promise)):
            return str(o) 
        else:
            return super().default(o)