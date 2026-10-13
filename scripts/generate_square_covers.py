#!/usr/bin/env python3
"""Build separate square covers from GBA/ without altering the originals.

Known square original artwork is preferred. Remaining covers use SmartCrop.py,
an open-source content-aware crop scorer. Every output is a 512x512 PNG.
"""
from io import BytesIO
import csv
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import sys

import smartcrop
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "GBA"
DEST = ROOT / "GBA_Square"
DEST_ORIGINAL = DEST / "Original"
DEST_CROPPED = DEST / "Cropped"
SIZE = 512
SOURCES_DIR = ROOT / "Sources"

NDS_SOURCE = ROOT / "NDS"
NDS_DEST = ROOT / "NDS_Square"
NDS_DEST_ORIGINAL = NDS_DEST / "Original"
NDS_DEST_CROPPED = NDS_DEST / "Cropped"
LIBRETRO_NDS_BASE = (
    "https://raw.githubusercontent.com/libretro-thumbnails/"
    "Nintendo_-_Nintendo_DS/master/Named_Boxarts/"
)

# Keyed by the ROM filename stem (without .nds). Prefer matching original box art.
# The final entry is a square community-made cover: Four Swords Anniversary was a
# DSiWare release and does not have a genuine retail DS box cover.
NDS_SOURCE_MAP = {
    "爱丽丝梦游仙境(US)(兔友汉化组)(512Mb)": ("Alice in Wonderland (USA) (En,Fr,Es) (NDSi Enhanced).png", ""),
    "北欧女神 负罪者 V2(JP)(ACG汉化组)(1024Mb)": ("Valkyrie Profile - Toga o Seou Mono (Japan).png", ""),
    "刺客信条2 英文字幕+中文配音最终版(fciq配音小组)(512Mb)": ("Assassin's Creed II - Discovery (USA) (En,Fr,Es) (NDSi Enhanced).png", ""),
    "大剑 银眼的魔女(JP)(CG汉化组)(1024Mb)": ("Claymore - Gingan no Majo (Japan).png", ""),
    "盗贼皇女(JP)(ACG汉化组)(512Mb)": ("Steal Princess - Touzoku Koujo (Japan) [b].png", ""),
    "鬼太郎 妖怪大激战(JP)(CG汉化组)(256Mb)": ("Gegege no Kitarou - Youkai Daigekisen (Japan).png", ""),
    "欢迎回来！小机器人！开心富裕大扫除！ 1.1(JP)(兔友汉化组)(512Mb)": ("Okaeri! Chibi-Robo! - Happy Rich Oosouji! (Japan).png", ""),
    "集合！卡比 v20200227(R4TT补丁版)(简)(JP)(那个汉化组)(512Mb)": ("Atsumete! Kirby (Japan).png", ""),
    "恋爱布丁 恋爱大冒险！(JP)(SOMA汉化组)(256Mb)": ("Koisuru Purin! - Koi wa Daibouken! Dr. Kanmi no Yabou! (Japan).png", ""),
    "绿野仙踪奇遇记 大字体完全汉化v1.1(JP)(OREZERO)(1024Mb)": ("Riz-Zoawd (Japan).png", ""),
    "美少女梦工场4DS 特别版 (繁)全文本汉化版 1.1(JP)(joyful)(1024Mb)": ("Princess Maker 4 - Special Edition (Japan).png", ""),
    "塞尔达传说 大地的汽笛(简)1.1(US)(FCU汉化组和兔友汉化组)(1024Mb)": ("Legend of Zelda, The - Spirit Tracks (USA) (En,Fr,Es).png", ""),
    "塞尔达传说 幻影沙漏 修正版(简)(JP)(巴士汉化组)(512Mb)": ("Zelda no Densetsu - Mugen no Sunadokei (Japan).png", ""),
    "塞尔达传说四支剑 25周年纪念版(简)(Monado汉化组)(108Mb)": ("https://images.launchbox-app.com/074d3405-6de6-48a5-8d51-b03596ae607b.png", "未找到原版零售盒绘；使用社区制作的封面图，不属于官方原版实体盒绘。"),
    "守护甜心！兴高采烈！甜心旋律(JP)(兔友汉化组)(1024Mb)": ("Shugo Chara! - Nori Nori! CharanaRhythm (Japan).png", ""),
    "万能先生的泡妞生活 夜晚把妹实战篇 6.18修正版(JP)(星组)(256Mb)": ("Dekiru Otoko no Mote Life - Yoru no Mote Jissen Hen (Japan).png", ""),
    "为你而生 完整汉化版(EU)(兔友汉化组)(1024Mb)": ("Project Rub (Europe) (En,Ja,Fr,De,Es,It).png", ""),
    "侠盗车手 血战唐人街 1.8(EU)(远离汉化组)(1024Mb)": ("Grand Theft Auto - Chinatown Wars (Europe) (En,Fr,De,Es,It).png", ""),
}
LIBRETRO_BASE = (
    "https://raw.githubusercontent.com/libretro-thumbnails/"
    "Nintendo_-_Game_Boy_Advance/master/Named_Boxarts/"
)

