import logging

logger = logging.getLogger(__name__)


def backoff_hdlr(details):
    logger.error(
        "Backing off {wait:0.1f} seconds after {tries} tries "
        "calling function {target} with args {args} and kwargs "
        "{kwargs}".format(**details)
    )
