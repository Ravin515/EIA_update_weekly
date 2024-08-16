import polars as pl
import urllib.request as ur
from lxml import etree
import re
import datetime
import time
from random import randint


# 1. 读取页面的csv文件（全量更新近五年）
# 筛选页面中的url
def all_update():
    url = 'https://www.eia.gov/petroleum/supply/weekly/archive/'
    response = ur\
        .urlopen(url)\
        .read()\
        .decode("utf-8")

    html = etree\
        .HTML(response)

    crawl_urls = html\
        .xpath('//div[@class="main_col"]//a/@href')\
        [1:]

    year_int = list(range(datetime.date.today().year - 5, datetime.date.today().year + 1, 1))
    year_str = list(map(str, year_int))

    crawl_clean = []
    for crawl_url in crawl_urls:
        if any(map(crawl_url.__contains__, year_str)):
            crawl_url = re.sub("/wpsr.+", "", crawl_url)
            crawl_url = "https://www.eia.gov" + crawl_url + "/csv/table9.csv"
            crawl_clean.append(crawl_url)
        else:
            pass
    # print(crawl_clean)

    # 将url传输到read_csv进行读取
    def read_eia_csv(self):
        hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
        }
        data = pl.read_csv(self, 
                        encoding = "cp1252", 
                        # storage_options = hdr
                        )
        
        data = data.select(pl.nth(0, 1, 2))
        data = data.unpivot(index = ["STUB_1", "STUB_2"])
        
        return data

    appended_data = []
    for crawl in crawl_clean:
        time.sleep(randint(5, 7))
        appended_data.append(read_eia_csv(crawl))
        print("Reading " + crawl + " Success!")
    appended_data = pl.concat(appended_data)

    appended_data = appended_data.with_columns(
        pl.col("variable")
        .str.strptime(pl.Date, "%m/%d/%y")  # Convert to Date type
        .dt.strftime("%Y-%m-%d")  # Format as string
        .alias("variable")  # Rename the column to 'variable'
    )

    appended_data.write_csv("./data/eia_history.csv")
    print("全量更新成功！！")

# 2. 读取页面的csv文件（增量更新近一年）
def one_year_update():
    url = 'https://www.eia.gov/petroleum/supply/weekly/archive/'
    response = ur\
        .urlopen(url)\
        .read()\
        .decode("utf-8")

    html = etree\
        .HTML(response)

    crawl_urls = html\
        .xpath('//div[@class="main_col"]//a/@href')\
        [1:]

    year_int = list(range(datetime.date.today().year, datetime.date.today().year + 1, 1))
    year_str = list(map(str, year_int))

    crawl_clean = []
    for crawl_url in crawl_urls:
        if any(map(crawl_url.__contains__, year_str)):
            crawl_url = re.sub("/wpsr.+", "", crawl_url)
            crawl_url = "https://www.eia.gov" + crawl_url + "/csv/table9.csv"
            crawl_clean.append(crawl_url)
        else:
            pass
    # print(crawl_clean)

    # 将url传输到read_csv进行读取
    def read_eia_csv(self):
        hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'
        }
        data = pl.read_csv(self, 
                        encoding = "cp1252", 
                        # storage_options = hdr
                        )
        
        data = data.select(pl.nth(0, 1, 2))
        data = data.unpivot(index = ["STUB_1", "STUB_2"])
        
        return data

    appended_data = []
    for crawl in crawl_clean:
        time.sleep(randint(5, 7))
        appended_data.append(read_eia_csv(crawl))
        print("Reading " + crawl + " Success!")
    appended_data = pl.concat(appended_data)

    appended_data = appended_data.with_columns(
        pl.col("variable")
        .str.strptime(pl.Date, "%m/%d/%y")  # Convert to Date type
        .dt.strftime("%Y-%m-%d")  # Format as string
        .alias("variable")  # Rename the column to 'variable'
    )

    eia_history = pl.read_csv("eia_history.csv", encoding = "utf-8")
    eia_history = pl.concat([appended_data, eia_history])
    eia_history = eia_history.unique(maintain_order = True)
    eia_history.to_csv("./data/eia_history.csv")
    print("1年内增量更新成功！！")

