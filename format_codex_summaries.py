import os
import shutil
import sqlite3
from datetime import datetime

db_path = os.path.expandvars(r"%APPDATA%\CNotes\notes.db")
backup = db_path + ".bak-format-" + datetime.now().strftime("%Y%m%d-%H%M%S")
shutil.copy2(db_path, backup)

conn = sqlite3.connect(db_path)
try:
    rows = conn.execute(
        "SELECT id, codex_summary FROM notes WHERE CAST(note_date AS INTEGER) >= 7"
    ).fetchall()
    for note_id, summary in rows:
        if not summary:
            continue
        # Sections already separated by one newline become visually distinct paragraphs.
        formatted = summary.replace("\r\n", "\n").replace("\n", "\n\n")
        conn.execute(
            "UPDATE notes SET codex_summary=?, updated_at=datetime('now','localtime') WHERE id=?",
            (formatted, note_id),
        )
    conn.commit()
    print(f"formatted={len(rows)} backup={backup}")
finally:
    conn.close()
