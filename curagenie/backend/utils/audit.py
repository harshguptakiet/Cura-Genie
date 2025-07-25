try:
    from elasticsearch import Elasticsearch
    import datetime
    es = Elasticsearch(['http://elasticsearch:9200'])
except ImportError:
    es = None
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')

logger = logging.getLogger('curagenie')
logger.setLevel(LOG_LEVEL)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def log_action(user_id, action, details):
    """Log sensitive actions for audit trail."""
    logger.info(f"AUDIT | user_id={user_id} | action={action} | details={details}")

    # Ship logs to Elasticsearch if available
    if es:
        doc = {
            'user_id': user_id,
            'action': action,
            'details': details,
            'timestamp': datetime.datetime.utcnow().isoformat()
        }
        try:
            es.index(index='curagenie-logs', document=doc)
        except Exception:
            pass
