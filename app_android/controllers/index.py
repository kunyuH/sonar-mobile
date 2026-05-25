import sys
import time
import traceback
import json
import threading

from ascript.android import system
from ascript.android.system import R
from ascript.android.ui import WebWindow
from ascript.android.ui import FloatWindow

from ...src.service.admin_client_service_v2 import AdminClientServiceV2
from ..service.xhs.comment import on_message_content
from ..service.xhs.note import on_message_note
from ...src.service.auth_service import Auth
from ...src.core.facade import f_gct
from ...src.utils.tools import system_exit, check_end, get_device_uuid, on, worker_id

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
            try:
                while check_end():
                    res_data = AdminClientServiceV2().http_get(api='/open/tasks/pop',
                                                             json={
                                                                 "limit": 1,
                                                                 "platform": "xhs",
                                                                 "endpoint": "android",
                                                                 "worker_id": worker_id()
                                                             })
                    if not res_data:
                        time.sleep(1)
                        continue
                    for task in res_data:
                        print(task)
                        task_id = task.get('id', '')
                        # 提取任务id 并放入 便于后续内部使用
                        f_gct().set('task_id', task_id)

                        if task.get('func') == 'xhs_gather_note':
                            on_message_note({
                                "max_num": task.get('scheme',{}).get('max_num',0),
                                "keyword": task.get('keyword',{}),
                                        "is_shop": False,
                                        "page": 1,
                                        "page_size": 10,
                                        "search_id": '',
                                        "sort": "general",
                                        "note_type": 0,
                                        "ext_flags": [],
                                        "image_formats": ["jpg", "webp", "avif"],
                                        "filters": [
                                            {"tags": ['general'], "type": "sort_type"},# 排序依据
                                            {"tags": ['不限'], "type": "filter_note_type"},           # 笔记类型
                                            {"tags": ['不限'], "type": "filter_note_time"},           # 发布时间
                                            {"tags": ['不限'], "type": "filter_note_range"},          # 搜索范围
                                            {"tags": ["不限"], "type": "filter_pos_distance"},        # 位置距离 不做更改 需要用户授权获取当前位置信息
                                        ]})
                        elif task.get('func') == 'xhs_gather_comment':
                            on_message_content(task.get('option'))
                            pass

                    time.sleep(1)
            except Exception as e:
                print('云控执行错误:', e)
                traceback.print_exc()
                from ascript.android.ui import Dialog
                Dialog.toast("全自动云控执行失败！{}".format(str(e)))
                system_exit()

        elif k == "close":
            system_exit()

    except Exception as e:
        print(e)
        traceback.print_exc()
        safe_msg = str(e).replace("'", "\\'")
        w.call("showError('{}')".format(safe_msg))