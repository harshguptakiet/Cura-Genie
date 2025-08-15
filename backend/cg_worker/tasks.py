# Proxy module to expose tasks under cg_worker.tasks namespace
# so Celery can import them without colliding with service name
from worker.tasks import *  # noqa: F401,F403
