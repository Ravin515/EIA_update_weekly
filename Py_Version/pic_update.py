# 5. Seasonal picture update
def pic_update():
    import polars as pl
    # import history data
    eia_history = (
        pl.read_csv("./data/eia_weekly.csv",
                encoding = "utf-8")
        )

    # eia_history = eia_history\
    #     .drop(columns = ["Unnamed: 0"])\
    #     .drop_duplicates()

    # read data for the update
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

    eia_update = read_eia_csv("https://ir.eia.gov/wpsr/table9.csv")

    eia_update = eia_update.with_columns(
        pl.col("variable")
        .str.strptime(pl.Date, "%m/%d/%y")  # Convert to Date type
        .dt.strftime("%Y-%m-%d")  # Format as string
        .alias("variable")  # Rename the column to 'variable'
    )


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
    )# 进口筛选

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
        pl.Series("name", names * (len(eia_update) // 30))
    )

    eia_update = eia_update.with_columns(
        pl.col("value").str.replace(",", "").cast(pl.Float64)
    )

    eia_update = eia_update.with_columns(
        pl.when(pl.col("name").str.contains("汽油")).then(pl.lit("汽油"))
        .when(pl.col("name").str.contains("柴油")).then(pl.lit("柴油"))
        .when(pl.col("name").str.contains("航煤")).then(pl.lit("航煤"))
        .when(pl.col("name").str.contains("燃料油")).then(pl.lit("燃料油"))
        .otherwise(pl.lit("原油"))
        .alias("sub_title")
    )

    eia_new = (
        pl.concat([eia_update, eia_history], rechunk=True)
            .unique()
            .sort(by=["sub_title", "name", "variable"])
    )


    eia_new.write_csv("./data/eia_weekly.csv")

    # eia_new = eia_new[eia_new["name"].isnull()]
    # eia_new = eia_new.drop(["name", "sub_title"], axis = 1, inplace = True)


    eia_new = eia_new.with_columns(
        pl.col("variable").str.slice(0, 4).cast(pl.Int32).alias("year")
    )

    eia_new = eia_new.with_columns(
        pl.col("variable").cum_count().cast(pl.Int64).over(["name", "year"]).alias("week")
    )
        
    import datetime
    eia_new = eia_new.filter(
        pl.col("year") >= datetime.date.today().year - 5
    )


    eia_new = eia_new.with_columns(
        pl.col("year").max().alias("now_year")
    ).with_columns(
        pl.col('value').filter(pl.col("year") < pl.col("now_year")).max().over(["name", "week"]).alias("y_max"),
        pl.col('value').filter(pl.col("year") < pl.col("now_year")).min().over(["name", "week"]).alias("y_min")
    )

    eia_new = eia_new.with_columns(
        pl.col("y_max").fill_null(pl.col("value")).alias("y_max"),
        pl.col("y_min").fill_null(pl.col("value")).alias("y_min")
    )

    eia_new = eia_new.filter(
        pl.col("year") >= datetime.date.today().year - 4
    )
    
    # eia_new["y_max"] = eia_new["y_max"].astype("float")
    # eia_new["y_min"] = eia_new["y_min"].astype("float")
    # eia_new["value"] = eia_new["value"].astype("float")
    # eia_new["week"] = eia_new["week"].astype("string")

    # eia_new = eia_new.reset_index(drop = True)
    # eia_new = eia_new.replace([np.inf, -np.inf], np.nan)

    import seaborn as sns
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    # import seaborn.objects as so

    # 画图
    sns.set_theme(font="SimHei")
    sns.color_palette()
    # =============================================================================
    # # seaborn oject module waiting for updating 
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
    eia_new = eia_new.filter(pl.col("year") >= (datetime.date.today().year - 3))
    eia_new = eia_new.to_pandas()
    names = eia_new["name"].unique().tolist()
    eia_new = eia_new.sort_values(by = ["sub_title", "name", "year", "week"])
    eia_new["week"] = eia_new["week"].astype("int64")

    f, axs = plt.subplots(6, 5, figsize=(60, 30))
    axs = axs.flatten()

    for ax, name in zip(axs, names):
        eia = eia_new[(eia_new["name"] == name)]

        # eia["week_int"] = eia.week.astype("int64")
        sns.lineplot(
            ax = ax, 
            x = "week", 
            y = 'value', 
            hue = eia["year"].astype("category"), 
            units = "year", 
            size = "year",
            sizes = ([1, 1, 1, 4]),
            data = eia,
            palette = sns.color_palette("tab10", n_colors = 4)
            ) # 画季节性图
        
        sns.lineplot(
            x = "week", 
            y = "y_min",
            data = eia, 
            color = "grey", 
            alpha = 0,
            ax = ax,
            hue = None
            )
        
        sns.lineplot(
            x = "week", 
            y = "y_max",
            data = eia, 
            color = "grey", 
            alpha = 0,
            ax = ax,
            hue = None
            )

        ax.fill_between(
            x = eia[["week", "y_min", "y_max"]]\
                .drop_duplicates()["week"],
            y1 = eia[["week", "y_min", "y_max"]]\
                .drop_duplicates()['y_min'],
            y2 = eia[["week", "y_min", "y_max"]]\
                .drop_duplicates()['y_max'],
            alpha = 0.3,
            facecolor = '#feb8cd',
            label = "5-year Range"
            )
        
        ax.legend(
            loc='upper center', 
            bbox_to_anchor=(0.5, -0.12),
            fontsize = ("x-large"),
            fancybox=True, 
            shadow=True, 
            ncol=5
            )
        
        ax.set_title(name, fontsize = 20)
        ax.set(xlabel = "周数")
        ax.set(ylabel = None)

    f.tight_layout()
    f.savefig('./pic/eia_pic.png', dpi=100)
    

    print("最新1期季节图更新完成！！")

# 6. bind eia_tab and eia_pic
def tab_pic_combine():
    from PIL import Image
    eia_tab = Image.open("./pic/eia_tab.png")
    eia_tab = eia_tab.resize((1600, 3000))
    # eia_tab.show()
    eia_pic = Image.open("./pic/eia_pic.png")
    # eia_pic.show()
    eia = Image.new('RGB', 
                    (eia_tab.size[0] + eia_pic.size[0], 
                        eia_tab.size[1]))
    eia.paste(eia_tab, (0, 0))
    eia.paste(eia_pic, (eia_tab.size[0], 0))
    # eia.show()
    eia.save("./pic/eia.png")
    print("综合图合并更新完成！！")
