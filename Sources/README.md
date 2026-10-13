# 封面来源网址索引

本目录集中保存每张封面的来源网址、仓库内原图路径、方形版本路径和处理类型。

## 文件说明

- [cover_sources.csv](cover_sources.csv)：GBA 与 NDS 全部封面合并清单。
- [gba_sources.csv](gba_sources.csv)：25 款 GBA 封面逐张来源。
- [nds_sources.csv](nds_sources.csv)：18 款 NDS 封面逐张来源。

CSV 内的「原比例封面来源网址」与「方形封面来源网址」均可直接打开。若来源文件名为 Libretro 的英文标题，表示采用同一游戏的对应地区盒绘；地区版本可能与本地 ROM 不同。

GBA 原图在仓库的 [GBA/](../GBA/) 中。方形版若有合适的原版方图，则优先使用该原版图；否则从仓库中的原比例封面裁切。NDS 原版盒绘主要来自 Libretro Named Boxarts；《塞尔达传说四支剑 25 周年纪念版》没有零售实体 DS 盒绘，使用社区制作的替代封面，来源及说明已在表格中标注。

## 上游来源库

- [Libretro Nintendo - Game Boy Advance Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)
- [Libretro Nintendo DS Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts)
- [SmartCrop.py 内容感知裁切算法](https://github.com/smartcrop/smartcrop.py)

封面美术版权属于各自权利人。仓库只整理封面，不包含任何 ROM 或汉化补丁。