# Exact square and near-square original artworks found in the public GBA box-art set.
# Only GBA_Square/ uses these regional alternatives; GBA/ remains untouched.
# The True flag permits tiny ratio normalization for one naturally near-square original.
SQUARE_ORIGINALS = {
    "公主同盟[狼狼小酷+流星落月](v20100811+NO.56修复)(简)(JP)(256Mb).png":
        ("Yggdra Union - We'll Never Fight Alone (USA).png", False),
    "哈利波特 - 阿兹卡班的逃犯[施珂昱](简)(JP)(128Mb).png":
        ("Harry Potter to Azkaban no Shuujin (Japan).png", False),
    "哈利波特 - 魔法石[shikeyu](v0.1)(简)(64Mb).png":
        ("Harry Potter to Kenja no Ishi (Japan).png", False),
    "海绵宝宝 亚特兰蒂斯[3爻3](简)(45Mb).png":
        ("SpongeBob's Atlantis SquarePantis (USA).png", True),
    "塞尔达传说 - 过去的林克&四支剑[漫游](简)(US)(64Mb).png":
        ("Legend of Zelda, The - A Link to the Past _ Four Swords (USA).png", False),
    "塞尔达传说 - 缩小帽[天使汉化组](日汉最终版v2005SP4)(简)(JP)(128Mb).png":
        ("Legend of Zelda, The - The Minish Cap (USA).png", False),
    "星之卡比 - 梦之泉[伤雪&Sody](简)(JP)(64Mb).png":
        ("Kirby - Nightmare in Dream Land (USA).png", False),
    "星之卡比 - 镜之大迷宫[CGP](简)(JP)(128Mb).png":
        ("Kirby _ The Amazing Mirror (USA).png", False),
    "约束之地 - 利维艾拉[PromisedLand](v1.05)[简](JP)(256Mb).png":
        ("Riviera - The Promised Land (USA).png", False),
}


