from uuid import uuid4
from core.constants import constants

def create_graph_config(user_id: str, thread_id: str | None = None):
    return {
        constants.CONFIGURABLE: {
            constants.THREAD_ID: thread_id or str(uuid4()),
            constants.USER_ID: user_id
        }
    }
