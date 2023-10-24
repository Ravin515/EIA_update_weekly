# 目前的微信版本适用wxautov1.py
from wxautov1 import *
import time, random

wx = WeChat()
wx.GetSessionList()

#在这里输入添加各位微信的好友或者群名称
whos = ["文件传输助手", 
        # "油品小圈子", 
        ]

msg = "EIA数据已更新"

file = ".\pic\eia.jpg"

for i in whos:
    who = i
    # message = msg
    # time.sleep(random.randint(10, 20))
    wx.ChatWith(who)
    # wx.Search(who)
    # wx.SendMsg(message)
    # time.sleep(random.randint(10, 20))
    wx.SendFiles(file)
    time.sleep(random.randint(10, 20))
    print("end send", i)
    
print("All end send")
