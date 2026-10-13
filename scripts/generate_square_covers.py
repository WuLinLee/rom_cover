#!/usr/bin/env python3
"""Build separate square covers from GBA/ without altering the originals.

Known square original artwork is preferred. Remaining covers use SmartCrop.py,
an open-source content-aware crop scorer. Every output is a 512x512 PNG.
"""
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import sys

import smartcrop
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "GBA"
DEST = ROOT / "GBA_Square"
SIZE = 512

NDS_SOURCE = ROOT / "NDS"
NDS_DEST = ROOT / "NDS_Square"
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
    uncropped = []
    cropped = []
    made = 0

    for path in image_files:
        try:
            with Image.open(path) as original:
                was_square = original.width == original.height
                original_size = f"{original.width}×{original.height}"
                output = crop_square(original.copy())
            output.save(NDS_DEST / (path.stem + ".png"), format="PNG", optimize=True)
            source_name, note = NDS_SOURCE_MAP.get(path.stem, ("", ""))
            if was_square and note:
                uncropped.append((path.name, original_size, source_name, note, "community"))
            elif was_square:
                uncropped.append((path.name, original_size, source_name, note, "original"))
            else:
                cropped.append((path.name, original_size, source_name, note))
            made += 1
            print(f"Created NDS_Square/{path.stem}.png")
        except Exception as exc:
            print(f"ERROR: NDS cover {path.name}: {exc}", file=sys.stderr)

    lines = [
        "# NDS 方形封面来源说明",
        "",
        "所有方形封面统一输出为 512 × 512 PNG，文件名与 ROM 对应。NDS/ 内的原始比例封面不会被覆盖。",
        "",
        "规则：优先保留原图本身就是正方形的封面；其他图片使用开源 SmartCrop.py 选择内容较重要的方形区域。自动裁切不是完美的人物识别，仍可能需要人工检查。",
        "",
        f"**统计：{len(uncropped)} 张原图本身为正方形（未裁切画面）；{len(cropped)} 张从原版比例封面裁切。**",
        "",
        "## 原图本身为正方形：未裁切画面",
        "",
    ]
    for filename, original_size, source_name, note, kind in uncropped:
        if kind == "community":
            lines.append(f"- **{filename}** — {original_size}；保留方形社区替代封面。{note}")
        else:
            lines.append(f"- **{filename}** — {original_size}；原图为方形，仅统一输出到 512 × 512。来源：{source_name}")
    lines.extend(["", "## 从原版比例封面裁切", ""])
    for filename, original_size, source_name, note in cropped:
        lines.append(f"- **{filename}** — 原图 {original_size}；从对应原版比例封面裁切。来源：{source_name}")
    lines.extend([
        "",
        "算法来源：[SmartCrop.py](https://github.com/smartcrop/smartcrop.py)。画面自动裁切可能舍弃边缘文字、标志或人物的一部分；如有单张构图不理想，建议针对该图手动调整。",
        "",
    ])
    (NDS_DEST / "README.md").write_text("\n".join(lines), encoding="utf-8")

    return made, len(image_files)


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
    no_crop_entries = []
    cropped_entries = []
    made = 0

    for path in files:
        try:
            override = load_square_original(path)
            if override:
                cover, source_name, near_square = override
                output = cover.resize((SIZE, SIZE), Image.Resampling.LANCZOS)
                if near_square:
                    label = "✅ 原版近方图，未裁切（原图 256×257，仅轻微统一比例）"
                else:
                    label = "✅ 原版方图，未裁切（只统一输出尺寸）"
                no_crop_entries.append((path.name, source_name, label, near_square))
            else:
                with Image.open(path) as original:
                    output = crop_square(original.copy())
                cropped_entries.append((path.name, f"GBA/{path.name}"))
            output.save(DEST / (path.stem + ".png"), format="PNG", optimize=True)
            made += 1
            print(f"Created {path.stem}.png")
        except Exception as exc:
            print(f"ERROR: {path.name}: {exc}", file=sys.stderr)

    note = [
        "# 方形封面来源说明",
        "",
        "本目录图片均为 512 × 512 PNG，文件名与 ROM 对应。",
        "",
        "## 标记说明",
        "",
        "- ✅ 原版方图，未裁切：使用对应游戏的原版 1:1 封面，仅统一输出尺寸。",
        "- ✅ 原版近方图，未裁切：原图近似 1:1，只轻微统一比例，没有裁切画面。",
        "- ✂️ 从原图裁切：没有找到合适的方形原版封面，使用 SmartCrop.py 从 GBA/ 原图中选择方形区域。",
        "",
        f"**统计：{len(no_crop_entries)} 张使用原版方图/近方图（未裁切）；{len(cropped_entries)} 张由原图裁切。**",
        "",
        "## ✅ 原版方图 / 近方图：未裁切",
        "",
    ]
    for rom_name, source_name, label, near_square in no_crop_entries:
        note.append(f"- **{rom_name}** — {label}。源图：{source_name}")
    note.extend(["", "## ✂️ 从原始封面裁切", ""])
    for rom_name, source_name in cropped_entries:
        note.append(f"- **{rom_name}** — 从 {source_name} 裁切成正方形")
    note.extend([
        "",
        "原版封面来源库：[Libretro Nintendo - Game Boy Advance Named Boxarts](https://github.com/libretro-thumbnails/Nintendo_-_Game_Boy_Advance/tree/master/Named_Boxarts)。需要裁切的封面使用开源 [SmartCrop.py](https://github.com/smartcrop/smartcrop.py) 算法选择画面区域；该算法使用细节、边缘、颜色饱和度、肤色线索和构图启发式，不是完美的人物识别，结果仍可能需要人工检查。少数未裁切方图使用同一游戏的其他地区原版封面；原始比例图片始终保留在 GBA/。",
        "",
    ])
    (DEST / "README.md").write_text("\n".join(note), encoding="utf-8")

    manifest = [
        "# ✅ 原版方图未裁切名单",
        "",
        "下列方形封面直接使用对应游戏的原版方形封面，没有裁切画面。输出统一调整到 512 × 512，仅作尺寸归一化。",
        "",
    ]
    for rom_name, source_name, label, near_square in no_crop_entries:
        if near_square:
            manifest.append(f"- ✅ **{rom_name}** — 原版近方图，未裁切，仅轻微统一比例。源图：{source_name}")
        else:
            manifest.append(f"- ✅ **{rom_name}** — 原版方图，未裁切。源图：{source_name}")
    manifest.extend([
        "",
        f"**合计：{len(no_crop_entries)} 张。** 其他 {len(cropped_entries)} 张来自原始比例封面的方形裁切，完整分类请查看 [README.md](README.md)。",
        "",
    ])
    (DEST / "原版方图未裁切名单.md").write_text("\n".join(manifest), encoding="utf-8")

    print(f"Done: {made}/{len(files)} GBA square covers; {len(no_crop_entries)} original square/near-square, {len(cropped_entries)} cropped.")

    print("Downloading original-proportion NDS cover art...")
    nds_sources_ok = sync_nds_originals()
    nds_made, nds_total = generate_nds_square_covers()
    print(f"Done: {nds_made}/{nds_total} NDS square covers.")

    return 0 if made == len(files) and nds_sources_ok and nds_made == nds_total and nds_total == len(NDS_SOURCE_MAP) else 1

if __name__ == "__main__":
    raise SystemExit(main())
