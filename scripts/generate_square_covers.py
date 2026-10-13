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
DEST_COMMUNITY = DEST / "Community"
SIZE = 512
SOURCES_DIR = ROOT / "Sources"

NDS_SOURCE = ROOT / "NDS"
NDS_DEST = ROOT / "NDS_Square"
NDS_DEST_ORIGINAL = NDS_DEST / "Original"
NDS_DEST_CROPPED = NDS_DEST / "Cropped"
NDS_DEST_COMMUNITY = NDS_DEST / "Community"
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
    "侠盗猎车手 - 前进[Beq & LCPD](Beta) (v20160720)[简](JP)(256Mb).png":
        ("https://images.launchbox-app.com/52218a81-8b54-47d7-8702-3c36c52db179.jpg", False),
    "拿破仑(12.24最终版)[Advance-002](简)(JP)(72Mb).png":
        ("https://images.launchbox-app.com/d1b3c796-9232-43fb-af81-60197d69efb8.jpg", True),
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

# Square community-made/fanart covers, verified in LaunchBox's "Fanart - Box - Front" listing.
# These are intentionally separate from genuine original box art.
GBA_COMMUNITY_MAP = {
    "侠盗猎车手 - 前进[Beq & LCPD](Beta) (v20160720)[简](JP)(256Mb)": (
        "https://images.launchbox-app.com/2f341c36-3480-4354-b275-bf085f97e3bd.png",
        "https://gamesdb.launchbox-app.com/games/details/3580-grand-theft-auto",
        "LaunchBox Games Database — Fanart - Box - Front (North America), 450 × 450",
    ),
    "节奏天国[漫游](简)(JP)(128Mb)": (
        "https://images.launchbox-app.com/529e3151-5c57-4f6b-9c37-01d52b8e2828.jpg",
        "https://gamesdb.launchbox-app.com/games/images/20455-rhythm-tengoku",
        "LaunchBox Games Database — Fanart - Box - Front (North America), 1375 × 1375",
    ),
    "逆转裁判3[逆转Ace](简)(JP)(69.64Mb)": (
        "https://gamesdb-images.launchbox.gg/r2_55b71046-88b4-4102-9ec4-e17346b55833.png",
        "https://gamesdb.launchbox-app.com/games/images/85224-gyakuten-saiban-3",
        "LaunchBox Games Database — Fanart - Box - Front (World), 1080 × 1080",
    ),
}

NDS_COMMUNITY_STEMS = {
    "塞尔达传说四支剑 25周年纪念版(简)(Monado汉化组)(108Mb)"
}
NDS_COMMUNITY_PAGES = {
    "塞尔达传说四支剑 25周年纪念版(简)(Monado汉化组)(108Mb)":
        "https://gamesdb.launchbox-app.com/games/images/56342-the-legend-of-zelda-four-swords-anniversary-edition"
}

# Some original-looking square box fronts are hosted by LaunchBox rather than Libretro.
SQUARE_ORIGINAL_PAGES = {
    "侠盗猎车手 - 前进[Beq & LCPD](Beta) (v20160720)[简](JP)(256Mb).png":
        "https://gamesdb.launchbox-app.com/games/details/3580-grand-theft-auto",
    "拿破仑(12.24最终版)[Advance-002](简)(JP)(72Mb).png":
        "https://gamesdb.launchbox-app.com/games/images/30528-napoleon-laigle-de-guerre",
}


def load_community_square(platform, stem):
    """Download and normalize a known square community-made cover to 512x512."""
    entry = GBA_COMMUNITY_MAP.get(stem) if platform == "GBA" else None
    if not entry:
        return None
    url, page_url, label = entry
    try:
        request = Request(url, headers={"User-Agent": "rom-cover-square-generator"})
        with urlopen(request, timeout=45) as response:
            data = response.read()
        with Image.open(BytesIO(data)) as source:
            image = ImageOps.exif_transpose(source).convert("RGBA" if "A" in source.getbands() else "RGB")
            ratio_difference = abs(image.width / image.height - 1.0)
            # This directory is for purpose-built square/near-square art, not portrait posters.
            if ratio_difference > 0.035:
                print(f"WARNING: community artwork is not square enough, skipping: {url}", file=sys.stderr)
                return None
            return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS), url, page_url, label
    except Exception as exc:
        print(f"WARNING: could not fetch community artwork for {stem}: {exc}", file=sys.stderr)
        return None