# 3. 清洗出相关有用数据
def data_clean():
    eia_history = pl.read_csv("./data/eia_history.csv", encoding="utf-8")

    # eia_history = eia_history\
    #     .drop(columns = ["Unnamed: 0", "Unnamed: 0.1"])\
    #     .drop_duplicates()

    # Filter rows based on STUB_2 content
    eia_history = eia_history.filter(
        pl.col("STUB_2").str.contains(
            "Domestic Production|Percent Utilization|Finished Motor Gasoline|Distillate Fuel Oil|Kerosene-Type Jet Fuel|Residual Fuel Oil|Commercial|Cushing|SPR|Total Stocks|Crude Oil|Operable Capacity|Total Motor Gasoline"
        ) &
        ~pl.col("STUB_2").str.contains("Crude Oil Inputs")
    )

    # Further filter based on STUB_1 and STUB_2 content
    eia_history = eia_history.filter(
        ~(
            pl.col("STUB_1").str.contains("Refiner and Blender") &
            pl.col("STUB_2").str.contains("Adjustment|Commercial")
        )
    ) # 产量筛选

    eia_history = eia_history.filter(
        ~(
            pl.col("STUB_1").str.contains("Stocks") &
            pl.col("STUB_2").str.contains("Crude|Finished Motor Gasoline")
        )
    ) # 库存筛选

    eia_history = eia_history.filter(
        ~(
            pl.col("STUB_1").str.contains("Imports") &
            pl.col("STUB_2").str.contains("Commercial|Imports by SPR|Imports into SPR by Others|Finished Motor Gasoline|Total Imports")
        )
    ) # 进口筛选

    eia_history = eia_history.filter(
        ~pl.col("STUB_1").str.contains("Net Imports")
    )

    names = [
        "美国原油产量（千桶/天）", 
        "美国炼厂运营炼能（千桶/天）", 
        "美国炼厂产能利用率（%）", 
        "美国汽油产量（千桶/天）", 
        "美国航煤产量（千桶/天）", 
        "美国柴油产量（千桶/天）", 
        "美国燃料油产量（千桶/天）", 
        "美国商业原油库存（百万桶）", 
        "美国库欣原油库存（百万桶）", 
        "美国战略原油储备（百万桶）", 
        "美国汽油库存（百万桶）", 
        "美国航煤库存（百万桶）", 
        "美国柴油库存（百万桶）", 
        "美国燃料油库存（百万桶）", 
        "美国原油成品油总库存去除战略储备（百万桶）", 
        "美国原油成品油总库存包含战略储备（百万桶）", 
        "美国原油进口（千桶/天）", 
        "美国汽油进口（千桶/天）", 
        "美国航煤进口（千桶/天）", 
        "美国柴油进口（千桶/天）", 
        "美国燃料油进口（千桶/天）", 
        "美国原油出口（千桶/天）", 
        "美国汽油出口（千桶/天）", 
        "美国航煤出口（千桶/天）", 
        "美国柴油出口（千桶/天）",
        "美国燃料油出口（千桶/天）",
        "美国汽油需求（千桶/天）",
        "美国航煤需求（千桶/天）",
        "美国柴油需求（千桶/天）",
        "美国燃料油需求（千桶/天）"
    ]

    eia_history = eia_history.with_columns(
        pl.Series("name", names * (len(eia_history) // 30))
    )

    eia_history = eia_history.with_columns(
        pl.col("value").str.replace(",", "").cast(pl.Float64)
    )

    eia_history = eia_history.with_columns(
        pl.when(pl.col("name").str.contains("汽油")).then(pl.lit("汽油"))
        .when(pl.col("name").str.contains("柴油")).then(pl.lit("柴油"))
        .when(pl.col("name").str.contains("航煤")).then(pl.lit("航煤"))
        .when(pl.col("name").str.contains("燃料油")).then(pl.lit("燃料油"))
        .otherwise(pl.lit("原油"))
        .alias("sub_title")
    )

    eia_history.write_csv("./data/eia_weekly.csv")
    print("数据清洗完成！！")