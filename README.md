# GBA / NDS 游戏封面库

为个人模拟器游戏库整理的封面集合，按你提供的 ROM 文件名对应，共 **43 款游戏：GBA 25 款、NDS 18 款**。本仓库只保存封面图片，不包含 ROM 或汉化补丁。

## 目录结构

| 目录 | 内容 |
|---|---|
| [GBA/](GBA/) | 25 张 GBA 原比例封面，原图保留 |
| [GBA_Square/](GBA_Square/) | GBA 方形封面，按来源分为三个子文件夹 |
| [GBA_Square/Original/](GBA_Square/Original/) | 找到的原版正方形/近方形盒绘，尽量保留完整画面 |
| [GBA_Square/Community/](GBA_Square/Community/) | 网上的玩家/社区专门制作方形封面，标明图片直链与来源页面 |
| [GBA_Square/Cropped/](GBA_Square/Cropped/) | 没有合适原版方图或社区方图时，从原比例封面裁切 |
| [NDS/](NDS/) | 18 张 NDS 原比例封面，原图保留 |
| [NDS_Square/](NDS_Square/) | NDS 方形封面，按来源分为三个子文件夹 |
| [NDS_Square/Original/](NDS_Square/Original/) | 原版正方形/近方形封面；目前暂无确认的原版方图 |
| [NDS_Square/Community/](NDS_Square/Community/) | 社区制作或投稿的方形封面；会注明非官方状态 |
| [NDS_Square/Cropped/](NDS_Square/Cropped/) | 原版方图与社区方图都找不到时的裁切版本 |
| [Sources/](Sources/) | **来源网址集中目录** |
| [Sources/cover_sources.csv](Sources/cover_sources.csv) | 43 款游戏的来源总表，含原图、方形类别、图片直链和来源网页 |
| [Sources/gba_sources.csv](Sources/gba_sources.csv) | GBA 每款封面的逐张来源 |
| [Sources/nds_sources.csv](Sources/nds_sources.csv) | NDS 每款封面的逐张来源 |
| [Sources/README.md](Sources/README.md) | 来源标注规则、社区图说明和上游来源库 |
| [scripts/generate_square_covers.py](scripts/generate_square_covers.py) | 自动找图下载与方形封面生成脚本 |
| [.github/workflows/generate-square-covers.yml](.github/workflows/generate-square-covers.yml) | GitHub Actions 自动生成流程 |

## 三种方形封面怎么选

优先级是 **Original → Community → Cropped**。

- **Original（原版）**：找到同一游戏的原版方图时优先使用。地区版本可能与本地汉化 ROM 的地区标记不同，但来源会写清楚。
- **Community（社区制作）**：找不到合适的原版方图时，优先寻找玩家投稿/非官方专门制作的正方形封面。此类作品会标明网站、来源页面和图片直链，不冒充官方美术。
- **Cropped（裁切）**：原版方图和合适的社区方图都找不到时，才从原比例封面中裁切主要内容。自动算法不能保证每次都完美保留人物脸部或标题，仍可能需要人工微调。

这三类是按图片来源与处理方式区分的。每款游戏默认只归入当前能找到的最佳类别，避免同一张封面在三个目录中重复；社区作者后来上传更合适的方图时，可以把该游戏从 Cropped 调整到 Community。所有方形输出统一为 512 × 512 PNG，GBA/ 与 NDS/ 的原比例源图不被覆盖。

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

原比例盒绘主要整理自 [Libretro GBA Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts) 和 [Libretro Nintendo DS Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts)。社区方形封面目前从 [LaunchBox Games Database](https://gamesdb.launchbox-app.com/) 的 Fanart - Box - Front 条目选取；具体作品页和图片直链都记录在 [Sources/cover_sources.csv](Sources/cover_sources.csv)。其中《塞尔达传说四支剑 25 周年纪念版》没有实体 DS 版零售盒绘，使用社区替代封面并单独标明。所有封面美术版权属于各自作者及游戏权利人。

## 重新生成

仓库中的 GitHub Actions 会在更新 GBA/NDS 原版封面、生成脚本或说明文档后运行。也可以在本地运行：

    python -m pip install Pillow smartcrop
    python scripts/generate_square_covers.py

脚本只处理封面图片，不读写 ROM 文件。
