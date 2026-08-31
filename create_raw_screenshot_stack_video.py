from __future__ import annotations

import ctypes
import re
import sqlite3
import subprocess
import time
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageGrab


ROOT = Path(r"C:\Users\Administrator\Desktop\codex项目汇总")
OUT = ROOT / "原样截图视频"
RAW = OUT / "raw_screenshots"
VIDEO = OUT / "raw_vscode_cnotes_stack.mp4"
C_DAY = Path(r"F:\DevTools\C-Learning\day")
CODE_CMD = Path(r"F:\DevTools\VSCode\bin\code.cmd")
DB = Path(r"C:\Users\Administrator\AppData\Roaming\CNotes\notes.db")
CNOTES_EXE = ROOT / "CNotes" / "dist" / "CNotes.exe"
SHOT_HELPER = Path(r"C:\Users\Administrator\.codex\skills\screenshot\scripts\take_screenshot.ps1")


user32 = ctypes.windll.user32


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


def list_windows() -> list[tuple[int, str]]:
    windows: list[tuple[int, str]] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def enum_proc(hwnd, _):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                windows.append((int(hwnd), buf.value))
        return True

    user32.EnumWindows(enum_proc, 0)
    return windows


def find_window(title_contains: str) -> int:
    title_contains = title_contains.lower()
    for hwnd, title in list_windows():
        if title_contains in title.lower():
            return hwnd
    raise RuntimeError(f"window not found: {title_contains}")


def foreground(hwnd: int) -> None:
    user32.ShowWindow(hwnd, 3)
    time.sleep(0.15)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.45)


def window_rect(hwnd: int) -> tuple[int, int, int, int]:
    rect = RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        raise RuntimeError("GetWindowRect failed")
    return rect.left, rect.top, rect.right, rect.bottom


def click(x: int, y: int) -> None:
    user32.SetCursorPos(x, y)
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.03)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.15)


def send_keys(keys: str) -> None:
    ps = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        f"[System.Windows.Forms.SendKeys]::SendWait('{keys}')"
    )
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)
    time.sleep(0.22)


def capture(hwnd: int, path: Path) -> Path:
    foreground(hwnd)
    bbox = window_rect(hwnd)
    img = ImageGrab.grab(bbox=bbox)
    img.save(path)
    return path


def day_key(path: Path) -> tuple[int, int, int, str]:
    stem = path.stem
    m = re.search(r"day_?(\d+)(?:[_-](\d+))?(?:[_-](\d+))?", stem, re.I)
    if not m:
        m = re.search(r"day(\d+)(?:[_-](\d+))?", stem, re.I)
    if not m:
        return (999, 999, 999, stem)
    return (int(m.group(1)), int(m.group(2) or 0), int(m.group(3) or 0), stem)


def c_files() -> list[Path]:
    files = []
    for path in C_DAY.glob("*.c"):
        if path.name == "tempCodeRunnerFile.c":
            continue
        if path.stat().st_size <= 40:
            continue
        files.append(path)
    return sorted(files, key=day_key)


def capture_vscode() -> list[Path]:
    shots: list[Path] = []
    files = c_files()
    for i, path in enumerate(files, 1):
        subprocess.run([str(CODE_CMD), "-r", str(path)], check=False)
        time.sleep(0.8)
        hwnd = find_window("visual studio code")
        out = RAW / f"vscode_{i:03d}_{path.stem}.png"
        capture(hwnd, out)
        shots.append(out)
    return shots


def note_count() -> int:
    con = sqlite3.connect(DB)
    try:
        return con.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    finally:
        con.close()


def ensure_cnotes() -> int:
    try:
        return find_window("cnotes - c")
    except RuntimeError:
        subprocess.Popen([str(CNOTES_EXE)])
        time.sleep(2.0)
        return find_window("cnotes - c")


def capture_cnotes() -> list[Path]:
    shots: list[Path] = []
    hwnd = ensure_cnotes()
    foreground(hwnd)
    left, top, right, bottom = window_rect(hwnd)

    # Focus the listbox, jump to the oldest item, then move upward through the
    # descending list so the exported screenshots read day1 -> latest day.
    click(left + 120, top + 190)
    send_keys("{END}")
    total = note_count()
    for i in range(total):
        out = RAW / f"cnotes_{i + 1:03d}.png"
        capture(hwnd, out)
        shots.append(out)
        send_keys("{UP}")
    return shots


def fit_to_canvas(path: Path, size=(1080, 1920)) -> Image.Image:
    img = Image.open(path).convert("RGB")
    cw, ch = size
    scale = min(cw / img.width, ch / img.height)
    nw, nh = round(img.width * scale), round(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (12, 14, 18))
    canvas.paste(resized, ((cw - nw) // 2, (ch - nh) // 2))
    return canvas


def make_video(paths: list[Path]) -> None:
    fps = 30
    hold = 0.85
    frames_per = round(fps * hold)
    with imageio.get_writer(
        VIDEO,
        fps=fps,
        codec="libx264",
        quality=7,
        macro_block_size=1,
        ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
    ) as writer:
        for path in paths:
            frame = np.asarray(fit_to_canvas(path))
            for _ in range(frames_per):
                writer.append_data(frame)


def make_contact_sheet(paths: list[Path]) -> None:
    thumbs = []
    for path in paths:
        img = Image.open(path).convert("RGB")
        img.thumbnail((240, 135), Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (240, 135), (20, 22, 28))
        tile.paste(img, ((240 - img.width) // 2, (135 - img.height) // 2))
        thumbs.append(tile)
    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 240, rows * 135), (8, 10, 14))
    for i, tile in enumerate(thumbs):
        sheet.paste(tile, ((i % cols) * 240, (i // cols) * 135))
    sheet.save(OUT / "raw_contact_sheet.jpg", quality=90)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    for old in RAW.glob("*.png"):
        old.unlink()

    shots = []
    shots.extend(capture_vscode())
    shots.extend(capture_cnotes())
    make_contact_sheet(shots)
    make_video(shots)
    print(f"screenshots={len(shots)}")
    print(VIDEO)


if __name__ == "__main__":
    main()
