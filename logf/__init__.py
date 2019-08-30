import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s][%(name)s %(asctime)s]:%(message)s',
    # filename='default_log.log',
    filemode='a',
    stream=sys.stderr
    )

logger = logging.getLogger('default_logger')
