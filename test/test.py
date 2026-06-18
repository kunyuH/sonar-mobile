import random
import time

from ascript.android.system import R
from android.content import Intent
from android.net import Uri
from ascript.android.node import Selector
from ascript.android import action
from ascript.android import system
from ascript.android.ui import Dialog

from ..src.utils.tools import run_sel_s
from ..src.core.facade import f_gct
from ..src.utils.tools import system_exit, check_end, get_device_uuid, on, worker_id
from ..src.service.admin_client_service_v2 import AdminClientServiceV2
from ..app_android.service.xhs.note import on_message_note

def test_run():
    on()
    task = {
            "id": 31,
            "scheme_id": 8,
            "status": "processing",
            "error": null,
            "started_at": "2026-05-26T02:15:02.000000Z",
            "completed_at": null,
            "created_at": "2026-05-25T10:27:42.000000Z",
            "updated_at": "2026-05-26T02:15:02.000000Z",
            "deleted_at": null,
            "platform": "xhs",
            "endpoint": "android",
            "keyword": "美食",
            "func": "xhs_gather_note",
            "scheme": {
                "id": 8,
                "user_id": 1,
                "name": "gggggg",
                "alert_negative_threshold": 0,
                "region": [],
                "keywords": [
                    "美食"
                ],
                "limit": 20,
                "exclude": [],
                "check_no_region": true,
                "created_at": "2026-04-30T08:51:33.000000Z",
                "updated_at": "2026-05-26T02:14:51.000000Z",
                "deleted_at": null,
                "platforms": [
                    "xhs"
                ],
                "platform_endpoints": {
                    "xhs": [
                        "pc",
                        "ios",
                        "android"
                    ]
                },
                "sort_by": [
                    "general",
                    "comment_descending",
                    "collect_descending"
                ],
                "note_type": "图文",
                "publish_time": "一天内",
                "search_scope": "未看过"
            }
        }
    task_id = task.get('id', '')
    f_gct().set('task_id', task_id)

    for sort_type in task.get('scheme', {}).get('sort_by', ['general']):
        on_message_note({
            "max_num": task.get('scheme', {}).get('limit', 0),
            "frequency": 0.5,
            "keyword": task.get('keyword', {}),
            "is_shop": False,
            "page": 1,
            "page_size": 10,
            "search_id": '',
            "sort": "general",
            "note_type": 0,
            "ext_flags": [],
            "image_formats": ["jpg", "webp", "avif"],
            "filters": [
                {"tags": [sort_type], "type": "sort_type"},  # 排序依据
                {"tags": [task.get('scheme', {}).get('note_type', '不限')], "type": "filter_note_type"},  # 笔记类型
                {"tags": [task.get('scheme', {}).get('publish_time', '不限')], "type": "filter_note_time"},  # 发布时间
                {"tags": [task.get('scheme', {}).get('search_scope', '不限')], "type": "filter_note_range"},  # 搜索范围
                {"tags": ["不限"], "type": "filter_pos_distance"},  # 位置距离 不做更改 需要用户授权获取当前位置信息
            ]})