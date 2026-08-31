from __future__ import annotations

import re
import sqlite3
import textwrap
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(r"C:\Users\Administrator\Desktop\codex项目汇总")
DB = Path(r"C:\Users\Administrator\AppData\Roaming\CNotes\notes.db")
OUT = ROOT / "CNotes视频快剪"
FRAMES = OUT / "frames"
VIDEO = OUT / "c_notes_code_and_notes.mp4"

CANVAS = (1080, 1920)
BG = (245, 247, 250)
INK = (28, 34, 44)
MUTED = (103, 113, 128)
BLUE = (39, 93, 173)
GREEN = (30, 132, 73)
DARK = (24, 28, 36)
PANEL = (255, 255, 255)

FONT_CN = r"C:\Windows\Fonts\msyh.ttc"
FONT_CN_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


F_TITLE = font(FONT_CN_BOLD, 42)
F_H1 = font(FONT_CN_BOLD, 34)
F_H2 = font(FONT_CN_BOLD, 27)
F_BODY = font(FONT_CN, 25)
F_SMALL = font(FONT_CN, 21)
F_MONO = font(FONT_MONO, 22)
F_MONO_SMALL = font(FONT_MONO, 20)


def clean(s: str | None) -> str:
    return (s or "").replace("\r\n", "\n").replace("\r", "\n").strip()


def day_key(text: str, fallback: int = 9999) -> tuple[int, int, str]:
    m = re.search(r"day\s*(\d+)(?:\D+(\d+))?", text, re.I)
    if not m:
        return (fallback, fallback, text)
    return (int(m.group(1)), int(m.group(2) or 0), text)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, width: int) -> list[str]:
    lines: list[str] = []
    for para in clean(text).split("\n"):
        para = para.strip()
        if not para:
            lines.append("")
            continue
        current = ""
        for ch in para:
            candidate = current + ch
            if draw.textlength(candidate, font=fnt) <= width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = ch
        if current:
            lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    width: int,
    max_lines: int,
    line_gap: int = 8,
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, width)
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + ["..."]
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + line_gap
    return y


