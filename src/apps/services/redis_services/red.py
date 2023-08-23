import redis


class RedisClient:
    def __init__(self):
        self.conn = redis.Redis(host="redis", port=6379, decode_responses=True)

    def __del__(self):
        self.conn.close()


redis_client = RedisClient()
