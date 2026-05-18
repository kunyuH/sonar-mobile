from .global_context import GCT
from .ttl_cache import TTLCache

def f_t_cache()->TTLCache:
    """
    缓存服务
    :return:
    """
    return TTLCache()

def f_gct()->GCT:
    """
    全局上下文
    :return:
    """
    return GCT()