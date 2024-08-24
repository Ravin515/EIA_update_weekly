from spider_clean import all_update
from spider_clean import one_year_update
from spider_clean import data_clean
from tab_update import tab_update
from pic_update import pic_update
from pic_update import tab_pic_combine
from wechat_send import sending_pics
import configparser
import time
import msvcrt
import sys
import os
import polars as pl
import datetime
import requests
from lxml import html 
import locale
locale.setlocale(locale.LC_ALL, 'C')

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

# 下一步开发：detect the csv
# 数据集个数检测，最终给与提示
path_data = os.getcwd().replace("\\", "/") + "/data"
data_list = os.listdir(path_data)
data_detect = pl.read_csv("./data/eia_weekly.csv")
detect_date = (
    data_detect
        .select(
            pl.col("variable")
                .max()
                .str.strptime(pl.Date)
            )
        .to_series()
        .to_list()[0]
) + datetime.timedelta(days=7)
detect_week = (
    data_detect
        .select(
            pl.col("variable")
                .max()
                .str.strptime(pl.Date)
                .dt.week()
            )
        .to_series()
        .to_list()[0]
)
now_week = datetime.date.today().isocalendar().week

if "eia_history.csv" not in data_list:
    print("未在data文件夹中检测到历史数据，建议首先进行任务1+任务3操作！")
elif now_week - detect_week > 2:
    # 返回下一次的更新时间进一步判断

    next_update_date = requests.get('https://www.eia.gov/petroleum/supply/weekly/')
    next_update_date = html.fromstring(next_update_date.content)
    next_update_date = next_update_date.xpath("/html/body/div[1]/div[2]/div/div[3]/div[1]/div[2]/span[3]/span[2]/text()")[0].replace(".", "")
    next_update_date = datetime.datetime.strptime(next_update_date, '%b %d, %Y').strftime("%Y-%m-%d")

    print(
        "可能存在数据中途断更或漏更的情况！！"+
        "\n检测到上次更新数据集的时间在"+ 
        color.YELLOW +
        str(detect_date) + 
        color.END +
        "这周，" +
        "\n下次EIA油品更新时间在" + 
        color.YELLOW +
        str(next_update_date) +
        color.END + "。"
        "\n若中间间隔超过一周以上，中间漏更未超过一次，建议进行任务4+任务5+任务6的操作！"
        "\n若中间间隔超过一周以上，中间漏更超过两次，且未跨年，建议进行任务2+任务3操作!!"+
        "\n若中间间隔超过一年以上或已跨年，建议进行任务1+任务3操作!!"
    )
else:
    pass

# 判定是否存在默认配置
# 存在默认配置
config = configparser.ConfigParser()
config.read("config.ini", encoding = "utf-8")
if config.has_option("Task", "default"):
    admins = config.get("Task", "default").strip()
    print("检测到您已进行默认配置，开始运行任务：" + color.RED + admins + color.END)
    admins = list(admins.replace(" ", ""))
    admins = list(set(map(int, admins)))
    # list of task
    tasks = [
        all_update, # 全量更新
        one_year_update, # 1年内增量更新
        data_clean, # 数据清洗
        tab_update, # 最新1期表格图更新
        pic_update, # 最新1期季节图更新
        tab_pic_combine, # 表格图与季节图的合并
        sending_pics # 图表发送
        ]
    
    # 执行自动任务
    for admin in admins:
        task = tasks[admin-1]()

    print("已完成指定任务！！")
    time.sleep(2)
    sys.exit(0)    

# 不存在默认配置
else:
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
                tab_pic_combine, # 表格图与季节图的合并
                sending_pics # 图表发送
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
