# EIA数据自动更新并发送项目

-   首先安装**R环境**和**python环境**

-   **00_0\_install_packages.R**为相关R包的安装文件，直接点击**00_0\_auto.bat**文件可安装相关包

-   **00_1\_history_web.R**为历史数据更新文件，在数据有较长时间未运行时，可用该文件进行补全，补全范围为距今5年的数据，直接点击**00_1\_auto.bat**可运行。 （注：抓取的网页为<https://www.eia.gov/petroleum/supply/weekly/archive/>，鉴于EIA官网对爬虫的限制，运行速度较慢）

-   **00_2\_update_web.R**为每周数据更新的主文件，主要生成完整的最新数据集（在*data*文件夹中），以及最新的图片（在*pic*文件夹中），点击**00_2\_auto.bat**可运行。（注：EIA周度数据每次第一时间更新都在<https://ir.eia.gov/wpsr/table9.csv>链接中）

-   **00_3\_send_pic.py**，**wxautov1.py**和**wxautov2.py**为python脚本下的微信自动发送脚本，使用时需要将微信聊天窗口打开方可运行，点击**00_3\_auto.bat**可运行。（注：**wxautov1.py**及**wxautov2.py**，均引用自<https://github.com/cluic/wxauto>的开源项目）

> 注意事项：
>
> 1.  安装R之后需要检查电脑环境变量中，R环境下的bin文件中的**Rscript.exe**有没有被添加，否则上述的bat文件都无法运行，只能通过打开**EIA_update_weekly.Rproj**，在RStudio中对相应文件进行运行。
> 2.  相关的python脚本可能会有失效的问题，最好在python的电脑版更新时进行测试。详情可以关注https://github.com/cluic/wxauto的开源项目
> 3.  相关**.bat**文件可在对应系统的任务管理中进行配置，或针对不同系统进行修改，此处只给出了windows系统的方案。
