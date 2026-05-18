# 获取屏幕信息
from ascript.android.system import Device
display = Device.display()
# 屏幕宽度
print(display.widthPixels)
# 屏幕高度
print(display.heightPixels)
# 屏幕密度
print(display.density)