def rounded(draw: ImageDraw.ImageDraw, box, fill, outline=None, radius=22, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def code_files() -> list[Path]:
    candidates = [
        Path(r"C:\Users\Administrator\Desktop\作业3（只用到第二周的知识做的）.c"),
        ROOT / "homework3.c",
        ROOT / "C-Learning" / "main.c",
    ]
    found = [p for p in candidates if p.exists()]
    day_prefixed = [p for p in found if re.match(r"day\d+", p.stem, re.I)]
    if day_prefixed:
        return sorted(day_prefixed, key=lambda p: day_key(p.stem))
    return sorted(found, key=lambda p: (len(p.read_text(encoding="utf-8", errors="replace")), str(p)))


def draw_code_frame(path: Path, index: int, total: int, no_day_prefix: bool) -> Path:
    img = Image.new("RGB", CANVAS, BG)
    draw = ImageDraw.Draw(img)
    draw.text((56, 46), "VS Code / C 代码", font=F_TITLE, fill=INK)
    subtitle = f"{index}/{total}  {path.name}"
    draw.text((58, 104), subtitle, font=F_SMALL, fill=MUTED)
    if no_day_prefix:
        draw.text((58, 134), "未找到 day*.c，按当前找到的 C 文件由简到繁展示", font=F_SMALL, fill=(170, 86, 40))

    editor = (42, 184, 1038, 1760)
    rounded(draw, editor, DARK, outline=(40, 48, 62), radius=18)
    draw.rectangle((42, 184, 1038, 238), fill=(31, 36, 47))
    draw.text((72, 201), path.name, font=F_SMALL, fill=(220, 226, 235))

    code = path.read_text(encoding="utf-8", errors="replace")
    code = code.replace("\t", "    ")
    y = 270
    x_line = 74
    x_code = 140
    max_chars = 58
    line_no = 1
    for raw in code.splitlines()[:58]:
        chunks = textwrap.wrap(raw, max_chars, replace_whitespace=False, drop_whitespace=False) or [""]
        for j, chunk in enumerate(chunks):
            if y > 1700:
                break
            if j == 0:
                draw.text((x_line, y), f"{line_no:>3}", font=F_MONO_SMALL, fill=(100, 110, 128))
            color = (229, 232, 239)
            stripped = chunk.strip()
            if stripped.startswith("#"):
                color = (138, 203, 255)
            elif any(k in stripped for k in ("int ", "double", "return", "scanf", "printf", "for", "while", "if")):
                color = (244, 213, 137)
            draw.text((x_code, y), chunk, font=F_MONO, fill=color)
            y += 30
        line_no += 1
    out = FRAMES / f"code_{index:02d}_{path.stem}.jpg"
    img.save(out, quality=94)
    return out


def load_notes() -> list[sqlite3.Row]:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT id, note_date, title, topics, summary, codex_summary, code, reflection
        FROM notes
        ORDER BY CAST(note_date AS INTEGER), id
        """
    ).fetchall()
    con.close()
    return rows


def draw_note_frame(row: sqlite3.Row, index: int, total: int) -> Path:
    img = Image.new("RGB", CANVAS, BG)
    draw = ImageDraw.Draw(img)

    title = clean(row["title"]) or f"note {row['id']}"
    topics = clean(row["topics"])
    draw.text((56, 46), "C 语言笔记", font=F_TITLE, fill=INK)
    draw.text((58, 104), f"{index}/{total}  第 {row['note_date']} 天 / {title}", font=F_SMALL, fill=MUTED)

    y = 160
    rounded(draw, (42, y, 1038, y + 150), PANEL, outline=(228, 232, 238), radius=20)
    draw.text((72, y + 24), title, font=F_H1, fill=BLUE)
    draw.text((72, y + 78), f"知识点：{topics or '未填写'}", font=F_BODY, fill=INK)
    y += 176

    summary = clean(row["codex_summary"]) or clean(row["summary"])
    if summary:
        rounded(draw, (42, y, 1038, y + 610), PANEL, outline=(228, 232, 238), radius=20)
        draw.text((72, y + 26), "总结", font=F_H2, fill=GREEN)
        draw_wrapped(draw, (72, y + 72), summary, F_BODY, INK, 930, 16)
        y += 638

    code = clean(row["code"])
    if code:
        box_h = 520 if y < 1180 else 430
        rounded(draw, (42, y, 1038, min(y + box_h, 1760)), DARK, outline=(40, 48, 62), radius=20)
        draw.text((72, y + 24), "C 代码", font=F_H2, fill=(185, 222, 255))
        cy = y + 72
        for line_no, raw in enumerate(code.replace("\t", "    ").splitlines()[:13], 1):
            line = raw[:72]
            draw.text((72, cy), f"{line_no:>2}", font=F_MONO_SMALL, fill=(100, 110, 128))
            draw.text((120, cy), line, font=F_MONO_SMALL, fill=(232, 236, 244))
            cy += 28
        y += box_h + 22

    reflection = clean(row["reflection"])
    if reflection and y < 1700:
        rounded(draw, (42, y, 1038, 1760), PANEL, outline=(228, 232, 238), radius=20)
        draw.text((72, y + 24), "复盘", font=F_H2, fill=(150, 90, 30))
        draw_wrapped(draw, (72, y + 70), reflection, F_BODY, INK, 930, 7)

    out = FRAMES / f"note_{index:03d}_day{row['note_date']}_{row['id']}.jpg"
    img.save(out, quality=94)
    return out


def make_contact_sheet(frames: list[Path]) -> None:
    thumbs = []
    for p in frames:
        im = Image.open(p).convert("RGB")
        im.thumbnail((162, 288), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (162, 288), (250, 250, 250))
        tile.paste(im, ((162 - im.width) // 2, (288 - im.height) // 2))
        thumbs.append(tile)
    cols = 6
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 162, rows * 288), (255, 255, 255))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % cols) * 162, (i // cols) * 288))
    sheet.save(OUT / "contact_sheet.jpg", quality=90)


def fit_frame(path: Path) -> Image.Image:
    return Image.open(path).convert("RGB").resize(CANVAS, Image.Resampling.LANCZOS)


def make_video(frames: list[Path]) -> None:
    fps = 30
    hold = 1.15
    n = round(hold * fps)
    fade = 5
    white = Image.new("RGB", CANVAS, BG)
    with imageio.get_writer(
        VIDEO,
        fps=fps,
        codec="libx264",
        quality=7,
        macro_block_size=1,
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    ) as writer:
        for p in frames:
            frame = fit_frame(p)
            for i in range(n):
                img = frame
                if i < fade:
                    img = Image.blend(white, frame, i / fade)
                elif i >= n - fade:
                    img = Image.blend(white, frame, (n - i - 1) / fade)
                writer.append_data(np.asarray(img))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    for old in FRAMES.glob("*.jpg"):
        old.unlink()

    frames: list[Path] = []
    c_files = code_files()
    no_day = not any(re.match(r"day\d+", p.stem, re.I) for p in c_files)
    for i, p in enumerate(c_files, 1):
        frames.append(draw_code_frame(p, i, len(c_files), no_day))

    notes = load_notes()
    for i, row in enumerate(notes, 1):
        frames.append(draw_note_frame(row, i, len(notes)))

    make_contact_sheet(frames)
    make_video(frames)
    print(f"frames={len(frames)}")
    print(VIDEO)


if __name__ == "__main__":
    main()
