import json
import redis

from app.config import REDIS_DB, REDIS_HOST, REDIS_PORT
from app.core.metrics import record_cache_hit, record_cache_miss


redis_client = None
REDIS_AVAILABLE = False


def connect_redis():
    global redis_client, REDIS_AVAILABLE

    if REDIS_AVAILABLE and redis_client is not None:
        return redis_client

    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
    return redis_client


def is_redis_available() -> bool:
    try:
        connect_redis()
        return True
    except Exception:
        global redis_client, REDIS_AVAILABLE
        redis_client = None
        REDIS_AVAILABLE = False
        return False


try:
    connect_redis()
except Exception:
    redis_client = None
    REDIS_AVAILABLE = False


def get_cache(key: str):
    if not is_redis_available():
        record_cache_miss()
        return None
    data = redis_client.get(key)
    if data:
        record_cache_hit()
        return json.loads(data)
    record_cache_miss()
    return None


def set_cache(key: str, value, expire: int = 60):
    if not is_redis_available():
        return
    redis_client.setex(key, expire, json.dumps(value, default=str))


def delete_cache(key: str):
    if not is_redis_available():
        return
    redis_client.delete(key)


def delete_cache_pattern(pattern: str):
    if not is_redis_available():
        return
    keys = list(redis_client.scan_iter(pattern))
    if keys:
        redis_client.delete(*keys)
