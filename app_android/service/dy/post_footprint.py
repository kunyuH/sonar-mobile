"""
抖音帖子留痕
"""
import json
import time
import random

from ascript.android.system import R
from android.content import Intent
from android.net import Uri
from ascript.android.node import Selector
from ascript.android import action
from ascript.android import system
from ascript.android.ui import Dialog

from ....src.service.admin_client_service import AdminClientService
from ....src.utils.tools import check_end, on, t_sleep, run_sel_s, random_sleep, system_exit

POST_FOOTPRINT_COMM_EVENT = 'post_footprint'

def get_random_script(script_str):
    """从话术字符串中随机获取一个话术"""
    if not script_str:
        return ""
    scripts = [s.strip() for s in script_str.split('/') if s.strip()]
    if scripts:
        return random.choice(scripts)
    return ""

def should_trigger(rate):
    if not rate:
        return False
    try:
        return random.randint(1, 100) <= int(rate)
    except:
        return False


def msg_post_footprint(f_w, form_data_json):
    form_data = json.loads(form_data_json) if form_data_json else {}
    on()

    counters = {
        'textComment': 0,
        'emojiComment': 0,
    }

    targets = {
        'textComment': int(form_data.get('textCommentCount', 0)) if form_data.get('textComment') else 0,
        'emojiComment': int(form_data.get('emojiCommentCount', 0)) if form_data.get('emojiComment') else 0,
    }

    interval_min = int(form_data.get('intervalMin', 1))
    interval_max = int(form_data.get('intervalMax', 10))

    def is_all_done():
        for key in targets:
            if targets[key] > 0 and counters[key] < targets[key]:
                return False
        return True

    while check_end() and not is_all_done():
        # 检测是不是没登陆账号
        if Selector(2).text("已阅读并同意.*").type("TextView").clickable(
                True).find():
            print("检测到未登录账号，请先登录账号")
            res = Dialog.confirm('检测到未登录账号，请先登录账号! ')
            if res:
                print("确定")
            else:
                print("取消")
            system_exit()

        # 1. 获取待操作帖子
        res_data = AdminClientService().http_get(api='/open/comm/req-mobile-data',json={
            "comm_event": POST_FOOTPRINT_COMM_EVENT
        }, timeout=None)
        if isinstance(res_data, str):
            post_id = res_data
            uri = Uri.parse(f"snssdk1128://aweme/detail/{post_id}?needlaunchlog=1")
            it = Intent(Intent.ACTION_VIEW, uri)
            it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            R.context.startActivity(it)

            # 确认帖子已经打开
            run_sel_s(lambda: Selector(2).type("EditText").clickable(True).find(), 15)

            do_text_comment = targets['textComment'] > 0 and counters['textComment'] < targets['textComment'] and should_trigger(form_data.get('textCommentRate', 100))
            do_emoji_comment = targets['emojiComment'] > 0 and counters['emojiComment'] < targets['emojiComment'] and should_trigger(form_data.get('emojiCommentRate', 100))

            if do_text_comment or do_emoji_comment:
                comment_input = run_sel_s(lambda: Selector(2).type("EditText").clickable(True).find(), 15)
                if comment_input:
                    comment_input_rect = comment_input.rect
                    action.Touch.down(comment_input_rect.centerX(), comment_input_rect.centerY())
                    action.Touch.up(comment_input_rect.centerX(), comment_input_rect.centerY())
                    time.sleep(1)

                    # 表情图评论（先选表情，选完后面板会收起）
                    if do_emoji_comment:
                        emoji_obg = run_sel_s(lambda: Selector(2).desc("表情").type("ImageView").clickable(True).find(), 20)
                        if emoji_obg:
                            print("找到表情按钮了 开始点击")
                            emoji_obg.click()
                            time.sleep(1)
                            tab_list = run_sel_s(lambda: Selector(2).path("/FrameLayout/RecyclerView/FrameLayout").type("Button").find_all(), 20)
                            if tab_list and len(tab_list) > 1:
                                tab_list[1].click()
                                time.sleep(1)
                            emoji_list = run_sel_s(
                                lambda: Selector(2).desc("点击添加自定义表情, 按钮").brother().clickable(True).find_all(), 20)
                            if emoji_list and len(emoji_list) > 1:
                                print(f"有{len(emoji_list) - 1}个表情")
                                random.choice(emoji_list[1:]).click()
                                time.sleep(1)

                    # 文字评论（表情面板收起后重新获取输入框焦点）
                    if do_text_comment:
                        script = get_random_script(form_data.get('commentScript', ''))
                        if script:
                            comment_input = run_sel_s(lambda: Selector(2).type("EditText").clickable(True).find(), 15)
                            if comment_input:
                                print(f"开始写入评论【{script}】")
                                comment_input.input(script)
                                time.sleep(1)
                            else:
                                print('文字评论 重新获取输入框失败，跳过')
                                do_text_comment = False
                        else:
                            print('文字评论 话术为空，跳过')
                            do_text_comment = False

                    # 发送
                    send_btn = run_sel_s(
                        lambda: Selector(2).text("发送").type("TextView").parent(1).clickable(True).click().find(), 15)
                    if send_btn:
                        if do_text_comment:
                            counters['textComment'] += 1
                            print(f'文字评论完成 {counters["textComment"]}/{targets["textComment"]}')
                        if do_emoji_comment:
                            counters['emojiComment'] += 1
                            print(f'表情评论完成 {counters["emojiComment"]}/{targets["emojiComment"]}')
                        random_sleep(2, 5)
                    else:
                        print('未找到发送按钮，本次跳过计数')
                    action.Key.back()
                else:
                    print('未找到评论输入框')
        else:
            t_sleep(2)

        random_sleep(interval_min, interval_max)

    if form_data.get('closeApp'):
        print('任务完成，关闭app')
        system_exit()
    else:
        print('任务完成，退出循环')