import pandas as pd
import numpy as np
import datetime

# 历史数据
eia_history = pd.read_csv("eia_weekly.csv", encoding = "utf-8")
eia_history = eia_history.drop(columns = ["Unnamed: 0"]).drop_duplicates()

# 新增数据
def read_eia_csv(self):
    hdr = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
    }
    data = pd.read_csv(self, encoding = "cp1252", storage_options = hdr)
    data = data.iloc[:, :3].melt(id_vars = ["STUB_1", "STUB_2"])
    return data
eia_update = read_eia_csv("https://ir.eia.gov/wpsr/table9.csv")
eia_update["variable"] = pd.to_datetime(eia_update["variable"], format = "%m/%d/%y").dt.strftime('%Y-%m-%d')
eia_update = eia_update[eia_update["STUB_2"].str.contains("Domestic Production|Percent Utilization|Finished Motor Gasoline|Distillate Fuel Oil|Kerosene-Type Jet Fuel|Residual Fuel Oil|Commercial|Cushing|SPR|Total Stocks|Crude Oil|Operable Capacity|Total Motor Gasoline") & (~eia_update["STUB_2"].str.contains("Crude Oil Inputs"))]
eia_update = eia_update[~(eia_update["STUB_1"].str.contains("Refiner and Blender") & eia_update["STUB_2"].str.contains("Adjustment|Commercial"))] # 产量筛选
eia_update = eia_update[~(eia_update["STUB_1"].str.contains("Stocks") & eia_update["STUB_2"].str.contains("Crude|Finished Motor Gasoline"))] # 库存筛选
eia_update = eia_update[~(eia_update["STUB_1"].str.contains("Imports") & eia_update["STUB_2"].str.contains("Commercial|Imports by SPR|Imports into SPR by Others|Finished Motor Gasoline|Total Imports"))] # 进口筛选
eia_update = eia_update[~(eia_update["STUB_1"].str.contains("Net Imports"))].reset_index(drop = True)
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
eia_update["value"] = eia_update["value"].str.replace(",", "").astype("float")
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
eia_new = pd.concat([eia_update, eia_history], sort = True).drop_duplicates().sort_values(by = [ "sub_title", "name", "variable"]).reset_index(drop = True)
eia_new.to_csv("eia_weekly.csv")

# eia_new = eia_new[eia_new["name"].isnull()]
# eia_new = eia_new.drop(["name", "sub_title"], axis = 1, inplace = True)


eia_new["year"] = eia_new["variable"].str.slice(start = 0, stop = 4).astype("int")
eia_new["week"] = eia_new.groupby(["name", "year"]).cumcount() + 1
eia_new = eia_new[eia_new.year >= datetime.date.today().year-5]
eia_new["y_max"] = eia_new[eia_new.year < max(eia_new.year)].groupby(["name", "week"])["value"].transform("max")
eia_new["y_max"] = eia_new.groupby(["name", "week"], group_keys=False)["y_max"].apply(lambda x: x.ffill().bfill())
eia_new["y_min"] = eia_new[eia_new.year < max(eia_new.year)].groupby(["name", "week"])["value"].transform("min")
eia_new["y_min"] = eia_new.groupby(["name", "week"], group_keys=False)["y_min"].apply(lambda x: x.ffill().bfill())
eia_new = eia_new[eia_new.year >= datetime.date.today().year-4]
eia_new["y_max"] = eia_new["y_max"].astype("float")
eia_new["y_min"] = eia_new["y_min"].astype("float")
eia_new["value"] = eia_new["value"].astype("float")
eia_new["week"] = eia_new["week"].astype("string")
eia_new = eia_new.reset_index(drop = True)
eia_new = eia_new.replace([np.inf, -np.inf], np.nan)

import seaborn as sns
import matplotlib.pyplot as plt
import datetime
# import seaborn.objects as so

# 画图
sns.set(font="SimHei")
sns.color_palette()
# =============================================================================
# # seaborn oject module
# custom_palette = sns.color_palette("Paired", 9)
# 
# eia_new["label"] = eia_new["STUB_2"] + " - " + eia_new["STUB_1"]
# eia_new["label"] = eia_new["label"].str.replace("Finished Motor Gasoline", "Total Motor Gasoline")
# eia_new = eia_new.sort_values(by = ["sub_title", "name"])
# 
# p = (
#     so.Plot(eia_new, x="week", y = "value", ymin="y_min", ymax="y_max")
#     .add(so.Band(color = "#feb8cd"))
#     .add(so.Line(), color = "year")
#     .add(so.Dot(), color = "year")
#     .layout(size = (120, 60))
#     .facet("label", wrap = 5)
#     .share(y = False)
#     .label(title = "{}".format)
#     .save("eia_pic.png")
#     # .label(title = n.format())
# )
# 
# =============================================================================

# seaborn base object
eia_new = eia_new[eia_new["year"] >= datetime.date.today().year - 3]
names = eia_new["name"].unique().tolist()

f, axs = plt.subplots(6, 5, figsize=(60, 30))

axs = axs.flatten()
for ax, name in zip(axs, names):
    eia = eia_new[(eia_new["name"] == name)]
    sns.lineplot(ax = ax, x = eia["week"].astype("int64"), 
                 y = 'value', 
                 hue = eia["year"].astype("category"), 
                 units = "year", 
                 data = eia,
                 palette = sns.color_palette("tab10")) # 画季节性图
    
    sns.lineplot(x = eia["week"].astype("int64"), 
                  y = "y_min",
                  data = eia, 
                  color = "grey", 
                  alpha = 0,
                  ax = ax)
    
    sns.lineplot(x = eia["week"].astype("int64"), 
                  y = "y_max",
                  data = eia, 
                  color = "grey", 
                  alpha = 0,
                  ax = ax)
    
    ax.fill_between(x = eia[["week", "y_min", "y_max"]].drop_duplicates()["week"].astype("int64"),
                      y1 = eia[["week", "y_min", "y_max"]].drop_duplicates()['y_min'],
                      y2 = eia[["week", "y_min", "y_max"]].drop_duplicates()['y_max'],
                      alpha = 0.3,
                      facecolor = 'grey',
                      label = "5-year Range")
    
    ax.legend(loc='upper center', 
              bbox_to_anchor=(0.5, -0.12),
              fancybox=True, 
              shadow=True, 
              ncol=5)
    ax.set_title(name, fontsize = 20)
    ax.set(xlabel = "周数")
    ax.set(ylabel = None)
    
f.tight_layout()
f.savefig('eia_pic.png', dpi=100)

from PIL import Image
eia_tab = Image.open("eia_tab.png")
eia_tab = eia_tab.resize((1600, 3000))
# eia_tab.show()
eia_pic = Image.open("eia_pic.png")
# eia_pic.show()
eia = Image.new('RGB', (eia_tab.size[0] + eia_pic.size[0], eia_tab.size[1]))
eia.paste(eia_tab, (0, 0))
eia.paste(eia_pic, (eia_tab.size[0], 0))
# eia.show()
eia.save("eia.png")