# Best-matching source entries in Libretro's GBA Named_Boxarts library.
# The entries are source art candidates; local ROM/cover filenames stay unchanged.
GBA_SOURCE_MAP = {
    "阿滋漫画大王Advance[PGCG](简)(JP)(64Mb)": "Azumanga Daiou Advance (Japan).png",
    "纯情房东俏房客Advance - 祝福之钟声[CGP&PGCG](简)(JP)(70.01Mb)": "Love Hina Advance - Shukufuku no Kane wa Naru Kana (Japan).png",
    "公主同盟[狼狼小酷+流星落月](v20100811+NO.56修复)(简)(JP)(256Mb)": "Yggdra Union (Japan).png",
    "哈利波特 - 阿兹卡班的逃犯[施珂昱](简)(JP)(128Mb)": "Harry Potter to Azkaban no Shuujin (Japan).png",
    "哈利波特 - 魔法石[shikeyu](v0.1)(简)(64Mb)": "Harry Potter to Kenja no Ishi (Japan).png",
    "哈利波特 - 消失的密室[施珂昱](简)(JP)(64Mb)": "Harry Potter to Himitsu no Heya (Japan).png",
    "海绵宝宝 亚特兰蒂斯[3爻3](简)(45Mb)": "SpongeBob's Atlantis SquarePantis (USA).png",
    "节奏天国[漫游](简)(JP)(128Mb)": "Rhythm Tengoku (Japan).png",
    "妹妹公主 - RePure[PGCG](繁)(JP)(64Mb)": "Sister Princess - RePure (Japan).png",
    "魔卡少女樱 小樱牌的迷你游戏[卧看微尘](v1.0)(简)(64Mb)": "Cardcaptor Sakura - Sakura Card de Mini Game (Japan).png",
    "拿破仑(12.24最终版)[Advance-002](简)(JP)(72Mb)": "Napoleon (Japan).png",
    "逆转裁判[Jpgmfan&逆转Ace](简)(JP)(66.41Mb)": "Gyakuten Saiban (Japan).png",
    "逆转裁判2[CGP](简)(JP)(77.39Mb)": "Gyakuten Saiban 2 (Japan).png",
    "逆转裁判3[逆转Ace](简)(JP)(69.64Mb)": "Gyakuten Saiban 3 (Japan).png",
    "人型电脑天使心GBA - 只属于我的人[PGCG](简)(JP)(64Mb)": "Chobits for Game Boy Advance - Atashi Dake no Hito (Japan).png",
    "人鱼恋曲 - Pichi Pichi Pitch[千岛&叶子](简)(JP)(136.33Mb)": "Mermaid Melody - Pichi Pichi Pitch (Japan).png",
    "塞尔达传说 - 过去的林克&四支剑[漫游](简)(US)(64Mb)": "Legend of Zelda, The - A Link to the Past _ Four Swords (USA).png",
    "塞尔达传说 - 缩小帽[天使汉化组](日汉最终版v2005SP4)(简)(JP)(128Mb)": "Legend of Zelda, The - The Minish Cap (USA).png",
    "侠盗猎车手 - 前进[Beq & LCPD](Beta) (v20160720)[简](JP)(256Mb)": "Grand Theft Auto Advance (USA).png",
    "星之卡比 - 镜之大迷宫[CGP](简)(JP)(128Mb)": "Kirby _ The Amazing Mirror (USA).png",
    "星之卡比 - 梦之泉[伤雪&Sody](简)(JP)(64Mb)": "Kirby - Nightmare in Dream Land (USA).png",
    "约束之地 - 利维艾拉[PromisedLand](v1.05)[简](JP)(256Mb)": "Riviera - The Promised Land (USA).png",
    "侦探神宫寺三郎 - 白影的少女[CGP](简)(JP)(65.56Mb)": "Tantei Jinguuji Saburou - Shiroi Kage no Shoujo (Japan).png",
    "侦探学园Q - 挑战究极诡计![CGP](简)(JP)(128Mb)": "Tantei Gakuen Q - Kyuukyoku Trick ni Idome! (Japan).png",
    "蜘蛛侠 - 纽约之战[Advance-005](简)(JP)(130.44Mb)": "Spider-Man - Battle for New York (Europe) (En,Fr,De,Es,It).png",
}

def load_square_original(filename):
    entry = SQUARE_ORIGINALS.get(filename.name)
    if not entry:
        return None
    source_name, near_square = entry
    url = LIBRETRO_BASE + quote(source_name, safe="")
    try:
        request = Request(url, headers={"User-Agent": "rom-cover-square-generator"})
        with urlopen(request, timeout=30) as response:
            data = response.read()
        with Image.open(BytesIO(data)) as source_image:
            image = ImageOps.exif_transpose(source_image).convert("RGB")
            width, height = image.size
            ratio = width / height
            if abs(ratio - 1.0) > 0.035:
                print(f"NOTE: {source_name} is not square; saliency crop will be used.")
                return None
            if not near_square and width != height:
                print(f"NOTE: {source_name} is not exactly square; saliency crop will be used.")
                return None
            return image.copy(), source_name, near_square
    except Exception as exc:
        print(f"WARNING: could not fetch square original {source_name}: {exc}", file=sys.stderr)
        return None


