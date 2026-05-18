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

def get_random_script(script_str):
    """从话术字符串中随机获取一个话术"""
    if not script_str:
        return ""
    scripts = [s.strip() for s in script_str.split('/') if s.strip()]
    if scripts:
        return random.choice(scripts)
    return ""
def test_run():
    post_id = '7559593977642863931'
    form_data = {
        "homeVideoCommentScript":"你好"
    }
    uri = Uri.parse(f"snssdk1128://aweme/detail/{post_id}?needlaunchlog=1")
    it = Intent(Intent.ACTION_VIEW, uri)
    it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    R.context.startActivity(it)
    time.sleep(1)

    # 确认帖子已经打开
    run_sel_s(lambda: Selector(2).type("EditText").clickable(True).find(),3)

    comment_input = run_sel_s(lambda: Selector(2).type("EditText").clickable(True).find(),3)
    if comment_input:
        comment_input_rect = comment_input.rect
        action.Touch.down(comment_input_rect.centerX(), comment_input_rect.centerY())
        action.Touch.up(comment_input_rect.centerX(), comment_input_rect.centerY())
        time.sleep(1)
        # 发文字评论
        comment_input = run_sel_s(lambda: Selector(2).type("EditText").clickable(True).find(), 15)
        if comment_input:
            script = get_random_script(form_data.get('homeVideoCommentScript', ''))
            if script:
                print(f"找到评论输入框 开始写入评论【{script}】")
                time.sleep(1)
                comment_input.input(script)
                time.sleep(1)

        # 发表情图
        emoji_obg = run_sel_s(lambda: Selector(2).desc("表情").type("ImageView").clickable(True).find(), 20)
        if emoji_obg:
            print("找到表情按钮了 开始点击")
            emoji_obg.click()
            time.sleep(1)
            run_sel_s(lambda: Selector(2).path("/FrameLayout/RecyclerView/FrameLayout").type(
                    "Button").find_all(), 20)[1].click()
            time.sleep(1)
            emoji_list = run_sel_s(
                lambda: Selector(2).desc("点击添加自定义表情, 按钮").brother().clickable(
                    True).find_all(), 20)
            if emoji_list and len(emoji_list) > 1:
                print(f"有{len(emoji_list) - 1}个表情")
                random.choice(emoji_list[1:]).click()
                # counters['privateMsgEmoji'] += 1
                print(
                    f'表情私信完成 ')
                time.sleep(1)

        # 点击发送
        if comment_input and emoji_obg:
            send_btn = run_sel_s(
                lambda: Selector(2).text("发送").type("TextView").parent(1).clickable(True).click().find(), 15)
            if send_btn:
                print(f'主页评论完成 ')

"""
表情图发送的代码

                                # 表情图私信
                                if do_emoji_msg:
                                    emoji_obg_all = run_sel_s(
                                        lambda: Selector(2).desc("表情").type("ImageView").parent(1).find_all(), 20)
                                    if emoji_obg_all:
                                        print("找到表情按钮了 开始点击")
                                        emoji_obg_all[0].click()
                                        time.sleep(1)
                                        run_sel_s(
                                            lambda: Selector(2).path("/FrameLayout/RecyclerView/FrameLayout").type(
                                                "Button").find_all(), 20)[1].click()
                                        time.sleep(1)
                                        emoji_list = run_sel_s(
                                            lambda: Selector(2).desc("点击添加自定义表情, 按钮").brother().clickable(
                                                True).find_all(), 20)
                                        if emoji_list and len(emoji_list) > 1:
                                            print(f"有{len(emoji_list) - 1}个表情")
                                            random.choice(emoji_list[1:]).click()
                                            counters['privateMsgEmoji'] += 1
                                            print(
                                                f'表情私信完成 {counters["privateMsgEmoji"]}/{targets["privateMsgEmoji"]}')
                                            time.sleep(1)


"""