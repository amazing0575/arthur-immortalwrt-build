# 京东云亚瑟 RE-SS-01 定制固件

基于 VIKINGYFY/immortalwrt 的 owrt 分支，固定源码提交构建，仅生成亚瑟固件。

首次提交会自动构建用户选定的 OpenClash、PassWall2、HomeProxy、IPv6、UPnP、DDNS、Samba 文件共享，并保留 Wi-Fi。代理自启动关闭，使用时按需启用一个透明代理。

以后在 Actions → Build Arthur Firmware → Run workflow 勾选需要的插件。Wi-Fi、中文 LuCI 和必要驱动固定保留。仓库不包含登录密码、订阅或节点数据。

成功后固件在 Releases；构建日志、配置和核验报告在 Actions Artifacts。检查 verification.json 的 fits_existing_6M_60M_layout；false 表示需要先扩大 GPT 的 rootfs 分区。构建不对路由器执行刷写。

硬件目标：IPQ6000、512 MiB 内存、aarch64_cortex-a53、qualcommax/ipq60xx、jdcloud_re-ss-01。当前设备为 64 GB 档 eMMC，原主内核分区 6 MiB，原主 rootfs 60 MiB。

硬件资料：https://lists.infradead.org/pipermail/lede-commits/2026-January/029021.html

源码：https://github.com/VIKINGYFY/immortalwrt

软件包定制脚本来源：https://github.com/VIKINGYFY/OpenWRT-CI

此仓库不包含上述项目的源码副本，构建时下载各项目；对应代码遵循各自许可证。
