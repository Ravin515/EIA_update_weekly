import pandas as pd
import numpy as np
from datetime import datetime
import dataframe_image as dfi

# import eia data and cleaning
eia_update = pd\
    .read_csv("https://ir.eia.gov/wpsr/table9.csv",
                encoding = "cp1252")

date = "EIA周度数据 "\
        + datetime\
            .strptime(eia_update.columns[2], 
                    "%m/%d/%y")\
            .date()\
            .strftime("%Y-%m-%d")

eia_update = eia_update\
    .iloc[:, :4]\
    .rename(columns = {eia_update.columns[2]:'本期',
                        eia_update.columns[3]:'上期'})

eia_update.iloc[:, 2:4] = eia_update\
    .iloc[:, 2:4]\
    .apply(lambda x: x.str.replace(",", ""))

eia_update = eia_update\
    .replace("–", np.nan)\
    .replace("– –", np.nan)

eia_update.iloc[:, 2:4] = eia_update\
    [eia_update.columns[2:4]]\
    .apply(lambda x: x.astype(float))

eia_update["变化"] = eia_update["本期"] \
                    - eia_update["上期"]

# eia_update["variable"] = pd.to_datetime(eia_update['variable'])

eia_update = eia_update\
    [eia_update["STUB_2"]\
        .str.contains("Domestic Production|Percent Utilization|Finished Motor Gasoline|Distillate Fuel Oil|Kerosene-Type Jet Fuel|Residual Fuel Oil|Commercial|Cushing|SPR|Total Stocks|Crude Oil|Operable Capacity|Total Motor Gasoline") 
    & (~eia_update["STUB_2"]\
        .str.contains("Crude Oil Inputs"))]

eia_update = eia_update\
    [~(eia_update["STUB_1"]\
        .str.contains("Refiner and Blender") \
    & eia_update["STUB_2"]\
        .str.contains("Adjustment|Commercial"))] # 产量筛选

eia_update = eia_update\
    [~(eia_update["STUB_1"]\
        .str.contains("Stocks") \
    & eia_update["STUB_2"]\
        .str.contains("Crude|Finished Motor Gasoline"))] # 库存筛选

eia_update = eia_update\
    [~(eia_update["STUB_1"]\
        .str.contains("Imports")\
    & eia_update["STUB_2"]\
        .str.contains("Commercial|Imports by SPR|Imports into SPR by Others|Finished Motor Gasoline|Total Imports"))] # 进口筛选

eia_update = eia_update\
    [~(eia_update["STUB_1"]\
        .str.contains("Net Imports"))]\
        .reset_index(drop = True)

eia_update["name"] = ["美国原油产量（千桶/天）", 
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
                    "美国燃料油需求（千桶/天）"]

eia_update = eia_update.iloc[:, 2:]
eia_update = eia_update[["name", "本期", "上期", "变化"]]

eia_update["sub_title"] = np.where(
    eia_update["name"].str.contains("汽油"), "汽油",
    np.where(
        eia_update["name"].str.contains("柴油"), "柴油",
        np.where(
            eia_update["name"].str.contains("航煤"), "航煤",
            np.where(
                eia_update["name"].str.contains("燃料油"), "燃料油", "原油"
            )
        )
    )
) 
eia_update = eia_update\
    .sort_values(by = ["sub_title", "name"])

eia_update = eia_update\
    [["sub_title",
    "name", 
    "本期", 
    "上期", 
    "变化"]]\
    .set_index(["sub_title", "name"])

eia_update.index = eia_update.index.set_names(["", ""])
eia_update = eia_update.round(2)

# table visualization
def _color_red_or_green(val):
    if val < 0:
        color = '#69cfd5'
    elif val > 0:
        color = '#feb8cd'
    else:
        color = '#ffffff'
    return 'background-color: %s' % color
styles = [dict(selector="caption",
            props=[("text-align", "right"),
                ("font-size", "150%"),
                ("color", 'black'),
                ("font-weight", "bold")]),
        dict(selector = 'td',
            props = [("text-align", "right")]),
        dict(selector = 'th.level1',
            props = [("text-align", "left")])
        ]

eia_update_style = eia_update\
    .style\
    .set_table_styles(styles)\
    .format("{:.2f}")

eia_update_style = eia_update_style\
    .map(_color_red_or_green, subset = ["变化"])\
    .set_caption(date)

dfi.export(eia_update_style, "eia_tab.png")