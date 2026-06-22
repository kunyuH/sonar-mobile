import sys
import time
import traceback
import json
import threading
import random
import requests

from ascript.android import system
from ascript.android.system import R
from ascript.android.ui import WebWindow
from ascript.android.ui import FloatWindow

from ...src.service.admin_client_service_v2 import AdminClientServiceV2
from ..service.xhs.comment import on_message_content
from ..service.xhs.note import on_message_note
from ...src.service.auth_service import Auth
from ...src.core.facade import f_gct
from ...src.utils.tools import system_exit, check_end, t_sleep, on, app_no, task_done

# 网络重试配置
NETWORK_RETRY_MAX_BACKOFF = 300  # 最长等待间隔（秒）
NETWORK_RETRY_INITIAL = 1        # 初始等待间隔（秒）

# ######################## 心跳 end ###################################

def show():
    try:
        global w
        w = WebWindow(R.ui("index.html"), tunnel=tunnel)
        w.size(width="90vw", height="80vh")
        w.show()
    except Exception as e:
        print(e)
        traceback.print_exc()

def tunnel(k, v=None):
    try:
        if k == "check_key":
            payload = json.loads(v) if v and v.startswith('{') else {'key': v}
            super_key = payload.get('key', '')
            device_name = payload.get('device_name', '')
            if super_key != 'aabbcc':
                w.call("showError('客户端标识错误')")
                return
            Auth().set_super_key(super_key)
            f_gct().set('device_name', device_name)
            w.call("showMainPage()")
        elif k == "cloud_start":
            on()
            w.close()

            # 网络重试状态
            net_backoff = NETWORK_RETRY_INITIAL
            network_errors = (requests.exceptions.ConnectionError,
                              requests.exceptions.Timeout,
                              ConnectionError)

            while check_end():
                try:
                    res_data = AdminClientServiceV2().http_get(api='/open/tasks/pop',
                                                             json={
                                                                 "limit": 1,
                                                                 "platform": "xhs",
                                                                 "endpoint": "android",
                                                                 "app_no": app_no()
                                                             })
                except network_errors as e:
                    print(f'网络连接失败，{net_backoff}秒后重试: {e}')
                    t_sleep(min(net_backoff, NETWORK_RETRY_MAX_BACKOFF))
                    net_backoff = min(net_backoff * 2, NETWORK_RETRY_MAX_BACKOFF)
                    continue

                # 请求成功 → 重置退避
                net_backoff = NETWORK_RETRY_INITIAL

                if not res_data:
                    time.sleep(1)
                    continue

                tasks = res_data['tasks']
                system_config = res_data['system_config']
                min_seconds = system_config['collection_interval']['min_seconds']
                max_seconds = system_config['collection_interval']['max_seconds']
                for task in tasks:
                    print(task)
                    task_id = task.get('id', '')
                    # 提取任务id 并放入 便于后续内部使用
                    f_gct().set('task_id', task_id)

                    if task.get('func') == 'xhs_gather_note':
                        for sort_type in task.get('scheme', {}).get('sort_by', ['general']):
                            on_message_note(sort_type, task)

                        # 暂停一会 让平台接收数据
                        t_sleep(5)
                        task_done()
                        # 暂停一下
                        seconds = random.randint(min_seconds, max_seconds)
                        print(f'暂停一下 {seconds} 秒')
                        t_sleep(seconds)

                    elif task.get('func') == 'xhs_gather_comment':
                        on_message_content(task.get('option'))
                        pass

                time.sleep(1)

        elif k == "close":
            system_exit()

    except Exception as e:
        print(e)
        traceback.print_exc()
        safe_msg = str(e).replace("'", "\\'")
        w.call("showError('{}')".format(safe_msg))