from datetime import datetime

from pytz import utc

from meetup_integration.models import Event


def do_line_profiler(view=None, extra_view=None):
    import line_profiler

    def wrapper(view):
        def wrapped(*args, **kwargs):
            prof = line_profiler.LineProfiler()
            prof.add_function(view)
            if extra_view:
                [prof.add_function(v) for v in extra_view]
            with prof:
                resp = view(*args, **kwargs)
            prof.print_stats()
            return resp

        return wrapped

    if view:
        return wrapper(view)

    return wrapper


def get_first_upcoming_event():
    current_date = datetime.utcnow().replace(tzinfo=utc)
    return Event.objects.filter(start_date__gte=current_date).\
        earliest("start_date")
