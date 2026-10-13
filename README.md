# GBA / NDS 游戏封面库

这是一个给个人模拟器游戏列表使用的封面整理仓库。封面文件以对应 ROM 的文件名为基础命名，方便前端自动匹配。

> **本仓库只存放游戏封面、封面来源记录、生成脚本与项目文档，不存放 GBA/NDS ROM 文件、BIOS、汉化补丁或游戏数据。**

目前整理了 **43 款游戏：GBA 25 款、NDS 18 款**。每个平台同时保留原比例封面和独立的 512 × 512 PNG 方形封面。

## 快速入口

| 想做什么 | 打开这里 |
|---|---|
| 查看全部 GBA 原比例封面 | [GBA/](GBA/) |
| 查看全部 NDS 原比例封面 | [NDS/](NDS/) |
| 查看 GBA 原版方图 | [GBA_Square/Original/](GBA_Square/Original/) |
| 查看 GBA 社区方图 | [GBA_Square/Community/](GBA_Square/Community/) |
| 查看 GBA 裁切方图 | [GBA_Square/Cropped/](GBA_Square/Cropped/) |
| 查看 NDS 原版方图 | [NDS_Square/Original/](NDS_Square/Original/) |
| 查看 NDS 社区方图 | [NDS_Square/Community/](NDS_Square/Community/) |
| 查看 NDS 裁切方图 | [NDS_Square/Cropped/](NDS_Square/Cropped/) |
| 查找任意封面的来源网址 | [Sources/cover_sources.csv](Sources/cover_sources.csv) |
| 查看来源记录格式与来源站点 | [Sources/README.md](Sources/README.md) |
| 查看自动生成代码 | [scripts/generate_square_covers.py](scripts/generate_square_covers.py) |
| 查看自动化任务 | [.github/workflows/generate-square-covers.yml](.github/workflows/generate-square-covers.yml) |
| 查看最近自动生成记录 | [GitHub Actions](https://github.com/WuLinLee/rom_cover/actions) |

## 仓库目录结构

```text
rom_cover/
├── GBA/                         # GBA 原比例封面；作为输入源保留
├── GBA_Square/                  # GBA 方形封面生成结果
│   ├── Original/                # 已找到的原版正方形/近方形盒绘
│   ├── Community/               # 玩家或社区专门制作/投稿的方形封面
│   ├── Cropped/                 # 没有更合适方图时，从原比例封面裁切
│   ├── README.md                # GBA 方形分类清单、数量和处理说明
│   └── 原版方图未裁切名单.md     # Original 分类单独清单
├── NDS/                         # NDS 原比例封面；缺图时由脚本按配置下载
├── NDS_Square/                  # NDS 方形封面生成结果
│   ├── Original/
│   ├── Community/
│   ├── Cropped/
│   └── README.md                # NDS 方形分类清单、数量和处理说明
├── Sources/                     # 全项目来源网址与归档说明
│   ├── README.md                # 来源标准、来源站点、版权提示
│   ├── cover_sources.csv        # GBA + NDS 共 43 款的总表
│   ├── gba_sources.csv          # 25 款 GBA 的来源子表
│   └── nds_sources.csv          # 18 款 NDS 的来源子表
├── scripts/
│   └── generate_square_covers.py # 下载/分类/裁切/生成 README 和来源 CSV
├── .github/
│   └── workflows/
│       └── generate-square-covers.yml # GitHub Actions 自动运行配置
├── LICENSE
└── README.md                    # 本项目总说明
```

每个生成目录的子文件夹中也有自己的 README，用于说明该分类的图片清单。脚本生成的图片和 CSV 属于构建结果；不要只改生成结果而不改脚本或来源配置，否则下一次自动运行会重新生成并覆盖手动修改。

## 方形封面分成三类

每款游戏在方形集里只保留一个当前最合适的分类，避免同一封面在三个目录里重复。

### 1. Original — 原版方图

在来源库中找到同一游戏的原版方形或近方形盒绘时优先使用。图片只统一输出尺寸，不裁掉原画面。少数方图可能是同一游戏的其他地区版本；这种情况会在来源总表记录。Original 指原版游戏美术/盒绘，不表示来源 ROM 的地区一定相同。

### 2. Community — 社区制作方图

原版方图不合适或找不到时，查找玩家、爱好者或社区数据库中专门制作/投稿的方形封面。例如 LaunchBox Games Database 的 **Fanart - Box - Front** 条目。它属于非官方社区图片，不应被描述成官方原版盒绘。当前明确收录的社区图会有图片直链和对应作品页面，记录在 [Sources/cover_sources.csv](Sources/cover_sources.csv)。

### 3. Cropped — 从原比例图裁切

只有在没有合适的 Original 或 Community 图时，才从 `GBA/` 或 `NDS/` 的原比例封面选取方形区域。脚本使用开源 [SmartCrop.py](https://github.com/smartcrop/smartcrop.py) 根据画面细节、边缘、饱和度和构图线索挑选窗口。它不是保证正确识别人脸或角色的模型，可能切掉人物、标题或边缘文字；因此仍建议人工检查重要封面。

### 当前整理数量

以下为最后一次生成成功后核对到的 PNG 数量，不含各目录中的 README 文件。

| 平台 | Original | Community | Cropped | 合计 |
|---|---:|---:|---:|---:|
| GBA | 11 | 2 | 12 | 25 |
| NDS | 0 | 1 | 17 | 18 |
| **总计** | **11** | **3** | **29** | **43** |

特殊情况：《塞尔达传说四支剑 25 周年纪念版》属于 DSiWare 下载版，没有找到原版实体 DS 零售盒绘，因此使用了社区替代图，归入 NDS 的 Community 并在来源清单中注明。

## Sources 来源记录是怎么组织的

[Sources/cover_sources.csv](Sources/cover_sources.csv) 是主索引，每款 ROM 对应一行；平台子表方便单独筛选 GBA 或 NDS。表中包括：

- 平台与对应的封面文件名。
- 仓库内原比例封面路径，以及对应方形输出路径。
- 方形分类：`Original`、`Community` 或 `Cropped`。
- 来源文件名、原比例封面来源网址、方形封面直链、来源页面网址。
- 备注，例如地区版本差异、社区图属性或裁切说明。

**来源网址的准确程度也要讲清楚。** 如果确认了具体的上游图片，会给出该图片的直链；如果只确认来源图库而没有确认具体文件，则表格会标明需要复核或链接到图库目录，不把未核实的单张图片说成已确认。图片直链可能随着上游网站维护而变化，所以来源页面通常也一起保留。

来源站点：

- [Libretro GBA Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)：GBA 原比例盒绘库。
- [Libretro Nintendo DS Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts)：NDS 原比例盒绘库。
- [LaunchBox Games Database](https://gamesdb.launchbox-app.com/)：可查游戏图片，也有社区投稿的 Fanart - Box - Front。
- [SmartCrop.py](https://github.com/smartcrop/smartcrop.py)：自动裁切算法。

游戏封面、美术与角色版权属于各自作者、发行商或权利人。此仓库用于个人封面整理与来源记录，不代表拥有图片再发布授权；使用前应遵守各来源站点和权利人的条款。

## 代码和自动生成逻辑

主要入口是 `scripts/generate_square_covers.py`。它会：

1. 读取 `GBA/` 中的现有封面；检查并使用 `NDS/` 中现有封面，只有缺少文件时才尝试从配置来源下载。
2. 对照脚本内的原版方图配置，优先尝试获取已知的原版方图/近方图。
3. 对明确登记的社区方图使用单独的图片直链和来源页面；社区图片不会混到 Original 分类。
4. 其余封面通过 SmartCrop.py 选择裁切区域，输出 512 × 512 PNG。
5. 分别重建两个平台的 `Original/`、`Community/`、`Cropped/` 输出目录和各目录 README。
6. 写入 `Sources/cover_sources.csv`、`gba_sources.csv`、`nds_sources.csv`，同时更新来源说明。

脚本中的主要配置和职责：

| 代码项 | 用途 |
|---|---|
| `SQUARE_ORIGINALS` | 已确认适合方形使用的原版方图/近方图配置 |
| `GBA_SOURCE_MAP`、`NDS_SOURCE_MAP` | ROM 对应名称到上游原比例封面文件的映射 |
| `GBA_COMMUNITY_MAP` | 已确认的 GBA 社区方图直链、作品页面与类型说明 |
| `NDS_COMMUNITY_STEMS`、`NDS_COMMUNITY_PAGES` | 特定 NDS 社区封面的分类标记和来源页面 |
| `crop_square()` | 调用 SmartCrop.py 进行内容感知裁切，失败时退回中心裁切 |
| `generate_nds_square_covers()` | 生成 NDS 三类方形封面与对应 README |
| `write_source_catalogs()` | 重新生成三份 CSV 来源清单 |

GitHub Actions 配置在 `.github/workflows/generate-square-covers.yml`。修改源封面、脚本、README、来源目录或相关输出目录时，会触发重新生成；也可以在 GitHub Actions 页面手动运行 `workflow_dispatch`。工作流会安装 Python 依赖、运行脚本，再提交生成结果。以 `github-actions[bot]` 身份生成的提交不会再次触发同一工作流，避免无限循环。

## 如何更新或加入游戏

### 更新已有封面

1. 把新的原比例封面放到对应的 `GBA/` 或 `NDS/`，并保持它与 ROM 对应的文件名。
2. 如果来源文件或来源网址变化，修改脚本中的映射配置或社区图记录。
3. 提交变更；检查 [Actions 运行记录](https://github.com/WuLinLee/rom_cover/actions) 是否成功。
4. 检查相应的 Square 子目录和 `Sources/cover_sources.csv`，确认分类和网址正确。

### 增加新游戏

- **GBA**：将原比例封面放入 `GBA/`；如需固定的原版方图，在 `SQUARE_ORIGINALS` 登记；如找到社区方图，在 `GBA_COMMUNITY_MAP` 登记直链、作品页面和来源标签。
- **NDS**：在 `NDS_SOURCE_MAP` 登记 ROM 文件名主干与原比例封面的上游文件名/网址。脚本会下载缺失的原比例封面；社区方图还需登记社区分类和对应来源页面。
- **不要手动编辑生成结果来表达长期规则**：`GBA_Square/`、`NDS_Square/`、`Sources/*.csv` 和生成的 README 会由脚本重写。应先修改配置/源图，再运行生成脚本。

## 本地运行

需要 Python 3.12 或兼容版本，以及网络连接（用于下载未缓存的上游封面）。

```bash
python -m pip install Pillow smartcrop
python scripts/generate_square_covers.py
```

脚本会写入/更新 `GBA_Square/`、`NDS/`、`NDS_Square/` 和 `Sources/`。它不会读取、修改或上传 ROM 文件。生成后请检查 Git 工作区差异，并抽查 Original / Community / Cropped 的分类及人物裁切效果。

## 项目文档

- [来源网址和版权说明](Sources/README.md)
- [GBA 方形封面分类清单](GBA_Square/README.md)
- [NDS 方形封面分类清单](NDS_Square/README.md)
- [生成脚本](scripts/generate_square_covers.py)
- [自动化配置](.github/workflows/generate-square-covers.yml)