def load_square_original(filename):
    entry = SQUARE_ORIGINALS.get(filename.name)
    if not entry:
        return None
    source_name, near_square = entry
    url = source_name if source_name.startswith(("https://", "http://")) else LIBRETRO_BASE + quote(source_name, safe="")
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
    """Generate separate NDS square sets by source type, without altering NDS/."""
    image_files = sorted(
        p for p in NDS_SOURCE.iterdir()
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    if not image_files:
        print(f"No NDS cover images found in {NDS_SOURCE}", file=sys.stderr)
        return 0, 0

    folders = (NDS_DEST_ORIGINAL, NDS_DEST_COMMUNITY, NDS_DEST_CROPPED)
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)
        for stale in folder.glob("*.png"):
            stale.unlink()
    for stale in NDS_DEST.glob("*.png"):
        stale.unlink()

    original_entries = []
    community_entries = []
    cropped_entries = []
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
            if path.stem in NDS_COMMUNITY_STEMS:
                destination_folder = NDS_DEST_COMMUNITY
                community_entries.append((path.name, original_size, source_name, note, was_exact_square))
            elif keep_full_image:
                destination_folder = NDS_DEST_ORIGINAL
                original_entries.append((path.name, original_size, source_name, note, was_exact_square))
            else:
                destination_folder = NDS_DEST_CROPPED
                cropped_entries.append((path.name, original_size, source_name, note))
            output.save(destination_folder / (path.stem + ".png"), format="PNG", optimize=True)
            made += 1
            print(f"Created {destination_folder.relative_to(ROOT)}/{path.stem}.png")
        except Exception as exc:
            print(f"ERROR: NDS cover {path.name}: {exc}", file=sys.stderr)

    lines = [
        "# NDS 方形封面来源说明",
        "",
        "方形封面统一为 512 × 512 PNG。Original/、Community/、Cropped/ 按图片来源分类；NDS/ 中的原比例源图始终保留。",
        "",
        f"**统计：{len(original_entries)} 张 Original 原版方/近方图；{len(community_entries)} 张 Community 社区制作方图；{len(cropped_entries)} 张 Cropped 自动裁切图。**",
        "",
        "## Original/：原版方图或近方图",
        "",
    ]
    if original_entries:
        for filename, original_size, source_name, note, was_exact_square in original_entries:
            shape = "正方形" if was_exact_square else "近方形，完整画面轻微归一"
            lines.append(f"- `Original/{filename}` — {original_size}，{shape}。来源：{source_name}")
    else:
        lines.append("- 当前没有找到确切的原版正方形封面；以后找到时放在这里。")
    lines.extend(["", "## Community/：社区制作的方形封面", ""])
    if community_entries:
        for filename, original_size, source_name, note, was_exact_square in community_entries:
            page = NDS_COMMUNITY_PAGES.get(Path(filename).stem, "来源页见 Sources/cover_sources.csv")
            desc = note or "社区提交的方形封面"
            lines.append(f"- `Community/{filename}` — 源图 {original_size}；{desc} 来源页：{page}")
    else:
        lines.append("- 当前没有匹配到社区制作方图。")
    lines.extend(["", "## Cropped/：从原比例封面裁切", ""])
    for filename, original_size, source_name, note in cropped_entries:
        lines.append(f"- `Cropped/{filename}` — 原图 {original_size}；从对应封面裁切。来源：{source_name}")
    lines.extend([
        "",
        "所有逐张来源网址见 [Sources/cover_sources.csv](../Sources/cover_sources.csv)。自动裁切使用 [SmartCrop.py](https://github.com/smartcrop/smartcrop.py)，不能保证每张人物脸部和标题都恰好保留，仍建议抽查。",
        "",
    ])
    (NDS_DEST / "README.md").write_text("\n".join(lines), encoding="utf-8")
    (NDS_DEST_ORIGINAL / "README.md").write_text(
        "# NDS Original 方形封面\n\n" + (
            "\n".join(f"- {x[0]}" for x in original_entries)
            if original_entries else
            "目前尚未找到可确认的原版正方形盒绘。找到后放在此目录。"
        ) + "\n",
        encoding="utf-8",
    )
    (NDS_DEST_COMMUNITY / "README.md").write_text(
        "# NDS Community 社区制作方形封面\n\n" + (
            "\n".join(f"- {x[0]}" for x in community_entries)
            if community_entries else
            "目前尚未匹配到社区制作方图。"
        ) + "\n\n逐张来源网址见 [Sources/cover_sources.csv](../../Sources/cover_sources.csv)。\n",
        encoding="utf-8",
    )
    (NDS_DEST_CROPPED / "README.md").write_text(
        "# NDS Cropped 自动裁切封面\n\n" + "\n".join(f"- {x[0]}" for x in cropped_entries) + "\n",
        encoding="utf-8",
    )
    return made, len(image_files)


