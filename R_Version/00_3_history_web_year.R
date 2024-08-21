library(data.table)
library(stringr)
library(rvest)
url <- 'https://www.eia.gov/petroleum/supply/weekly/archive/'
urlpage <- read_html(url)
fread_sleep <- function(x, ...){
  Sys.sleep(5)
  fread(x, ...)
}
# 1. Retrive last 1-year data: table9.csv and save the list data
eia_web_update <- 
  data.table(
      url_part =  
          html_nodes(
          urlpage, 
          xpath = '//div[@class="main_col"]//a'
      ) |> 
      html_attr("href")
  )
eia_web_update <- 
  eia_web_update[
    !is.na(url_part), 
    .SD[-1]
  ][, 
    url_part := 
      str_replace(
      url_part, "/wpsr(.+)php", ""
      )
  ][, 
    url_part := 
      str_c(
        "https://www.eia.gov", 
        url_part, 
        "/csv/table9.csv"
      )
  ][
    str_detect(
      url_part, 
      paste((year(Sys.Date())-1):year(Sys.Date()), 
        collapse = "|")
    ), 
    .SD
  ][, 
    .(data = 
      fread_sleep(
        url_part, 
        encoding = "UTF-8"
      ) %>% 
      list()), 
    by = .(url_part)
  ]

load("./data/eia_web_history.Rdata")

eia_web <- rbindlist(list(eia_web, eia_web_update)) |> unique()

save(
  eia_web, 
  file = "./data/eia_web_history.Rdata"
)

# 2. Clean for all data
load("./data/eia_web_history.Rdata")
eia_weekly_clean <- function(x) {
  x[!str_detect(STUB_2, "PADD")
      ][
        str_detect(
          STUB_2, 
          "Domestic Production|Percent Utilization|Finished Motor Gasoline|Distillate Fuel Oil|Kerosene-Type Jet Fuel|Residual Fuel Oil|Commercial|Cushing|SPR|Total Stocks|Crude Oil|Operable Capacity|Total Motor Gasoline"
          ), 
        .SD
      ][
        (str_detect(STUB_1, "Crude")) |
        (str_detect(STUB_1, "Refiner Inputs")) |
        (
          str_detect(STUB_1, "Refiner and Blender") &
          !str_detect(STUB_2, "Adjustment|Commercial")
        ) |
        (
          str_detect(STUB_1, "Stocks") & 
          !str_detect(STUB_2, "Crude")) |
        (
          str_detect(STUB_1, "Imports") & 
          str_detect(STUB_2, "Total Motor Gasoline|Distillate Fuel Oil|Kerosene-Type Jet Fuel|Residual Fuel Oil|Crude")
        ) |
        (str_detect(STUB_1, "Exports")) |
        (str_detect(STUB_1, "Supplied"))
        
      ][
        !str_detect(STUB_1, "Net Imports") & 
        !str_detect(STUB_2, "Crude Oil Inputs")
      ][
        !(str_detect(STUB_1, "Stock") & 
        str_detect(STUB_2, "Finished Motor Gasoline"))
      ][, 
        name := 
          c(
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
          )
      ][, 
        sub_title := 
          fcase(
            str_detect(name, "汽油"), "汽油",
            str_detect(name, "柴油"), "柴油",
            str_detect(name, "航煤"), "航煤",
            str_detect(name, "燃料油"), "燃料油",
            default = "原油"
          )  
      ][, .SD, .SDcols = c(10, 9, 3, 4)
      ][, .SD, .SDcols = 2:3
      ][, 
        melt(
          .SD, 
          id = 1, 
          measure = 2, 
          value.factor = F
        )
      ][, 
        setnames(.SD, 2, "date")
      ][, 
        date := 
          as.character(date) %>% 
          as.Date("%m/%d/%y")
      ][, 
        ':='(
          year = year(date),
          month = month(date)
        )
      ][]
}

eia_data_weekly <- eia_web[, 
    lapply(data, eia_weekly_clean) %>% rbindlist(), 
    by = .(url_part)
  ][, 
    url_part := NULL
  ][, 
    value := 
      str_replace_all(value, ",", "") %>%  
      as.numeric()
  ]

save(eia_data_weekly, file = "./data/eia_data_weekly.Rdata")
