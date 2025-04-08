from cachetools import TTLCache
from config import settings

cache = TTLCache(maxsize=1000, ttl=settings.MIN_TTL)
