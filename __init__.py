import sys
from .src.core.global_context import GCT

GCT().set('debug',False)

# from .test.test import test_run
# test_run()
# exit()


# 重置 GCT 单例（解决重启后缓存未释放问题）
GCT.reset_instance()
# 清理缓存
print(GCT().keys())
print('已经清空')

print(sys.platform)
if sys.platform == "android":
    from .app_android.controllers import index
    index.show()
elif sys.platform == "linux":
    from .app_android.controllers import index
    index.show()
elif sys.platform == "ios":
    pass
    # from .controllers.iOS import form_iOS
    # form_iOS.run()
else:
    print("其他平台")