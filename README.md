# GBA ROM 封面库

为个人 GBA 游戏库整理的封面集合，目前包含 **25 款游戏**。原始比例封面与正方形版本分开保存，方便不同模拟器前端使用。

## 目录结构

| 目录 | 用途 | 图片处理 |
|---|---|---|
| [GBA/](GBA/) | 原始封面 | 保留原图比例，不裁切 |
| [GBA_Square/](GBA_Square/) | 方形封面 | 统一为 512 × 512 PNG；优先用原版方图，其余才裁切 |
| [GBA_Square/原版方图未裁切名单.md](GBA_Square/原版方图未裁切名单.md) | **原版方图标记** | 清楚列出哪些封面没有裁切 |
| [GBA_Square/README.md](GBA_Square/README.md) | 完整处理记录 | 标记原版方图和裁切图的全部清单 |
| [scripts/generate_square_covers.py](scripts/generate_square_covers.py) | 方形封面生成脚本 | 使用开源 SmartCrop.py 进行内容感知裁切 |
| [.github/workflows/generate-square-covers.yml](.github/workflows/generate-square-covers.yml) | 自动化流程 | 更新原图或脚本后自动重新生成 |

## 方形封面的处理规则

1. **优先使用原版正方形封面。** 当前已找到的原版方图包括《公主同盟》《哈利波特：阿兹卡班的逃犯》《哈利波特：魔法石》《塞尔达传说：过去的林克＆四支剑》《塞尔达传说：缩小帽》《星之卡比：梦之泉》《星之卡比：镜之大迷宫》和《约束之地：利维艾拉》；《海绵宝宝：亚特兰蒂斯》使用原版近方图，只做轻微比例归一，不裁切。
2. **没有合适的原版方图时才裁切。** 脚本使用开源社区项目 [SmartCrop.py](https://github.com/smartcrop/smartcrop.py) 选择方形窗口。它会综合评估画面细节、边缘、饱和度、肤色线索和构图启发式，比单纯的中心裁切更适合封面；但它不是保证正确识别人脸/角色的 AI 模型，所以结果仍可能有偏差。不会拉伸人物，也不会添加假背景。
3. **原始封面始终保留。** 所有原比例图片都在 GBA/ 中，方形裁切不会覆盖它们。部分图片是自动裁切，并非人工逐张校对；如果某一张主体位置不理想，仍建议看一下原图。

方形版使用同一游戏的其他地区封面时，会在方形目录的来源记录中标明；地区版本可能与本地汉化 ROM 不同。

## 游戏清单

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

## 来源与版权

原始封面主要来自公开的 [Libretro GBA Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts) 图片库。这些是游戏的原版发行封面或盒绘，不是专门制作的中文汉化版封面。封面、美术与角色版权属于各自权利人。本仓库只整理封面图片，不包含 ROM 或汉化补丁。

## 重新生成

推送 GBA/ 中的封面或更新生成脚本后，GitHub Actions 会自动更新 GBA_Square/。也可以在本地运行：

    python -m pip install Pillow smartcrop
    python scripts/generate_square_covers.py

脚本只读取 GBA/，不会覆盖原始封面。
