# GBA / NDS 游戏封面库

为个人模拟器游戏库整理的封面集合，按你提供的 ROM 文件名对应，共 **43 款游戏：GBA 25 款、NDS 18 款**。本仓库只保存封面图片，不包含 ROM 或汉化补丁。

## 目录结构

| 目录 | 内容 |
|---|---|
| [GBA/](GBA/) | 25 张 GBA 原比例封面，原图保留 |
| [GBA_Square/](GBA_Square/) | GBA 方形封面总目录，里面分为 Original/ 和 Cropped/ |
| [GBA_Square/Original/](GBA_Square/Original/) | 优先放找到的原版正方形盒绘；画面未裁切 |
| [GBA_Square/Cropped/](GBA_Square/Cropped/) | 没有合适原版方图时，从原图选择主体区域裁切 |
| [NDS/](NDS/) | 18 张 NDS 原比例封面，原图保留 |
| [NDS_Square/](NDS_Square/) | NDS 方形封面总目录，里面分为 Original/ 和 Cropped/ |
| [NDS_Square/Original/](NDS_Square/Original/) | 原图为正方形或接近正方形时保留完整画面；特殊替代图会标注 |
| [NDS_Square/Cropped/](NDS_Square/Cropped/) | 从原比例封面中裁出主体区域 |
| [Sources/](Sources/) | **所有封面来源网址、来源文件名、处理类别和方形图路径的集中索引** |
| [Sources/cover_sources.csv](Sources/cover_sources.csv) | GBA + NDS 全部封面的来源清单，可用表格软件打开 |
| [Sources/gba_sources.csv](Sources/gba_sources.csv) | GBA 每张封面的单独来源网址 |
| [Sources/nds_sources.csv](Sources/nds_sources.csv) | NDS 每张封面的单独来源网址 |
| [scripts/generate_square_covers.py](scripts/generate_square_covers.py) | 方形封面生成脚本 |
| [.github/workflows/generate-square-covers.yml](.github/workflows/generate-square-covers.yml) | 自动生成流程 |

## 封面分类和来源说明

- **Original（原图未裁切）**：方形版优先使用找到的同一游戏原版 1:1 盒绘；近方形图会保留完整画面并轻微统一尺寸。此分类表示没有裁掉画面，不代表每一张都是官方实体盒绘；社区替代图会在来源表中注明。
- **Cropped（裁切版）**：找不到合适的原版方图时，才使用 SmartCrop.py 内容感知裁切，尽量保住人物和主要视觉元素。算法不能保证正确识别人脸，部分图片仍可能需要人工微调。
- **原图不会被方形处理覆盖**：GBA 原图保存在 GBA/，NDS 原图保存在 NDS/，两套方形版分别存于各自的 Square 子目录中。
- **来源网址集中存放**：根目录的 Sources/ 中有总 CSV 和按平台分开的 CSV。文件同时记录上游网址、仓库原图地址、方形输出地址及处理类型。地区版本可能和汉化 ROM 所标记的地区不同。

## GBA 游戏清单（25 款）

- 阿滋漫画大王Advance
- 纯情房东俏房客Advance - 祝福之钟声
- 公主同盟
- 哈利波特 - 阿兹卡班的逃犯
- 哈利波特 - 魔法石
- 哈利波特 - 消失的密室
- 海绵宝宝 亚特兰蒂斯
- 节奏天国
- 妹妹公主 - RePure
- 魔卡少女樱 小樱牌的迷你游戏
- 拿破仑
- 逆转裁判
- 逆转裁判2
- 逆转裁判3
- 人型电脑天使心GBA - 只属于我的人
- 人鱼恋曲 - Pichi Pichi Pitch
- 塞尔达传说 - 过去的林克&四支剑
- 塞尔达传说 - 缩小帽
- 侠盗猎车手 - 前进
- 星之卡比 - 镜之大迷宫
- 星之卡比 - 梦之泉
- 约束之地 - 利维艾拉
- 侦探神宫寺三郎 - 白影的少女
- 侦探学园Q - 挑战究极诡计!
- 蜘蛛侠 - 纽约之战

## NDS 游戏清单（18 款）

- 爱丽丝梦游仙境
- 北欧女神 负罪者
- 刺客信条2
- 大剑 银眼的魔女
- 盗贼皇女
- 鬼太郎 妖怪大激战
- 欢迎回来！小机器人！开心富裕大扫除！
- 集合！卡比
- 恋爱布丁 恋爱大冒险！
- 绿野仙踪奇遇记
- 美少女梦工场4DS 特别版
- 塞尔达传说 大地的汽笛
- 塞尔达传说 幻影沙漏
- 塞尔达传说四支剑 25 周年纪念版
- 守护甜心！兴高采烈！甜心旋律
- 万能先生的泡妞生活 夜晚把妹实战篇
- 为你而生
- 侠盗车手 血战唐人街

## 来源与版权

GBA 原版封面主要整理自 [Libretro GBA Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)。NDS 封面来源主要为 [Libretro Nintendo DS Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts)。少数游戏用同一作品的其他地区版本；需要替代图时会单独注明。游戏封面、美术和角色版权属于各自权利人。

## 重新生成

仓库中的 GitHub Actions 会在更新 GBA/NDS 原版封面、生成脚本或说明文档后运行。也可以在本地运行：

    python -m pip install Pillow smartcrop
    python scripts/generate_square_covers.py

脚本只处理封面图片，不读写 ROM 文件。