def local_cover_url(folder, filename):
    return "https://raw.githubusercontent.com/WuLinLee/rom_cover/main/" + folder + "/" + quote(filename, safe="")


def write_source_catalogs():
    """Write a per-ROM index with direct artwork URLs, page URLs, and category."""
    SOURCES_DIR.mkdir(parents=True, exist_ok=True)
    header = [
        "平台", "ROM对应封面文件", "仓库原比例封面路径", "方形封面路径", "方形分类",
        "原比例图来源文件名", "原比例图来源网址", "方形图来源文件名/类型",
        "方形图直接网址", "来源页面网址", "备注",
    ]
    rows = []

    for path in sorted(p for p in SOURCE.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}):
        source_name = GBA_SOURCE_MAP.get(path.stem, "")
        original_url = LIBRETRO_BASE + quote(source_name, safe="") if source_name else "https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts"
        note = "原比例源图与 ROM 名称对应；地区版可能与汉化 ROM 不同。"

        override = SQUARE_ORIGINALS.get(path.name)
        community = GBA_COMMUNITY_MAP.get(path.stem)
        if (DEST_ORIGINAL / (path.stem + ".png")).exists():
            classification = "Original"
            square_path = f"GBA_Square/Original/{path.stem}.png"
            square_name = override[0] if override else source_name
            square_url = (
                square_name if square_name and square_name.startswith(("https://", "http://"))
                else LIBRETRO_BASE + quote(square_name, safe="") if square_name
                else original_url
            )
            source_page = SQUARE_ORIGINAL_PAGES.get(
                path.name,
                "https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts",
            )
            if square_name and square_name.startswith(("https://", "http://")):
                source_label = "LaunchBox Box - Front 原版发行盒绘"
            else:
                source_label = "Libretro Named Boxarts 原版方/近方图"
            note += f" 方形版为对应游戏的原版方/近方图（{source_label}），未裁切画面。"
        elif (DEST_COMMUNITY / (path.stem + ".png")).exists() and community:
            classification = "Community"
            square_path = f"GBA_Square/Community/{path.stem}.png"
            square_url, source_page, square_name = community
            note += f" 方形版为社区提交/非官方方图（{square_name}）。"
        else:
            classification = "Cropped"
            square_path = f"GBA_Square/Cropped/{path.stem}.png"
            square_name = source_name or path.name
            square_url = original_url
            source_page = "https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts"
            note += " 未找到合适的原版方图或匹配的社区方图，因此从仓库内原比例封面裁切。"

        rows.append([
            "GBA", path.name, f"GBA/{path.name}", square_path, classification,
            source_name or "原图已收录；上游单张文件名未核实", original_url,
            square_name or "原比例封面裁切", square_url, source_page, note,
        ])

    for path in sorted(p for p in NDS_SOURCE.iterdir() if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}):
        source_name, note = NDS_SOURCE_MAP.get(path.stem, ("", ""))
        source_url = nds_source_url(source_name) if source_name else "https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts"
        if (NDS_DEST_COMMUNITY / (path.stem + ".png")).exists():
            classification = "Community"
            square_path = f"NDS_Square/Community/{path.stem}.png"
            square_name = "Community art / Fanart - Box - Front"
            square_url = source_url
            source_page = NDS_COMMUNITY_PAGES.get(path.stem, source_url)
            note = note or "社区提交的非官方方图；不是原版实体盒绘。"
        elif (NDS_DEST_ORIGINAL / (path.stem + ".png")).exists():
            classification = "Original"
            square_path = f"NDS_Square/Original/{path.stem}.png"
            square_name = source_name
            square_url = source_url
            source_page = "https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts"
            note = note or "对应游戏原版方/近方图；地区版本可能不同。"
        else:
            classification = "Cropped"
            square_path = f"NDS_Square/Cropped/{path.stem}.png"
            square_name = source_name or "当前仓库原图"
            square_url = source_url
            source_page = "https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts"
            note = note or "从 NDS/ 中保存的对应原比例封面裁切；地区版本可能不同。"

        rows.append([
            "NDS", path.name, f"NDS/{path.name}", square_path, classification,
            source_name or "社区替代图；详情见备注", source_url,
            square_name or "来源待核实", square_url, source_page, note,
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
        "此目录集中记录每款游戏原比例封面和方形版的来源网址、文件名、处理类别和仓库路径。CSV 可用 Excel、Numbers 或 LibreOffice Calc 打开。",
        "",
        "## 文件说明",
        "",
        "- [cover_sources.csv](cover_sources.csv)：GBA + NDS 全部 43 款 ROM 的封面来源清单。",
        "- [gba_sources.csv](gba_sources.csv)：25 款 GBA 封面逐张来源。",
        "- [nds_sources.csv](nds_sources.csv)：18 款 NDS 封面逐张来源。",
        "",
        "## 方形封面类别",
        "",
        "- **Original**：找到同一游戏的原版正方形/近方形盒绘，保留画面，只统一尺寸。",
        "- **Community**：找到社区/玩家提交的方形封面。LaunchBox 图库中的 Fanart - Box - Front 都明确按 fanart 归类，不冒充官方原版盒绘。",
        "- **Cropped**：没有找到合适的原版方图或匹配的社区方图，才从原比例封面裁切。",
        "",
        "已确认的社区方图来自 [LaunchBox Games Database](https://gamesdb.launchbox-app.com/)，逐张图片直链和对应游戏图集页都记录在 CSV。地区版可能和汉化 ROM 的地区标记不同。",
        "",
        "## 上游来源库",
        "",
        "- [Libretro GBA Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)",
        "- [Libretro Nintendo DS Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_DS/tree/master/Named_Boxarts)",
        "- [LaunchBox Games Database](https://gamesdb.launchbox-app.com/)，包含社区提交的 Fanart - Box - Front 图片。",
        "- [SmartCrop.py](https://github.com/smartcrop/smartcrop.py)，为剩余没有合适方形来源的封面挑选裁切区域。",
        "",
        "图片的版权归原作者和各游戏权利人。仓库保留来源链接用于注明出处；社区作品不代表官方美术，也不等于已获得再发布授权。",
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

    for folder in (DEST_ORIGINAL, DEST_COMMUNITY, DEST_CROPPED):
        folder.mkdir(parents=True, exist_ok=True)
        for stale in folder.glob("*.png"):
            stale.unlink()
    for stale in DEST.glob("*.png"):
        stale.unlink()

    no_crop_entries = []
    community_entries = []
    cropped_entries = []
    made = 0

    for path in files:
        try:
            override = load_square_original(path)
            if override:
                cover, source_name, near_square = override
                output = cover.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
                destination_folder = DEST_ORIGINAL
                label = "原版近方图，未裁切" if near_square else "原版方图，未裁切"
                no_crop_entries.append((path.name, source_name, label, near_square))
            else:
                community = load_community_square("GBA", path.stem)
                if community:
                    output, source_url, source_page, source_label = community
                    destination_folder = DEST_COMMUNITY
                    community_entries.append((path.name, source_url, source_page, source_label))
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
        "方形封面按来源分为 Original、Community、Cropped 三类。Original 是可确认的原版方/近方盒绘；Community 是网上找到的玩家/社区方形封面；Cropped 是没有合适方形来源时从原比例封面裁切的版本。",
        "",
        f"**统计：{len(no_crop_entries)} 张 Original；{len(community_entries)} 张 Community；{len(cropped_entries)} 张 Cropped。**",
        "",
        "## Original/：原版方图",
        "",
    ]
    for rom_name, source_name, label, near_square in no_crop_entries:
        note.append(f"- `Original/{rom_name}` — {label}（只统一尺寸）。源图：{source_name}")
    note.extend(["", "## Community/：玩家/社区制作方图", ""])
    for rom_name, source_url, source_page, source_label in community_entries:
        note.append(f"- `Community/{rom_name}` — {source_label}。图片：[直链]({source_url})；[来源页面]({source_page})")
    note.extend(["", "## Cropped/：从原比例封面裁切", ""])
    for rom_name, source_name in cropped_entries:
        note.append(f"- `Cropped/{rom_name}` — 从 `{source_name}` 裁切为 512 × 512。")
    note.extend([
        "",
        "全部来源网址与处理说明见 [Sources/cover_sources.csv](../Sources/cover_sources.csv)。裁切算法：[SmartCrop.py](https://github.com/smartcrop/smartcrop.py)。",
        "",
    ])
    (DEST / "README.md").write_text("\n".join(note), encoding="utf-8")
    (DEST_ORIGINAL / "README.md").write_text(
        "# GBA Original 方形封面\n\n" + "\n".join(f"- {x[0]}" for x in no_crop_entries) + "\n",
        encoding="utf-8",
    )
    (DEST_COMMUNITY / "README.md").write_text(
        "# GBA Community 社区制作方形封面\n\n" + (
            "\n".join(f"- {x[0]}（来源：{x[3]}）" for x in community_entries)
            if community_entries else "目前没有匹配到社区方图。"
        ) + "\n\n逐张来源网址见 [Sources/cover_sources.csv](../../Sources/cover_sources.csv)。\n",
        encoding="utf-8",
    )
    (DEST_CROPPED / "README.md").write_text(
        "# GBA Cropped 自动裁切封面\n\n" + "\n".join(f"- {x[0]}" for x in cropped_entries) + "\n",
        encoding="utf-8",
    )

    manifest = [
        "# 原版方图未裁切名单",
        "",
        "本名单对应 GBA_Square/Original/ 下的封面。它们使用同一游戏的原版方形盒绘，只统一输出尺寸；地区版本可能和本地 ROM 不一致。",
        "",
    ]
    for rom_name, source_name, label, near_square in no_crop_entries:
        manifest.append(f"- `Original/{rom_name}` — {label}。源图：{source_name}")
    manifest.extend([
        "",
        f"**合计：{len(no_crop_entries)} 张。** 社区制作方图位于 `GBA_Square/Community/`，其余裁切图位于 `GBA_Square/Cropped/`。",
        "",
    ])
    (DEST / "原版方图未裁切名单.md").write_text("\n".join(manifest), encoding="utf-8")

    print(f"Done: {made}/{len(files)} GBA square covers; {len(no_crop_entries)} Original, {len(community_entries)} Community, {len(cropped_entries)} Cropped.")
    print("Downloading original-proportion NDS cover art...")
    nds_sources_ok = sync_nds_originals()
    nds_made, nds_total = generate_nds_square_covers()
    print(f"Done: {nds_made}/{nds_total} NDS square covers.")
    write_source_catalogs()

    return 0 if made == len(files) and nds_sources_ok and nds_made == nds_total and nds_total == len(NDS_SOURCE_MAP) else 1

if __name__ == "__main__":
    raise SystemExit(main())
