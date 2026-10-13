# GBA / NDS 游戏封面库

为个人模拟器游戏库整理的封面集合，按你提供的 ROM 文件名对应，共 **43 款游戏：GBA 25 款、NDS 18 款**。本仓库只保存封面图片，不包含 ROM 或汉化补丁。

## 目录结构

| 目录 | 用途 | 处理规则 |
|---|---|---|
| [GBA/](GBA/) | GBA 原版比例封面 | 保留原图比例，不裁切 |
| [GBA_Square/](GBA_Square/) | GBA 正方形封面 | 512 × 512 PNG；优先使用同一游戏的原版方图，没有合适方图时再裁切 |
| [NDS/](NDS/) | NDS 原版比例封面 | 依照 ROM 名称保存对应游戏的原版盒绘；没有实体盒绘的下载版会标明替代图来源 |
| [NDS_Square/](NDS_Square/) | NDS 正方形封面 | 512 × 512 PNG；原图本身为正方形时不裁画面，否则使用内容感知裁切 |
| [GBA_Square/README.md](GBA_Square/README.md) | GBA 方形图来源清单 | 列出原版方图与自动裁切图 |
| [GBA_Square/原版方图未裁切名单.md](GBA_Square/原版方图未裁切名单.md) | GBA 原版方图名单 | 标记未裁切的封面 |
| [NDS/README.md](NDS/README.md) | NDS 原版封面来源 | 记录来源文件和下载地址 |
| [NDS_Square/README.md](NDS_Square/README.md) | NDS 方形图来源清单 | 标记原图方图与自动裁切图 |
| [scripts/generate_square_covers.py](scripts/generate_square_covers.py) | 生成脚本 | 下载 NDS 原版封面并重新生成两套方形封面 |
| [.github/workflows/generate-square-covers.yml](.github/workflows/generate-square-covers.yml) | GitHub Actions | 更新封面或脚本时自动生成封面 |

## 封面选择规则

1. **先找对应游戏的原版封面。** GBA 封面原图保存在 `GBA/`；NDS 原版比例封面优先取自公开的 Libretro Named Boxarts 图库。地区版本可能与汉化 ROM 的地区标记不同。
2. **原版方图优先。** 如果来源本身就是正方形，则不裁切画面，只统一输出尺寸。
3. **找不到正方形原版封面才裁切。** 使用开源 [SmartCrop.py](https://github.com/smartcrop/smartcrop.py) 选择方形区域，尽量突出人物或主体。它不是保证正确识别人脸的 AI 模型，偶尔仍可能切掉人物、标题或边缘内容。
4. **原始比例封面不被方形处理覆盖。** 所有方形版分别保存在 `GBA_Square/` 或 `NDS_Square/`。
5. **特殊情况会注明。** 《塞尔达传说四支剑 25 周年纪念版》是 DSiWare 下载版，没有原版实体 DS 盒绘；方形集使用了社区制作的替代封面，并在来源清单中明确标记，不冒充官方原版盒绘。

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
