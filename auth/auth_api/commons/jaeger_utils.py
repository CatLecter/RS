from functools import wraps

from auth_api.extensions import tracer
from flask import request
from sqlalchemy import event
from sqlalchemy.engine import Engine


def trace(func):
    """Декоратор для трассировки отдельной функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if tracer.active_span is None:
            tracer.start_active_span(operation_name=func.__name__)
            span = tracer.active_span
        else:
            span = tracer.start_span(operation_name=func.__name__)
        span.set_tag("http.request_id", request.headers.get("X-Request-Id"))
        span.log_kv({"args": args, "kwargs": kwargs})
        value = func(*args, **kwargs)
        span.finish()
        return value

    return wrapper


@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    if tracer.active_span is None:
        tracer.start_active_span(operation_name="SQL_QUERY_EXECUTION")
        span = tracer.active_span
    else:
        span = tracer.start_span(operation_name="SQL_QUERY_EXECUTION")
    if request:
        span.set_tag("http.request_id", request.headers.get("X-Request-Id"))
    conn.info.setdefault("jaeger_span", []).append(span)


@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    span = conn.info["jaeger_span"].pop(-1)
    span.log_kv({"Query": statement})
    span.finish()
