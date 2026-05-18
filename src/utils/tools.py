import hashlib
import json
import random
import re
import sys
import threading
import time
import uuid
from datetime import datetime, timedelta
import requests

from ..core.facade import f_gct


def system_exit():
    try:
        from ..service.admin_client_service import AdminClientService
        AdminClientService().http_post(api='/open/key/kick-device', timeout=10)
    except Exception as e:
        print(f'kick_device 失败: {e}')
    if sys.platform == "android":
        from ascript.android import system
        system.exit()
    elif sys.platform == "ios":
        from ascript.ios import system
        system.exit()
    else:
        sys.exit()
def timestamp_to_date(timestamp, fmt='%Y-%m-%d %H:%M:%S'):
    # 如果是10位
    if len(str(timestamp)) == 13:
        timestamp = timestamp / 1000
    # 将10位时间戳转换为datetime对象
    dt = datetime.fromtimestamp(timestamp)
    # 格式化日期
    date = dt.strftime(fmt)
    return date

def date_to_timestamp(time_str):
    dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    return int(dt.timestamp())*1000

def generate_guid():
    return str(uuid.uuid4())

def is_json(s):
    if not isinstance(s, str):
        return False
    try:
        obj = json.loads(s)
        return isinstance(obj, (dict, list))  # 确保是对象或数组
    except json.JSONDecodeError:
        return False

def parse_chinese_time(text):
    now = datetime.now()

    if match := re.match(r"(\d+)分钟前", text):
        minutes = int(match.group(1))
        dt = now - timedelta(minutes=minutes)
    elif text.startswith("刚刚"):
        dt = now
    elif match := re.match(r"(\d+)小时前", text):
        hours = int(match.group(1))
        dt = now - timedelta(hours=hours)
    elif match := re.match(r"(\d+)天前", text):
        days = int(match.group(1))
        dt = now - timedelta(days=days)
    elif text.startswith("昨天"):
        time_part = text.replace("昨天", "").strip()
        if time_part:
            try:
                time_obj = datetime.strptime(time_part, "%H:%M")
                dt = datetime(now.year, now.month, now.day, time_obj.hour, time_obj.minute) - timedelta(days=1)
            except:
                dt = now - timedelta(days=1)
        else:
            dt = now - timedelta(days=1)
    elif re.match(r"^\d{2}:\d{2}$", text):  # HH:MM 格式，当天时间
        time_obj = datetime.strptime(text, "%H:%M")
        dt = datetime(now.year, now.month, now.day,
                      time_obj.hour, time_obj.minute)
    elif re.match(r"\d{2}-\d{2}$", text):  # MM-DD
        dt = datetime.strptime(f"{now.year}-{text}", "%Y-%m-%d")
    elif re.match(r"\d{4}-\d{2}-\d{2}", text):  # YYYY-MM-DD
        dt = datetime.strptime(text, "%Y-%m-%d")
    else:
        return None  # 不识别的格式

    return dt.strftime("%Y-%m-%d %H:%M:%S")

is_end_key = 'sys_is_end_key'
def off():
    f_gct().remove(is_end_key)
    f_jump_sleep()

def on():
    f_gct().set(is_end_key, True)

def check_end():
    if f_gct().get(is_end_key) is None:
        return False
    return f_gct().get(is_end_key)

def out_info(msg):
    from ..service.admin_client_service import AdminClientService
    AdminClientService().http_post(api='/open/comm/res-mobile-data',data={
        "type": "log_info",
        "msg": msg,
        "comm_event": f"send_phone:{get_device_uuid()}",
    })
def out_error(msg):
    from ..service.admin_client_service import AdminClientService
    AdminClientService().http_post(api='/open/comm/res-mobile-data', data={
        "type": "log_error",
        "msg": msg,
        "comm_event": f"send_phone:{get_device_uuid()}",
    })
def out_success(msg):
    from ..service.admin_client_service import AdminClientService
    AdminClientService().http_post(api='/open/comm/res-mobile-data', data={
        "type": "log_success",
        "msg": msg,
        "comm_event": f"send_phone:{get_device_uuid()}",
    })
def out_warning(msg):
    from ..service.admin_client_service import AdminClientService
    AdminClientService().http_post(api='/open/comm/res-mobile-data', data={
        "type": "log_warning",
        "msg": msg,
        "comm_event": f"send_phone:{get_device_uuid()}",
    })

