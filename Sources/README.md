# 封面来源网址索引

此目录集中记录每款游戏原比例封面和方形版的来源网址、文件名、处理类别和仓库路径。CSV 可用 Excel、Numbers 或 LibreOffice Calc 打开。

## 文件说明

- [cover_sources.csv](cover_sources.csv)：GBA + NDS 全部 43 款 ROM 的封面来源清单。
- [gba_sources.csv](gba_sources.csv)：25 款 GBA 封面逐张来源。
- [nds_sources.csv](nds_sources.csv)：18 款 NDS 封面逐张来源。

## 方形封面类别

- **Original**：找到同一游戏的原版正方形/近方形盒绘，保留画面，只统一尺寸。
- **Community**：找到社区/玩家提交的方形封面。LaunchBox 图库中的 Fanart - Box - Front 都明确按 fanart 归类，不冒充官方原版盒绘。
- **Cropped**：没有找到合适的原版方图或匹配的社区方图，才从原比例封面裁切。

已确认的社区方图来自 [LaunchBox Games Database](https://gamesdb.launchbox-app.com/)，逐张图片直链和对应游戏图集页都记录在 CSV。地区版可能和汉化 ROM 的地区标记不同。

## 上游来源库

- [Libretro GBA Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)
- [Libretro Nintendo DS Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts)
- [LaunchBox Games Database](https://gamesdb.launchbox-app.com/)，包含社区提交的 Fanart - Box - Front 图片。
- [SmartCrop.py](https://github.com/smartcrop/smartcrop.py)，为剩余没有合适方形来源的封面挑选裁切区域。

图片的版权归原作者和各游戏权利人。仓库保留来源链接用于注明出处；社区作品不代表官方美术，也不等于已获得再发布授权。
