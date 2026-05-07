# Redis
import redis
import os

r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)