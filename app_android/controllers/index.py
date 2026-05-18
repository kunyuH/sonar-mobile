import sys
import time
import traceback
import json
import threading

from ascript.android import system
from ascript.android.system import R
from ascript.android.ui import WebWindow
from ascript.android.ui import FloatWindow

from ...src.service.admin_client_service import AdminClientService
from ..service.dy.footprint import msg_footprint
from ..service.dy.post_footprint import msg_post_footprint
from ..service.xhs.comment import on_message_content
from ..service.xhs.note import on_message_note
from ...src.service.auth_service import Auth
from ...src.core.facade import f_gct
from ...src.utils.tools import system_exit, check_end, get_device_uuid, on

# ######################## 心跳 start ###################################
w = None
_heartbeat_stop = threading.Event()
_heartbeat_interval = 60  # 秒

def _do_heartbeat():
    try:
        if Auth().get_super_key():
            print('check auth 心跳')
            Auth().get_key_info(ttl=0)
    except Exception as e:
        traceback.print_exc()
        error_msg = str(e)
        from ascript.android.ui import Dialog
        Dialog.toast(error_msg, 3000)
        _heartbeat_stop.set()
        system_exit()

def _heartbeat_loop():
    while not _heartbeat_stop.is_set():
        # 首次 先执行一次
        _do_heartbeat()
        _heartbeat_stop.wait(timeout=_heartbeat_interval)

def start_heartbeat():
    """启动后台心跳线程（守护线程，随进程退出自动结束）"""
    _heartbeat_stop.clear()
    t = threading.Thread(target=_heartbeat_loop, daemon=True)
    t.start()

def stop_heartbeat():
    _heartbeat_stop.set()
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
            try:
                payload = json.loads(v) if v and v.startswith('{') else {'key': v}
                super_key = payload.get('key', '')
                device_name = payload.get('device_name', '')
                Auth().set_super_key(super_key)
                f_gct().set('device_name', device_name)

                # 启动心跳
                start_heartbeat()

                key_info = Auth().get_key_info()
                roles = key_info.get('roles', {}) if key_info else {}

                roles_json = json.dumps(roles, ensure_ascii=False).replace("'", "\\'")
                w.call("renderPermissions('{}')".format(roles_json))

            except Exception as e:
                traceback.print_exc()
                error_msg = str(e) if str(e) else '验证失败'
                safe_msg = error_msg.replace("'", "\\'")
                w.call("showError('{}')".format(safe_msg))

        elif k == "dy_start_footprint":
            w.call("showLoading('留痕中...')")
            w.close()
            try:
                msg_footprint(f_w=w, form_data_json=v)
            except Exception as e:
                print('留痕执行错误:', e)
                traceback.print_exc()
                from ascript.android.ui import Dialog
                Dialog.toast("抖音留痕执行失败！{}".format(str(e)))

        elif k == "dy_start_post_footprint":
            w.call("showLoading('帖子留痕中...')")
            w.close()
            try:
                msg_post_footprint(f_w=w, form_data_json=v)
            except Exception as e:
                print('帖子留痕执行错误:', e)
                traceback.print_exc()
                from ascript.android.ui import Dialog
                Dialog.toast("抖音帖子留痕执行失败！{}".format(str(e)))
        elif k == "cloud_start":
            on()
            w.close()
            try:
                while check_end():
                    res_str = AdminClientService().http_get(api='/open/comm/req-mobile-data',
                                                             json={
                                                                 "comm_event": f"send_phone:{get_device_uuid()}"
                                                             })
                    if not res_str:
                        time.sleep(1)
                        continue
                    res_data = json.loads(res_str)
                    if res_data.get('func') == 'xhs_gather_comment':
                        on_message_content(res_data.get('option'))
                    elif res_data.get('func') == 'xhs_gather_note':
                        on_message_note(res_data.get('option'))
                        pass

                    time.sleep(1)
            except Exception as e:
                print('帖子留痕执行错误:', e)
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