

"""
抖音私信 与 留痕
操作
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


def get_random_script(script_str):
    """从话术字符串中随机获取一个话术"""
    if not script_str:
        return ""
    scripts = [s.strip() for s in script_str.split('/') if s.strip()]
    if scripts:
        return random.choice(scripts)
    return ""

def should_trigger(rate):
    """根据概率判断是否触发"""
    if not rate:
        return False
    try:
        rate_num = int(rate)
        return random.randint(1, 100) <= rate_num
    except:
        return False

def msg_footprint(f_w,form_data_json):
    # 1.进入这个用户主页
    # 2.私信
    # 3.留痕
    form_data = json.loads(form_data_json) if form_data_json else {}
    on()

    # 初始化计数器
    counters = {
        'follow': 0,
        'privateMsg': 0,
        'homeLike': 0,
        'homeCollect': 0,
        'homeComment': 0
    }

    # 获取配置的目标次数
    targets = {
        'follow': int(form_data.get('followCount', 0)) if form_data.get('follow') else 0,
        'privateMsg': int(form_data.get('privateMsgCount', 0)) if form_data.get('privateMsg') else 0,
        'homeLike': int(form_data.get('homeLikeCount', 0)) if form_data.get('homeLike') else 0,
        'homeCollect': int(form_data.get('homeCollectCount', 0)) if form_data.get('homeCollect') else 0,
        'homeComment': int(form_data.get('homeCommentCount', 0)) if form_data.get('homeComment') else 0
    }

    # 获取间隔时间
    interval_min = int(form_data.get('intervalMin', 120))
    interval_max = int(form_data.get('intervalMax', 199))

    # 检查是否所有任务都完成了
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


        # 1. 提取需要操作的用户信息
        res_data = AdminClientService().http_get(api='/open/gather/dy/req-mobile-user-footprint', timeout=None)
        if isinstance(res_data, str):
            user_uid = res_data
            uri = Uri.parse(f"snssdk1128://user/profile/{user_uid}")
            it = Intent(Intent.ACTION_VIEW, uri)
            it.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            R.context.startActivity(it)

            # 确认用户主页已经打开
            run_sel_s(lambda: Selector(2).desc("私信").type("ImageView").find(),15)

            # 关注操作
            if targets['follow'] > 0 and counters['follow'] < targets['follow']:
                if should_trigger(form_data.get('followRate', 100)):
                    time.sleep(0.5)
                    print('执行关注操作')
                    follow_btn = run_sel_s(lambda: Selector().text("关注").type("TextView").hintText("按钮").clickable(True).find(), 15)
                    if follow_btn:
                        follow_btn.click()
                        counters['follow'] += 1
                        print(f'关注完成 {counters["follow"]}/{targets["follow"]}')
                        random_sleep(2, 5)

            # 私信操作
            if targets['privateMsg'] > 0:
                if counters['privateMsg'] < targets['privateMsg']:
                    if should_trigger(form_data.get('privateMsgRate', 100)):
                        time.sleep(0.5)
                        print('执行私信操作')
                        msg_btn = run_sel_s(
                            lambda: Selector(2).desc("私信").type("ImageView").desc("私信").type(
                                "ImageView").parent(1).clickable(True).find(), 5)
                        if not msg_btn:
                            msg_btn = run_sel_s(
                                lambda: Selector(2).desc("私信").type("TextView").clickable(True).find(), 5)

                        if msg_btn:
                            print('私信 点击私信按钮')
                            msg_btn.click()
                            time.sleep(0.5)
                            input_field = run_sel_s(lambda: Selector(2).type("EditText").clickable(True).find(), 20)
                            if input_field:
                                print('私信 点击输入框')
                                script = get_random_script(form_data.get('privateMsgScript', ''))
                                if script:
                                    input_field.input(script)
                                    time.sleep(0.5)
                                    send_btn = Selector(2).desc("发送").type("ImageView").clickable(True).find()
                                    if send_btn:
                                        print('私信 点击发送')
                                        send_btn.click()
                                        counters['privateMsg'] += 1
                                        print(f'私信完成 {counters["privateMsg"]}/{targets["privateMsg"]}')
                                else:
                                    print('私信 话术为空，跳过')
                            else:
                                print('私信 没找到输入框')
                            random_sleep(2, 5)
                            action.Key.back()
                        else:
                            print('私信按钮没找到')
                    else:
                        print('私信 按照概率跳过')
                else:
                    print('私信次数已完成')

            # 主页视频操作（点赞、收藏、评论）
            do_home_like = targets['homeLike'] > 0 and counters['homeLike'] < targets['homeLike'] and should_trigger(form_data.get('homeLikeRate', 100))
            do_home_collect = targets['homeCollect'] > 0 and counters['homeCollect'] < targets['homeCollect'] and should_trigger(form_data.get('homeCollectRate', 100))
            do_home_comment = targets['homeComment'] > 0 and counters['homeComment'] < targets['homeComment'] and should_trigger(form_data.get('homeCommentRate', 100))

            if do_home_like or do_home_collect or do_home_comment:
                time.sleep(0.5)
                print('执行主页视频操作')
                # 找到首条视频
                video = run_sel_s(lambda: Selector(2).path("/FrameLayout/RecyclerView/View").find(), 15)
                if video:
                    # 进入视频页
                    video.find(Selector(2).click())
                    time.sleep(1)

                    # 主页点赞
                    if do_home_like:
                        like_btn = run_sel_s(lambda: Selector(2).type("LinearLayout").desc("未点赞.*").clickable(True).find(), 15)
                        if like_btn:
                            like_btn.click()
                            counters['homeLike'] += 1
                            print(f'主页点赞完成 {counters["homeLike"]}/{targets["homeLike"]}')
                            random_sleep(1, 3)

                    # 主页收藏
                    if do_home_collect:
                        collect_btn = run_sel_s(lambda: Selector(2).desc("未选中，收藏.*").type("LinearLayout").clickable(True).find(), 15)
                        if collect_btn:
                            collect_btn.click()
                            counters['homeCollect'] += 1
                            print(f'主页收藏完成 {counters["homeCollect"]}/{targets["homeCollect"]}')
                            random_sleep(1, 3)

                    # 主页评论
                    if do_home_comment:
                        comment_input = Selector(2).type("EditText").clickable(True).find()
                        if comment_input:
                            comment_input_rect = comment_input.rect
                            action.Touch.down(comment_input_rect.centerX(), comment_input_rect.centerY())
                            action.Touch.up(comment_input_rect.centerX(), comment_input_rect.centerY())
                            comment_input = run_sel_s(lambda: Selector(2).type("EditText").clickable(True).find(), 15)
                            if comment_input:
                                script = get_random_script(form_data.get('homeVideoCommentScript', ''))
                                if script:
                                    time.sleep(0.5)
                                    comment_input.input(script)
                                    time.sleep(1)
                                    send_btn = run_sel_s(lambda: Selector(2).text("发送").type("TextView").parent(1).clickable(True).click().find(), 15)
                                    if send_btn:
                                        counters['homeComment'] += 1
                                        print(f'主页评论完成 {counters["homeComment"]}/{targets["homeComment"]}')

                    # 返回用户主页
                    action.Key.back()
                    random_sleep(2, 5)

            # 每轮间隔
            random_sleep(interval_min, interval_max)

        else:
            t_sleep(2)

    # 任务完成，判断是否关闭app
    if form_data.get('closeApp'):
        print('任务完成，关闭app')
        system_exit()
    else:
        print('任务完成，退出循环')
    pass