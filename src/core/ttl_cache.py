
import threading
import time
from .global_context import GCT

class TTLCache:
    def __init__(self):
        self.cache = GCT()
        self.lock = threading.RLock()

    def set(self, key, value, ttl=None):
        with self.lock:
            cache_data = {
                'data': value,
                'ttl': ttl,
                'expire_at': time.time() + ttl if ttl is not None else None
            }
            self.cache.set(key, cache_data)

    def get(self, key, default=None):
        with self.lock:
            cache_data = self.cache.get(key)
            if cache_data is None:
                return default

            # 检查是否过期
            expire_at = cache_data.get('expire_at')
            if expire_at is not None and time.time() > expire_at:
                # 已过期，删除并返回默认值
                self.cache.delete(key)
                return default

            return cache_data['data']

    def has(self, key):
        with self.lock:
            cache_data = self.cache.get(key)
            if cache_data is None:
                return False

            # 检查是否过期
            expire_at = cache_data.get('expire_at')
            if expire_at is not None and time.time() > expire_at:
                self.cache.delete(key)
                return False

            return True

    def delete(self, key):
        with self.lock:
            self.cache.delete(key)

    def clear(self):
        with self.lock:
            self.cache.clear()

    def size(self):
        # 先清理过期的，再返回数量
        with self.lock:
            keys_to_delete = []
            for key in self.cache.keys():
                cache_data = self.cache.get(key)
                expire_at = cache_data.get('expire_at')
                if expire_at is not None and time.time() > expire_at:
                    keys_to_delete.append(key)

            for key in keys_to_delete:
                self.cache.delete(key)

            return self.cache.size()

    def remember(self, key, ttl, func):
        # 1. 先尝试读取
        value = self.get(key)
        if value is not None:
            return value

        # 2. 没命中，加锁准备写入
        with self.lock:
            # 3. 再次检查，防止在加锁等待期间其他线程已经写好了（双重检查）
            value = self.get(key)
            if value is not None:
                return value

            # 执行函数获取值
            value = func()
            self.set(key, value, ttl)
            return value