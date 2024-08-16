import polars as pl
import numpy as np
from datetime import datetime as dt


# 4. 最新一期表格图更新
def tab_update():
    eia_update = (
        pl.read_csv("https://ir.eia.gov/wpsr/table9.csv",
                    encoding = "cp1252")
        )

    date = (
        "EIA周度数据 "
        + dt.strptime(eia_update.columns[2], "%m/%d/%y")
            .date()
            .strftime("%Y-%m-%d")
        )
    
    eia_update = eia_update.select([
        pl.nth(0).alias("STUB_1"),
        pl.nth(1).alias("STUB_2"),
        pl.nth(2).alias("本期"),
        pl.nth(3).alias("上期")
    ])

    eia_update = eia_update.with_columns([
        pl.col("本期").str.replace(",", "").alias("本期"),
        pl.col("上期").str.replace(",", "").alias("上期")
    ])

    eia_update = eia_update.with_columns(
        pl.col("本期").str.replace("–|– –", np.nan).cast(pl.Float64, strict = False).alias("本期"),
        pl.col("上期").str.replace("–|– –", np.nan).cast(pl.Float64, strict = False).alias("上期")
    )


    eia_update = eia_update.with_columns(
        (pl.col("本期") - pl.col("上期")).alias("变化")
    )

    # filter all the data
    eia_update = eia_update.filter(
        pl.col("STUB_2").str.contains(
            "Domestic Production|Percent Utilization|Finished Motor Gasoline|Distillate Fuel Oil|Kerosene-Type Jet Fuel|Residual Fuel Oil|Commercial|Cushing|SPR|Total Stocks|Crude Oil|Operable Capacity|Total Motor Gasoline"
        ) &
        ~pl.col("STUB_2").str.contains("Crude Oil Inputs")
    )

    eia_update = eia_update.filter(
        ~(
            pl.col("STUB_1").str.contains("Refiner and Blender") &
            pl.col("STUB_2").str.contains("Adjustment|Commercial")
        )
    ) # 产量筛选

    eia_update = eia_update.filter(
        ~(
            pl.col("STUB_1").str.contains("Stocks") &
            pl.col("STUB_2").str.contains("Crude|Finished Motor Gasoline")
        )
    ) # 库存筛选

    eia_update = eia_update.filter(
        ~(
            pl.col("STUB_1").str.contains("Imports") &
            pl.col("STUB_2").str.contains("Commercial|Imports by SPR|Imports into SPR by Others|Finished Motor Gasoline|Total Imports")
        )
    ) # 进口筛选

    eia_update = eia_update.filter(
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

    eia_update = eia_update.with_columns(
        pl.Series("name", names).alias("name")
    )
    eia_update = eia_update.select(pl.nth(2, 3, 4, 5))

    eia_update = eia_update.with_columns(
        pl.when(pl.col("name").str.contains("汽油")).then(pl.lit("汽油"))
        .when(pl.col("name").str.contains("柴油")).then(pl.lit("柴油"))
        .when(pl.col("name").str.contains("航煤")).then(pl.lit("航煤"))
        .when(pl.col("name").str.contains("燃料油")).then(pl.lit("燃料油"))
        .otherwise(pl.lit("原油"))
        .alias("sub_title")
    )

    eia_update = eia_update.sort(["sub_title", "name"])

    eia_update = eia_update.select(
        pl.col("sub_title"),
        pl.col("name"), 
        pl.col("本期"), 
        pl.col("上期"), 
        pl.col("变化")
    )

    eia_update = eia_update.to_pandas().set_index(["sub_title", "name"])
    eia_update.index = eia_update.index.set_names(["", ""])
    eia_update = eia_update.round(2)
    
    import dataframe_image as dfi
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

    dfi.export(eia_update_style, "./pic/eia_tab.png")
    print("最新1期表格更新成功！！")