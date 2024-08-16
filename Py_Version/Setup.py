from spider_clean import all_update
from spider_clean import one_year_update
from spider_clean import data_clean

from tab_update import tab_update
from pic_update import pic_update
from pic_update import tab_pic_combine
import time
import msvcrt
import sys

# set the colors and fonts
class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = "\033[94m"
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# 下一步开发：detect the csv and png files
# 下一步开发：添加默认配置文件

# initial prompt
print(
    color.BOLD + 
    "    欢迎进入EIA油品数据即时更新系统，请选择任务序号组合进行操作：\n" + 
    color.END + 
    "  1. 全量更新：更新5年EIA油品周度数据，适用首次或当前文件夹中没有数据集时使用，更新速度较慢。\n  2. 1年内的增量更新：更新每年年初至当前时间点的EIA油品周度数据，适用于遗漏更新2周及以上数据的情况下使用，更新速度中等。\n  3. 数据清洗：对1和2中数据获取完成之后的数据进行的清洗。\n  4. 最新1期表格图更新，包含最新1期30个相关指标的变化等。\n  5. 最新1期季节图更新，包含最新1期30个相关指标的季节图。\n  6. 表格图与季节图的合并，对4和5生成的图进行合并。\n  7. 发送生成的图片至指定微信好友或群聊\n"+
    color.YELLOW +
    " 注：\n  (1) 任务1-3进行组合操作使用，任务4-7进行组合操作使用，1-3与4-7之间不建议进行组合操作！！\n  (2) 任务4不更新数据集，任务5更新数据集！！\n  (3) 任务7运行时，请先登录本地微信账号，否则无法运行！！！"+
    color.END
    )

print("\n按Enter键继续，按Esc键直接退出")
while True:
    key = msvcrt.getch()
    if key == b'\r':  # Enter key is represented by b'\r'
        admins = input(
            color.RED + 
            "\n请输入任务序号组合运行（例如，12、456等）："+
            color.END
        )
        admins = list(admins.replace(" ", ""))
        admins = list(set(map(int, admins)))
        while len(admins) < 1:
            admins = input(
                color.RED + 
                "\n请输入任务序号组合运行（例如，12、456等）："+
                color.END
                )
        # list of task
        tasks = [
            all_update, # 全量更新
            one_year_update, # 1年内增量更新
            data_clean, # 数据清洗
            tab_update, # 最新1期表格图更新
            pic_update, # 最新1期季节图更新
            tab_pic_combine # 表格图与季节图的合并
            ]

        # execute selected tasks
        for admin in admins:
            task = tasks[admin-1]()


        print("已完成指定任务！！")
        time.sleep(2)
        sys.exit(0)

    elif key == b'\x1b':  # ESC key is represented by b'\x1b'
        print("\n您已退出！")
        time.sleep(2)
        sys.exit(0)
    else:
        print("按Enter键继续，按Esc键直接退出")