def send(data):
    """
    发送消息（兼容 WebSocket 和原生 socket）
    - WebSocket: ws.send()
    - Socket: ws.sendall() + \n
    """
    msg = json.dumps(data)
    from ..service.admin_client_service import AdminClientService
    AdminClientService().http_post(api='/open/comm/res-mobile-data', data={
        "type": "done",
        "msg": msg,
        "comm_event": f"send_phone:{get_device_uuid()}",
    })
    # try:
    #     # 尝试使用 sendall (socket)
    #     ws.sendall(msg.encode('utf-8') + b'\n')
    # except AttributeError:
    #     # 如果是 WebSocket 则使用 send
    #     ws.send(msg)

def run_sel(fun, re_time=10, sleep=0.8):

    """
    执行一个函数，直到它返回真值或达到最大重试次数

    参数:
        fun: 要执行的函数
        re_time: 最大重试次数，默认为10
        sleep: 每次重试之间的初始等待时间，默认为0.8秒

    返回:
        如果函数返回真值，则返回该值
        如果达到最大重试次数仍未返回真值，则返回None
    """
    num = 0  # 当前重试次数计数器
    while True:
        time.sleep(sleep)  # 执行前等待指定时间
        if num >= re_time:  # 检查是否达到最大重试次数
            return None  # 达到最大重试次数，返回None
        try:
            a = fun()  # 执行目标函数
            if a:  # 如果函数返回真值
                return a  # 返回函数结果
        except Exception as e:  # 捕获所有异常
            pass  # 忽略异常，继续重试
        num += 1  # 增加重试计数
        time.sleep(0.5)  # 重试后等待0.5秒

def run_sel_s(fun, re_time=1):
    num = 0
    while True:
        if num >= (re_time*10):
            return None
        try:
            a = fun()
            if a:
                return a
        except Exception as e:
            print(f'run_sel_s 异常: {e}')
        num += 1
        time.sleep(0.1)

def random_sleep(min_sec, max_sec):
    sleep_time = random.uniform(min_sec, max_sec)
    t_sleep(sleep_time)

def getLinkToNoteUrl(option=None):
    # 参数组装
    if option is None:
        option = {}
    url = option['url'] if 'url' in option else ''

    res = requests.get(url, allow_redirects=False)  # 不跟随跳转# 默认是 True
    if res.is_redirect or res.status_code in (301, 302, 303, 307, 308):
        redirect_url = res.headers.get('Location')
        return redirect_url

    if 'discovery/item' in res.url or 'user/profile' in res.url:
        return res.url

    if res.history:
        for history in res.history:
            if history.status_code == 302:
                return history.url
    return ''

def getNoteIdByUrl(url):
    """
    从笔记链接中获取笔记ID
    :param url:
    :return:
    """
    return str(url).split("/")[-1].split("?")[0]
def getUserIdByUrl(url):
    """
    从用户链接中获取用户ID
    :param url:
    :return:
    """
    return str(url).split("/")[-1].split("?")[0]

def getUrl(str):
    strs = re.findall(r'https?://[^\s]+', str)
    return strs[0] if strs else None

# 初始化全局锁
events_lock = threading.Lock()
t_sleep_key = 'sys_t_sleep'
events = {}

def t_sleep(seconds):
    """
    延时
    """
    global events
    stop_event = threading.Event()
    event_id = generate_guid()
    # 注册事件（加锁）
    with events_lock:
        events[event_id] = stop_event

    if events[event_id].wait(timeout=seconds):
        with events_lock:
            events.pop(event_id,None)
        raise Exception('强制退出延迟执行', 'jump')
    else:
        with events_lock:
            events.pop(event_id, None)
        pass
def f_jump_sleep():
    """
    可强制退出延迟
    """
    global events
    with events_lock:
        current_events = list(events.values())
    for event in current_events:
        event.set()

def get_device_uuid():
    """获取设备唯一标识 md5之后的"""
    uuid = ''
    try:
        if sys.platform == "android" or sys.platform == "linux":
            from ascript.android.system import Device
            uuid = Device.id()
        elif sys.platform == "ios":
            uuid = ''
    except:
        pass

    if not uuid:
        uuid_cache_key = 'device_uuid_cache'
        uuid = f_gct().get(uuid_cache_key)
        if not uuid:
            uuid = generate_guid()
            f_gct().set(uuid_cache_key, uuid)
    return hashlib.md5(uuid.encode()).hexdigest()