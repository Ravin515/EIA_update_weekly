from wxauto import WeChat
import os

path = os.getcwd()
path = path.replace("\\", "/")

# print(path)

# 自动发送图片
# 下一步开发：（添加相关自动配置文件）

# 手动发送图片

plot_list = [
    r'/pic/eia_tab.png', 
    r"/pic/eia_pic.png", 
    r"/pic/eia.png"]


plot_no = input("请选择您要发送的图片序号（可多选）1.表格图 2.季节图 3.合并后的图：")

while len(plot_no) < 1:
    plot_no = input("请选择您要发送的图片序号（可多选）1.表格图 2.季节图 3.合并后的图：")

# 只选择一张图
if len(plot_no) == 1:
    files = path + plot_list[int(plot_no) - 1]
    # print(files)

# 选择一张图以上
else:
    plot_no = list(plot_no.replace(" ", ""))
    plot_no = list(set(map(int, plot_no)))
    plot_list = [plot_list[i-1] for i in plot_no]
    files = [
        path + p_list for p_list in plot_list # need absolute path
    ]

whos = input("请输入您要发送的联系人或群名称，多个请用空格分隔：").split()
wx = WeChat()
for who in whos:
    # print(who)
    wx.SendFiles(filepath = files, who = who)

print("图片发送完成！！")