def crop_square(image):
    """Use SmartCrop.py to pick a content-aware 1:1 window from a non-square cover."""
    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGBA" if "transparency" in image.info else "RGB")
    width, height = image.size
    if width == height:
        return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)

    side = min(width, height)
    try:
        # SmartCrop.py scores candidate windows using visual detail, edges,
        # saturation, skin-colour likelihood, and composition heuristics.
        analysis = image.convert("RGB")
        result = smartcrop.SmartCrop().crop(analysis, side, side)
        best = result.get("top_crop") or {}
        x = max(0, min(int(best.get("x", (width - side) // 2)), width - 1))
        y = max(0, min(int(best.get("y", (height - side) // 2)), height - 1))
        crop_width = max(1, min(int(best.get("width", side)), width - x))
        crop_height = max(1, min(int(best.get("height", side)), height - y))

        # SmartCrop may choose a slightly smaller or rounded crop. Convert its
        # selected window to a true square around the chosen composition.
        square_side = min(crop_width, crop_height)
        x += max(0, (crop_width - square_side) // 2)
        y += max(0, (crop_height - square_side) // 2)
        cropped = image.crop((x, y, x + square_side, y + square_side))
        return cropped.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    except Exception as exc:
        # Keep batch processing resilient; mark fallback clearly in CI logs.
        print(f"WARNING: SmartCrop failed for one image; using centre crop: {exc}", file=sys.stderr)
        x = (width - side) // 2
        y = (height - side) // 2
        cropped = image.crop((x, y, x + side, y + side))
        return cropped.resize((SIZE, SIZE), Image.Resampling.LANCZOS)



def nds_source_url(source_name):
    """Return the public artwork URL for a Libretro filename or a direct URL."""
    if source_name.startswith(("https://", "http://")):
        return source_name
    return LIBRETRO_NDS_BASE + quote(source_name, safe="")


def sync_nds_originals():
    """Download source cover art into NDS/ while keeping ROM files out of the repo."""
    NDS_SOURCE.mkdir(parents=True, exist_ok=True)
    failures = []
    source_records = []

    for rom_stem, (source_name, note) in NDS_SOURCE_MAP.items():
        target = NDS_SOURCE / (rom_stem + ".png")
        url = nds_source_url(source_name)

        # Keep existing saved originals. Missing files are fetched from the source.
        if not target.exists() or target.stat().st_size == 0:
            last_error = None
            for attempt in range(3):
                try:
                    request = Request(url, headers={"User-Agent": "rom-cover-square-generator"})
                    with urlopen(request, timeout=45) as response:
                        data = response.read()
                    with Image.open(BytesIO(data)) as image:
                        image.verify()
                    target.write_bytes(data)
                    last_error = None
                    break
                except Exception as exc:
                    last_error = exc
            if last_error is not None:
                print(f"ERROR: Could not download NDS cover for {rom_stem}: {last_error}", file=sys.stderr)
                failures.append(rom_stem)
                continue

        source_label = source_name if not source_name.startswith(("https://", "http://")) else source_name
        source_records.append((rom_stem, source_label, note, url))

    lines = [
        "# NDS 原版比例封面来源说明",
        "",
        "此目录保存和 ROM 文件名对应的 NDS 封面 PNG，不包含 ROM 文件。优先使用 Libretro 的原版游戏盒绘；地区版可能和汉化 ROM 的地区标记不同。",
        "",
        "## 封面来源",
        "",
    ]
    for rom_stem, source_name, note, url in source_records:
        status = f" — {note}" if note else " — Libretro Named Boxarts 原版游戏盒绘"
        lines.append(f"- **{rom_stem}.png**：{source_name}{status}")
        lines.append(f"  来源：{url}")
    if failures:
        lines.extend(["", "## 下载失败，需要重试", ""])
        lines.extend(f"- {name}.png" for name in failures)
    lines.extend([
        "",
        "原始封面版权属于各自游戏权利人；本仓库只为个人模拟器封面整理使用。四支剑 25 周年纪念版为 DSiWare 下载版，没有原版实体 DS 盒绘，因此采用社区制作的替代封面并已标明。",
        "",
    ])
    (NDS_SOURCE / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return not failures


def generate_nds_square_covers():
    """Generate NDS_Square/; do not alter the source images in NDS/."""
    image_files = sorted(
        p for p in NDS_SOURCE.iterdir()
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    if not image_files:
        print(f"No NDS cover images found in {NDS_SOURCE}", file=sys.stderr)
        return 0, 0

    NDS_DEST.mkdir(parents=True, exist_ok=True)
    NDS_DEST_ORIGINAL.mkdir(parents=True, exist_ok=True)
    NDS_DEST_CROPPED.mkdir(parents=True, exist_ok=True)
    # Move the old flat-layout set into Original/ and Cropped/ by rebuilding it.
    for stale in NDS_DEST.glob("*.png"):
        stale.unlink()
    for folder in (NDS_DEST_ORIGINAL, NDS_DEST_CROPPED):
        for stale in folder.glob("*.png"):
            stale.unlink()
    uncropped = []
    cropped = []
    made = 0

    for path in image_files:
        try:
            with Image.open(path) as original:
                was_exact_square = original.width == original.height
                ratio_difference = abs(original.width / original.height - 1.0)
                keep_full_image = ratio_difference <= 0.035
                original_size = f"{original.width}×{original.height}"
                if keep_full_image:
                    output = ImageOps.exif_transpose(original).convert(
                        "RGBA" if "A" in original.getbands() else "RGB"
                    ).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
                else:
                    output = crop_square(original.copy())
            source_name, note = NDS_SOURCE_MAP.get(path.stem, ("", ""))
            if keep_full_image and note:
                destination_folder = NDS_DEST_ORIGINAL
                uncropped.append((path.name, original_size, source_name, note, "community", was_exact_square))
            elif keep_full_image:
                destination_folder = NDS_DEST_ORIGINAL
                uncropped.append((path.name, original_size, source_name, note, "original", was_exact_square))
            else:
                destination_folder = NDS_DEST_CROPPED
                cropped.append((path.name, original_size, source_name, note))
            output.save(destination_folder / (path.stem + ".png"), format="PNG", optimize=True)
            made += 1
            print(f"Created NDS_Square/{path.stem}.png")
        except Exception as exc:
            print(f"ERROR: NDS cover {path.name}: {exc}", file=sys.stderr)

    lines = [
        "# NDS 方形封面来源说明",
        "",
        "所有方形封面统一输出为 512 × 512 PNG，文件名与 ROM 对应。原始比例封面保存在 NDS/，不会被覆盖。",
        "",
        "本目录分为两个子文件夹：Original/ 存放画面未裁切的原图方图/近方图（特殊替代图会单独注明）；Cropped/ 存放从原比例封面中选择方形区域的版本。来源网址集中记录在 Sources/cover_sources.csv。",
        "",
        "自动裁切使用开源 SmartCrop.py，根据画面细节和构图线索选择窗口，并不保证每张人物构图都完美，建议重点检查人物脸部和边缘文字。",
        "",
        f"**统计：{sum(1 for item in uncropped if item[5])} 张原图本身为正方形；{sum(1 for item in uncropped if not item[5])} 张为近方形（保留完整画面并轻微统一尺寸）；{len(cropped)} 张从原版比例封面裁切。**",
        "",
        "## Original/：原图未裁切",
        "",
    ]
    for filename, original_size, source_name, note, kind, was_exact_square in uncropped:
        shape_label = "正方形" if was_exact_square else "近方形，轻微统一比例"
        if kind == "community":
            lines.append(f"- `Original/{filename}` — {original_size}；保留{shape_label}社区替代封面。{note}")
        else:
            lines.append(f"- `Original/{filename}` — {original_size}；原图为{shape_label}，输出 512 × 512。来源：{source_name}")
    lines.extend(["", "## Cropped/：内容感知裁切", ""])
    for filename, original_size, source_name, note in cropped:
        lines.append(f"- `Cropped/{filename}` — 原图 {original_size}；从对应原版比例封面裁切。来源：{source_name}")
    lines.extend([
        "",
        "算法来源：[SmartCrop.py](https://github.com/smartcrop/smartcrop.py)。画面自动裁切可能舍弃边缘文字、标志或人物的一部分；如有单张构图不理想，建议针对该图手动调整。",
        "",
    ])
    (NDS_DEST / "README.md").write_text("\n".join(lines), encoding="utf-8")

    return made, len(image_files)



def local_cover_url(folder, filename):
    return "https://raw.githubusercontent.com/WuLinLee/rom_cover/main/" + folder + "/" + quote(filename, safe="")


def write_source_catalogs():
    """Keep a root-level, machine-readable directory of per-cover source URLs."""
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    header = [
        "平台", "原比例封面文件", "仓库原图路径", "方形封面路径", "方形类型",
        "原比例封面来源文件名", "原比例封面来源网址",
        "方形封面来源文件名", "方形封面来源网址", "备注",
    ]
    rows = []

    # GBA cover sources; where the precise upstream title is known, link to it.
    for path in sorted(p for p in SOURCE.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}):
        source_name = GBA_SOURCE_MAP.get(path.stem, "")
        if source_name:
            original_source_url = LIBRETRO_BASE + quote(source_name, safe="")
            note = "匹配 Libretro 对应游戏盒绘；地区封面可能与 ROM 不同。"
        else:
            original_source_url = "https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts"
            note = "已收录原图保存在 GBA/；上游单张文件名未核实，请通过来源库检索。"

        override = SQUARE_ORIGINALS.get(path.name)
        if override:
            square_source_name = override[0]
            square_source_url = LIBRETRO_BASE + quote(square_source_name, safe="")
            note += " 方形版采用同一游戏的原版方图/近方图；如为其他地区版本，以此处方形来源为准。"
        else:
            square_source_name = source_name or path.name
            square_source_url = original_source_url
            note += " 方形版从仓库中的原比例封面裁切。"

        if (DEST_ORIGINAL / (path.stem + ".png")).exists():
            classification = "Original（原图未裁切）"
            square_path = f"GBA_Square/Original/{path.stem}.png"
        else:
            classification = "Cropped（裁切）"
            square_path = f"GBA_Square/Cropped/{path.stem}.png"

        rows.append([
            "GBA", path.name, f"GBA/{path.name}", square_path, classification,
            source_name or "当前仓库原图；上游条目需复核", original_source_url,
            square_source_name, square_source_url, note,
        ])

    # NDS cover sources; one DSiWare item uses a clearly identified community substitute.
    for path in sorted(p for p in NDS_SOURCE.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}):
        source_name, note = NDS_SOURCE_MAP.get(path.stem, ("", ""))
        source_url = nds_source_url(source_name) if source_name else "https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts"
        if (NDS_DEST_ORIGINAL / (path.stem + ".png")).exists():
            classification = "Original（未裁切画面）"
            square_path = f"NDS_Square/Original/{path.stem}.png"
        else:
            classification = "Cropped（裁切）"
            square_path = f"NDS_Square/Cropped/{path.stem}.png"
        if not note:
            note = "Libretro Named Boxarts 对应游戏封面；部分为其他地区发行版本。" if not source_name.startswith(("http://", "https://")) else "使用独立替代封面；请查看说明。"
        rows.append([
            "NDS", path.name, f"NDS/{path.name}", square_path, classification,
            source_name or "来源需核实", source_url,
            source_name or "来源需核实", source_url, note,
        ])

    csv_files = [
        ("cover_sources.csv", rows),
        ("gba_sources.csv", [row for row in rows if row[0] == "GBA"]),
        ("nds_sources.csv", [row for row in rows if row[0] == "NDS"]),
    ]
    for filename, selected_rows in csv_files:
        with (SOURCES_DIR / filename).open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(selected_rows)

    source_readme = [
        "# 封面来源网址索引",
        "",
        "本目录集中保存每张封面的来源网址、仓库内原图路径、方形版本路径和处理类型。",
        "",
        "## 文件说明",
        "",
        "- [cover_sources.csv](cover_sources.csv)：GBA 与 NDS 全部封面合并清单。",
        "- [gba_sources.csv](gba_sources.csv)：25 款 GBA 封面逐张来源。",
        "- [nds_sources.csv](nds_sources.csv)：18 款 NDS 封面逐张来源。",
        "",
        "CSV 内的「原比例封面来源网址」与「方形封面来源网址」均可直接打开。若来源文件名为 Libretro 的英文标题，表示采用同一游戏的对应地区盒绘；地区版本可能与本地 ROM 不同。",
        "",
        "GBA 原图在仓库的 [GBA/](../GBA/) 中。方形版若有合适的原版方图，则优先使用该原版图；否则从仓库中的原比例封面裁切。NDS 原版盒绘主要来自 Libretro Named Boxarts；《塞尔达传说四支剑 25 周年纪念版》没有零售实体 DS 盒绘，使用社区制作的替代封面，来源及说明已在表格中标注。",
        "",
        "## 上游来源库",
        "",
        "- [Libretro Nintendo - Game Boy Advance Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)",
        "- [Libretro Nintendo DS Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts)",
        "- [SmartCrop.py 内容感知裁切算法](https://github.com/smartcrop/smartcrop.py)",
        "",
        "封面美术版权属于各自权利人。仓库只整理封面，不包含任何 ROM 或汉化补丁。",
        "",
    ]
    (SOURCES_DIR / "README.md").write_text("\n".join(source_readme), encoding="utf-8")

def main():
    if not SOURCE.is_dir():
        print(f"Missing source folder: {SOURCE}", file=sys.stderr)
        return 2
    files = sorted(p for p in SOURCE.iterdir()
                   if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
    if not files:
        print(f"No cover images found in {SOURCE}", file=sys.stderr)
        return 2

    DEST.mkdir(parents=True, exist_ok=True)
    DEST_ORIGINAL.mkdir(parents=True, exist_ok=True)
    DEST_CROPPED.mkdir(parents=True, exist_ok=True)
    # Clean the former flat layout and stale categorized outputs before rebuilding.
    for stale in DEST.glob("*.png"):
        stale.unlink()
    for folder in (DEST_ORIGINAL, DEST_CROPPED):
        for stale in folder.glob("*.png"):
            stale.unlink()
    no_crop_entries = []
    cropped_entries = []
    made = 0

    for path in files:
        try:
            override = load_square_original(path)
            if override:
                cover, source_name, near_square = override
                output = cover.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
                destination_folder = DEST_ORIGINAL
                if near_square:
                    label = "原版近方图，未裁切（原图 256×257，仅轻微统一比例）"
                else:
                    label = "原版方图，未裁切（只统一输出尺寸）"
                no_crop_entries.append((path.name, source_name, label, near_square))
            else:
                with Image.open(path) as original:
                    output = crop_square(original.copy())
                destination_folder = DEST_CROPPED
                cropped_entries.append((path.name, f"GBA/{path.name}"))
            output.save(destination_folder / (path.stem + ".png"), format="PNG", optimize=True)
            made += 1
            print(f"Created {destination_folder.relative_to(ROOT)}/{path.stem}.png")
        except Exception as exc:
            print(f"ERROR: {path.name}: {exc}", file=sys.stderr)

    note = [
        "# GBA 方形封面目录说明",
        "",
        "本目录分为 Original/ 和 Cropped/ 两类。Original/ 优先保存已找到的同一游戏原版正方形盒绘，未裁切画面；Cropped/ 则在找不到合适原版方图时，从 GBA/ 原图选择主体区域裁切。",
        "",
        f"**统计：{len(no_crop_entries)} 张原版方图/近方图未裁切；{len(cropped_entries)} 张从原图裁切。**",
        "",
        "## Original/：原图未裁切",
        "",
    ]
    for rom_name, source_name, label, near_square in no_crop_entries:
        note.append(f"- `Original/{rom_name}` — {label}。方形来源：{source_name}")
    note.extend(["", "## Cropped/：内容感知裁切", ""])
    for rom_name, source_name in cropped_entries:
        note.append(f"- `Cropped/{rom_name}` — 从原比例封面 `{source_name}` 裁切为 512 × 512。")
    note.extend([
        "",
        "所有来源网址统一见 [Sources/cover_sources.csv](../Sources/cover_sources.csv)；来源说明见 [Sources/README.md](../Sources/README.md)。裁切算法：[SmartCrop.py](https://github.com/smartcrop/smartcrop.py)。",
        "",
    ])
    (DEST / "README.md").write_text("\n".join(note), encoding="utf-8")

    manifest = [
        "# 原版方图未裁切名单",
        "",
        "本名单对应 GBA_Square/Original/ 下的封面。它们使用同一游戏的原版方形盒绘，只统一输出到 512 × 512；地区版本可能和本地 ROM 不一致。",
        "",
    ]
    for rom_name, source_name, label, near_square in no_crop_entries:
        manifest.append(f"- `Original/{rom_name}` — {label}。源图：{source_name}")
    manifest.extend([
        "",
        f"**合计：{len(no_crop_entries)} 张。** 其余 {len(cropped_entries)} 张位于 `GBA_Square/Cropped/`。",
        "",
    ])
    (DEST / "原版方图未裁切名单.md").write_text("\n".join(manifest), encoding="utf-8")

    print(f"Done: {made}/{len(files)} GBA square covers; {len(no_crop_entries)} original square/near-square, {len(cropped_entries)} cropped.")
    print("Downloading original-proportion NDS cover art...")
    nds_sources_ok = sync_nds_originals()
    nds_made, nds_total = generate_nds_square_covers()
    print(f"Done: {nds_made}/{nds_total} NDS square covers.")
    write_source_catalogs()

    return 0 if made == len(files) and nds_sources_ok and nds_made == nds_total and nds_total == len(NDS_SOURCE_MAP) else 1

if __name__ == "__main__":
    raise SystemExit(main())
