from __future__ import annotations

import datetime as dt
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path
from tkinter import (
    BOTH,
    DISABLED,
    END,
    HORIZONTAL,
    INSERT,
    LEFT,
    NORMAL,
    RIGHT,
    VERTICAL,
    WORD,
    Button,
    Entry,
    Frame,
    Label,
    Listbox,
    Menu,
    PanedWindow,
    Scrollbar,
    StringVar,
    Text,
    Tk,
    Toplevel,
    filedialog,
    messagebox,
)
from tkinter import ttk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None


APP_NAME = "CNotes"
TITLE = "CNotes - C 语言学习笔记"
DB_NAME = "notes.db"
WINDOW_SIZE = "1280x760"
COMMON_GCC = Path(r"C:\msys64\ucrt64\bin\gcc.exe")
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
IMAGE_MARKER_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
NOTE_IMAGE_MARKER_RE = re.compile(r"\[图片\]")

C_KEYWORDS = {
    "auto",
    "break",
    "case",
    "char",
    "const",
    "continue",
    "default",
    "do",
    "double",
    "else",
    "enum",
    "extern",
    "float",
    "for",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "register",
    "restrict",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "struct",
    "switch",
    "typedef",
    "union",
    "unsigned",
    "void",
    "volatile",
    "while",
}

TYPE_WORDS = (
    "int",
    "char",
    "float",
    "double",
    "long",
    "short",
    "unsigned",
    "signed",
    "void",
    "size_t",
    "bool",
)


def app_data_dir() -> Path:
    root = Path(os.environ.get("APPDATA", Path.home())) / APP_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def database_path() -> Path:
    return app_data_dir() / DB_NAME


def images_root() -> Path:
    root = app_data_dir() / "images"
    root.mkdir(parents=True, exist_ok=True)
    return root


def image_store_dir(note_id: int) -> Path:
    root = images_root() / str(note_id)
    root.mkdir(parents=True, exist_ok=True)
    return root


def today_text() -> str:
    return dt.date.today().isoformat()


def now_text() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def compact_space(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def strip_comments(code: str) -> str:
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.S)
    code = re.sub(r"//.*", "", code)
    return code


def safe_filename(value: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]+', "_", value.strip())
    name = re.sub(r"\s+", "_", name)
    return name[:80] or "CNotes"


def is_image_path(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


class NotesStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.setup()

    def setup(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_date TEXT NOT NULL,
                title TEXT NOT NULL,
                topics TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL DEFAULT '',
                codex_summary TEXT NOT NULL DEFAULT '',
                code TEXT NOT NULL DEFAULT '',
                reflection TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        columns = {row[1] for row in self.conn.execute("PRAGMA table_info(notes)")}
        if "codex_summary" not in columns:
            self.conn.execute("ALTER TABLE notes ADD COLUMN codex_summary TEXT NOT NULL DEFAULT ''")
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS note_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL,
                area TEXT NOT NULL,
                display_order INTEGER NOT NULL,
                original_name TEXT NOT NULL,
                stored_path TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def list_notes(self, keyword: str = "") -> list[sqlite3.Row]:
        keyword = keyword.strip()
        if keyword:
            like = f"%{keyword}%"
            cursor = self.conn.execute(
                """
                SELECT * FROM notes
                WHERE note_date LIKE ? OR title LIKE ? OR topics LIKE ? OR summary LIKE ? OR codex_summary LIKE ? OR code LIKE ? OR reflection LIKE ?
                ORDER BY
                    CASE WHEN note_date LIKE '数据%' THEN 0 ELSE 1 END,
                    CASE WHEN note_date LIKE '数据%' THEN CAST(SUBSTR(note_date, 3) AS INTEGER) END DESC,
                    CASE WHEN note_date NOT LIKE '数据%' THEN CAST(note_date AS INTEGER) END DESC,
                    updated_at DESC
                """,
                (like, like, like, like, like, like, like),
            )
        else:
            cursor = self.conn.execute(
                """
                SELECT * FROM notes
                ORDER BY
                    CASE WHEN note_date LIKE '数据%' THEN 0 ELSE 1 END,
                    CASE WHEN note_date LIKE '数据%' THEN CAST(SUBSTR(note_date, 3) AS INTEGER) END DESC,
                    CASE WHEN note_date NOT LIKE '数据%' THEN CAST(note_date AS INTEGER) END DESC,
                    updated_at DESC
                """
            )
        return list(cursor.fetchall())

    def get_note(self, note_id: int) -> sqlite3.Row | None:
        cursor = self.conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        return cursor.fetchone()

    def create_note(self, note_date: str | None = None) -> int:
        created = now_text()
        date_value = note_date or today_text()
        cursor = self.conn.execute(
            """
            INSERT INTO notes (note_date, title, topics, summary, code, reflection, created_at, updated_at)
            VALUES (?, ?, '', ?, ?, '', ?, ?)
            """,
            (
                date_value,
                f"{date_value} C 语言学习",
                "今天学到：\n\n卡住的地方：\n\n明天复习：",
                "#include <stdio.h>\n\nint main(void)\n{\n    printf(\"Hello, C language!\\n\");\n    return 0;\n}\n",
                created,
                created,
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def save_note(
        self,
        note_id: int | None,
        note_date: str,
        title: str,
        topics: str,
        summary: str,
        codex_summary: str,
        code: str,
        reflection: str,
    ) -> int:
        title = title.strip() or f"{note_date} C 语言学习"
        note_date = note_date.strip() or today_text()
        updated = now_text()
        if note_id is None:
            cursor = self.conn.execute(
                """
                INSERT INTO notes (note_date, title, topics, summary, codex_summary, code, reflection, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (note_date, title, topics, summary, codex_summary, code, reflection, updated, updated),
            )
            self.conn.commit()
            return int(cursor.lastrowid)

        self.conn.execute(
            """
            UPDATE notes
            SET note_date = ?, title = ?, topics = ?, summary = ?, codex_summary = ?, code = ?, reflection = ?, updated_at = ?
            WHERE id = ?
            """,
            (note_date, title, topics, summary, codex_summary, code, reflection, updated, note_id),
        )
        self.conn.commit()
        return note_id

    def delete_note(self, note_id: int) -> None:
        self.conn.execute("DELETE FROM note_images WHERE note_id = ?", (note_id,))
        self.conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        self.conn.commit()

    def add_image(self, note_id: int, area: str, original_name: str, stored_path: Path) -> int:
        cursor = self.conn.execute(
            "SELECT COALESCE(MAX(display_order), 0) + 1 FROM note_images WHERE note_id = ? AND area = ?",
            (note_id, area),
        )
        display_order = int(cursor.fetchone()[0])
        cursor = self.conn.execute(
            """
            INSERT INTO note_images (note_id, area, display_order, original_name, stored_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (note_id, area, display_order, original_name, str(stored_path), now_text()),
        )
        self.conn.commit()
        return int(cursor.lastrowid)

    def list_images(self, note_id: int, area: str) -> list[sqlite3.Row]:
        cursor = self.conn.execute(
            """
            SELECT * FROM note_images
            WHERE note_id = ? AND area = ?
            ORDER BY display_order ASC, id ASC
            """,
            (note_id, area),
        )
        return list(cursor.fetchall())

    def image_exists(self, note_id: int, area: str, stored_path: Path) -> bool:
        cursor = self.conn.execute(
            """
            SELECT 1 FROM note_images
            WHERE note_id = ? AND area = ? AND stored_path = ?
            LIMIT 1
            """,
            (note_id, area, str(stored_path)),
        )
        return cursor.fetchone() is not None

    def close(self) -> None:
        self.conn.close()


class CNotesApp:
    def __init__(self) -> None:
        root_class = TkinterDnD.Tk if TkinterDnD is not None else Tk
        self.root = root_class()
        self.root.title(TITLE)
        self.root.geometry("1380x820")
        self.root.minsize(1080, 680)

        self.store = NotesStore(database_path())
        self.current_note_id: int | None = None
        self.note_ids: list[int] = []
        self.search_var = StringVar()
        self.date_var = StringVar(value=today_text())
        self.title_var = StringVar()
        self.topics_var = StringVar()
        self.status_var = StringVar(value=f"数据位置：{database_path()}")
        self._highlight_after: str | None = None
        self.image_refs: list[object] = []
        self.image_panels: list[tuple[Text, Frame]] = []

        self.setup_style()
        self.build_layout()
        self.bind_shortcuts()
        self.refresh_list()
        if self.note_ids:
            self.load_note(self.note_ids[0])
        else:
            self.new_today_note()

    def setup_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        self.root.option_add("*Font", ("Microsoft YaHei UI", 11))
        self.root.option_add("*Text.Font", ("Microsoft YaHei UI", 11))
        self.root.configure(bg="#f5f7fb")
        style.configure("TNotebook", background="#ffffff", borderwidth=0)
        style.configure("TNotebook.Tab", font=("Microsoft YaHei UI", 10, "bold"), padding=(18, 10))
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#175cd3")])
        style.configure("TButton", padding=(10, 6))

    def build_layout(self) -> None:
        main = PanedWindow(self.root, orient=HORIZONTAL, sashwidth=6, bg="#d9dee7")
        main.pack(fill=BOTH, expand=True)

        left = Frame(main, bg="#f6f7f9", padx=12, pady=12)
        main.add(left, width=270, minsize=240)
        self.build_sidebar(left)

        workspace = PanedWindow(main, orient=HORIZONTAL, sashwidth=6, bg="#d9dee7")
        main.add(workspace, minsize=780)

        editor = Frame(workspace, bg="#ffffff", padx=12, pady=12)
        output = Frame(workspace, bg="#ffffff", padx=12, pady=12)
        workspace.add(editor, width=820, minsize=650)
        workspace.add(output, width=330, minsize=260)

        self.build_editor(editor)
        self.build_output_panel(output)

        status = Label(self.root, textvariable=self.status_var, anchor="w", bg="#eef1f5", fg="#415065", padx=10)
        status.pack(fill="x")

    def build_sidebar(self, parent: Frame) -> None:
        Label(parent, text="每日 C 笔记", bg="#f6f7f9", fg="#1d2733", font=("Microsoft YaHei UI", 15, "bold")).pack(
            anchor="w"
        )
        Label(parent, text="按日期、标题、知识点或代码搜索", bg="#f6f7f9", fg="#6a7483").pack(anchor="w", pady=(2, 10))
        search = Entry(parent, textvariable=self.search_var)
        search.pack(fill="x")
        search.bind("<KeyRelease>", lambda _event: self.refresh_list())

        list_frame = Frame(parent, bg="#f6f7f9")
        list_frame.pack(fill=BOTH, expand=True, pady=10)
        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side=RIGHT, fill="y")
        self.notes_list = Listbox(
            list_frame,
            activestyle="none",
            exportselection=False,
            yscrollcommand=scrollbar.set,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#d5dae3",
            selectbackground="#2d6cdf",
            selectforeground="#ffffff",
        )
        self.notes_list.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.notes_list.yview)
        self.notes_list.bind("<<ListboxSelect>>", self.on_note_selected)

        button_row = Frame(parent, bg="#f6f7f9")
        button_row.pack(fill="x")
        ttk.Button(button_row, text="新建今天", command=self.new_today_note).pack(side=LEFT, fill="x", expand=True, padx=(0, 4))
        ttk.Button(button_row, text="刷新", command=self.refresh_from_database).pack(side=LEFT, fill="x", expand=True, padx=4)
        ttk.Button(button_row, text="删除", command=self.delete_current_note).pack(side=LEFT, fill="x", expand=True, padx=(4, 0))

        ttk.Button(parent, text="导入 .c 文件", command=self.import_c_file).pack(fill="x", pady=(10, 0))
        ttk.Button(parent, text="导出 Markdown", command=self.export_markdown).pack(fill="x", pady=(8, 0))

        Label(parent, text="建议节奏：每天一段代码 + 一个困惑 + 一个复盘。", bg="#f6f7f9", fg="#6a7483", wraplength=230).pack(
            anchor="w", pady=(14, 0)
        )

    def build_editor(self, parent: Frame) -> None:
        meta = Frame(parent, bg="#ffffff")
        meta.pack(fill="x")

        Label(meta, text="日期", bg="#ffffff", fg="#4b5565").grid(row=0, column=0, sticky="w")
        Entry(meta, textvariable=self.date_var, width=14).grid(row=1, column=0, sticky="we", padx=(0, 10))
        Label(meta, text="标题", bg="#ffffff", fg="#4b5565").grid(row=0, column=1, sticky="w")
        Entry(meta, textvariable=self.title_var).grid(row=1, column=1, sticky="we", padx=(0, 10))
        Label(meta, text="知识点标签", bg="#ffffff", fg="#4b5565").grid(row=0, column=2, sticky="w")
        Entry(meta, textvariable=self.topics_var).grid(row=1, column=2, sticky="we")
        meta.columnconfigure(1, weight=2)
        meta.columnconfigure(2, weight=1)

        toolbar = Frame(parent, bg="#ffffff")
        toolbar.pack(fill="x", pady=(10, 8))
        ttk.Button(toolbar, text="保存 Ctrl+S", command=self.save_current_note).pack(side=LEFT)
        ttk.Button(toolbar, text="编译运行 F5", command=self.compile_and_run).pack(side=LEFT, padx=(8, 0))
        ttk.Button(toolbar, text="添加图片", command=self.choose_images).pack(side=LEFT, padx=(8, 0))

        content = PanedWindow(parent, orient=VERTICAL, sashwidth=6, bg="#d9dee7")
        content.pack(fill=BOTH, expand=True)

        note_panel = Frame(content, bg="#ffffff")
        code_panel = Frame(content, bg="#ffffff")
        content.add(note_panel, height=430, minsize=260)
        content.add(code_panel, height=250, minsize=190)

        notebook = ttk.Notebook(note_panel)
        notebook.pack(fill=BOTH, expand=True)

        self.summary_text = self.make_text(notebook, "课堂笔记")
        self.codex_summary_text = self.make_text(notebook, "翁凯课总结", font=("Microsoft YaHei UI", 11))
        self.reflection_text = self.make_text(notebook, "复盘")
        self.input_text = self.make_text(notebook, "程序输入", height=6)
        self.code_text = self.make_code_box(code_panel)

        self.code_text.bind("<KeyRelease>", self.schedule_highlight)
        self.codex_summary_text.bind("<KeyRelease>", lambda _event: self.format_codex_summary())
        self.install_code_context_menu()
        self.enable_image_drop(self.summary_text)
        self.enable_image_drop(self.reflection_text)

    def build_output_panel(self, parent: Frame) -> None:
        Label(
            parent,
            text="运行结果",
            bg="#ffffff",
            fg="#1d2733",
            font=("Microsoft YaHei UI", 14, "bold"),
        ).pack(anchor="w")
        Label(
            parent,
            text="编译运行后的输出会显示在这里",
            bg="#ffffff",
            fg="#6a7483",
        ).pack(anchor="w", pady=(2, 8))

        frame = Frame(parent, bg="#ffffff")
        frame.pack(fill=BOTH, expand=True)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill="y")
        self.output_text = Text(
            frame,
            wrap=WORD,
            borderwidth=0,
            padx=12,
            pady=12,
            yscrollcommand=scrollbar.set,
            bg="#fbfcfe",
            fg="#17202a",
            highlightthickness=1,
            highlightbackground="#dce1ea",
            selectbackground="#cfe0ff",
            selectforeground="#102a56",
            font=("Consolas", 10),
        )
        self.output_text.pack(side=LEFT, fill=BOTH, expand=True)
        self.output_text.configure(state=DISABLED)
        scrollbar.config(command=self.output_text.yview)

    def make_text(
        self,
        notebook: ttk.Notebook,
        title: str,
        readonly: bool = False,
        font: tuple[str, int] | tuple[str, int, str] | None = None,
        height: int | None = None,
    ) -> Text:
        frame = Frame(notebook, bg="#ffffff")
        notebook.add(frame, text=title)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill="y")
        text = Text(
            frame,
            wrap=WORD,
            undo=True,
            height=height or 20,
            borderwidth=0,
            padx=12,
            pady=12,
            yscrollcommand=scrollbar.set,
            bg="#fbfcfe",
            fg="#17202a",
            insertbackground="#17202a",
            highlightthickness=1,
            highlightbackground="#dce1ea",
            selectbackground="#cfe0ff",
            selectforeground="#102a56",
            spacing1=3,
            spacing2=2,
            spacing3=7,
        )
        if font:
            text.configure(font=font)
        text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=text.yview)
        if readonly:
            text.configure(state=DISABLED)
        return text

    def make_code_box(self, parent: Frame) -> Text:
        header = Frame(parent, bg="#eef4ff", padx=10, pady=7)
        header.pack(fill="x", pady=(8, 0))
        Label(
            header,
            text="C 代码显示框",
            bg="#eef4ff",
            fg="#173b72",
            font=("Microsoft YaHei UI", 11, "bold"),
        ).pack(side=LEFT)
        Label(
            header,
            text="固定显示 · 语法高亮 · 可编译运行",
            bg="#eef4ff",
            fg="#5b6b82",
        ).pack(side=LEFT, padx=(12, 0))

        frame = Frame(parent, bg="#ffffff")
        frame.pack(fill=BOTH, expand=True)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill="y")
        text = Text(
            frame,
            wrap="none",
            undo=True,
            borderwidth=0,
            padx=14,
            pady=12,
            yscrollcommand=scrollbar.set,
            bg="#101826",
            fg="#d8e2f2",
            insertbackground="#ffffff",
            highlightthickness=1,
            highlightbackground="#26364f",
            selectbackground="#284a76",
            selectforeground="#ffffff",
            tabs=("32p",),
            font=("Cascadia Code", 11),
        )
        text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=text.yview)
        return text

    def bind_shortcuts(self) -> None:
        self.root.bind("<Control-s>", lambda _event: self.save_current_note())
        self.root.bind("<F5>", lambda _event: self.compile_and_run())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def install_code_context_menu(self) -> None:
        menu = Menu(self.root, tearoff=0)
        menu.add_command(label="编译运行", command=self.compile_and_run)
        menu.add_separator()
        menu.add_command(label="复制", command=lambda: self.root.focus_get().event_generate("<<Copy>>"))
        menu.add_command(label="粘贴", command=lambda: self.root.focus_get().event_generate("<<Paste>>"))

        def popup(event) -> None:
            menu.tk_popup(event.x_root, event.y_root)

        self.code_text.bind("<Button-3>", popup)

    def refresh_list(self) -> None:
        selected_id = self.current_note_id
        notes = self.store.list_notes(self.search_var.get())
        self.notes_list.delete(0, END)
        self.note_ids = []
        for note in notes:
            label = f"{note['note_date']}  {note['title']}"
            if note["topics"].strip():
                label += f"  [{note['topics']}]"
            self.note_ids.append(int(note["id"]))
            self.notes_list.insert(END, label)

        if selected_id in self.note_ids:
            index = self.note_ids.index(selected_id)
            self.notes_list.selection_set(index)
            self.notes_list.see(index)
        self.status_var.set(f"共 {len(self.note_ids)} 篇笔记 · 数据位置：{database_path()}")

    def refresh_from_database(self) -> None:
        selected_id = self.current_note_id
        self.refresh_list()
        if selected_id in self.note_ids:
            self.load_note(selected_id)
        elif self.note_ids:
            self.load_note(self.note_ids[0])
        else:
            self.clear_editor()
        self.status_var.set(f"已刷新 · 共 {len(self.note_ids)} 篇笔记")

    def on_note_selected(self, _event=None) -> None:
        selection = self.notes_list.curselection()
        if not selection:
            return
        note_id = self.note_ids[int(selection[0])]
        if note_id != self.current_note_id:
            self.load_note(note_id)

    def load_note(self, note_id: int) -> None:
        note = self.store.get_note(note_id)
        if note is None:
            return
        self.current_note_id = note_id
        summary = self.migrate_legacy_image_markers(note_id, "summary", note["summary"])
        reflection = self.migrate_legacy_image_markers(note_id, "reflection", note["reflection"])
        if summary != note["summary"] or reflection != note["reflection"]:
            self.store.save_note(
                note_id,
                note["note_date"],
                note["title"],
                note["topics"],
                summary,
                note["codex_summary"],
                note["code"],
                reflection,
            )
            note = self.store.get_note(note_id)
            if note is None:
                return
        self.date_var.set(note["note_date"])
        self.title_var.set(note["title"])
        self.topics_var.set(note["topics"])
        self.set_text(self.summary_text, note["summary"])
        self.set_text(self.codex_summary_text, note["codex_summary"])
        self.format_codex_summary()
        self.set_text(self.code_text, note["code"])
        self.set_text(self.reflection_text, note["reflection"])
        self.render_note_images()
        self.highlight_code()

    def new_today_note(self) -> None:
        note_id = self.store.create_note(today_text())
        self.current_note_id = note_id
        self.refresh_list()
        self.load_note(note_id)
        self.status_var.set("已新建今天的 C 语言学习笔记。")

    def save_current_note(self) -> int:
        note_id = self.store.save_note(
            self.current_note_id,
            self.date_var.get(),
            self.title_var.get(),
            self.topics_var.get(),
            self.get_text(self.summary_text),
            self.get_text(self.codex_summary_text),
            self.get_text(self.code_text),
            self.get_text(self.reflection_text),
        )
        self.current_note_id = note_id
        self.refresh_list()
        self.status_var.set(f"已保存：{self.title_var.get().strip() or note_id}")
        return note_id

    def delete_current_note(self) -> None:
        if self.current_note_id is None:
            return
        if not messagebox.askyesno("确认删除", "要删除当前笔记吗？此操作无法撤销。"):
            return
        self.store.delete_note(self.current_note_id)
        self.current_note_id = None
        self.refresh_list()
        if self.note_ids:
            self.load_note(self.note_ids[0])
        else:
            self.clear_editor()

    def clear_editor(self) -> None:
        self.date_var.set(today_text())
        self.title_var.set("")
        self.topics_var.set("")
        self.set_text(self.summary_text, "")
        self.set_text(self.codex_summary_text, "")
        self.set_text(self.code_text, "")
        self.set_text(self.reflection_text, "")
        self.render_note_images()

    def compile_and_run(self) -> None:
        self.save_current_note()
        code = self.get_text(self.code_text)
        compiler = self.find_compiler()
        if compiler is None:
            self.write_readonly(
                self.output_text,
                "没有找到 GCC 编译器。\n\n已检查：PATH 中的 gcc，以及 C:\\msys64\\ucrt64\\bin\\gcc.exe。\n"
                "你可以安装 MSYS2/GCC，或在系统 PATH 中加入 gcc.exe。",
            )
            self.status_var.set("未找到 GCC，无法编译运行。")
            return

        with tempfile.TemporaryDirectory(prefix="cnotes_") as temp_dir:
            temp = Path(temp_dir)
            source = temp / "main.c"
            exe = temp / "main.exe"
            source.write_text(code, encoding="utf-8")
            compile_cmd = [
                str(compiler),
                "-Wall",
                "-Wextra",
                "-std=c11",
                str(source),
                "-o",
                str(exe),
            ]
            try:
                build = subprocess.run(compile_cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=12)
            except subprocess.TimeoutExpired:
                self.write_readonly(self.output_text, "编译超时：请检查代码或编译器环境。")
                return

            output: list[str] = []
            output.append("编译命令：")
            output.append(" ".join(compile_cmd))
            output.append("")
            if build.stdout.strip():
                output.append("编译标准输出：")
                output.append(build.stdout)
            if build.stderr.strip():
                output.append("编译警告/错误：")
                output.append(build.stderr)
                output.append("")
            if build.returncode != 0:
                output.append(f"编译失败，退出码：{build.returncode}")
                self.write_readonly(self.output_text, "\n".join(output))
                self.status_var.set("编译失败，先看第一条 error。")
                return

            try:
                run = subprocess.run(
                    [str(exe)],
                    input=self.get_text(self.input_text),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=5,
                )
                output.append("运行输出：")
                output.append(run.stdout if run.stdout else "(程序没有标准输出)")
                if run.stderr.strip():
                    output.append("")
                    output.append("运行错误：")
                    output.append(run.stderr)
                output.append("")
                output.append(f"程序退出码：{run.returncode}")
                self.status_var.set("编译并运行完成。")
            except subprocess.TimeoutExpired:
                output.append("运行超时：程序可能在等待输入，或进入了死循环。可在“程序输入”页签中预先填写输入。")
                self.status_var.set("运行超时。")
            self.write_readonly(self.output_text, "\n".join(output))

    def find_compiler(self) -> Path | None:
        env_cc = os.environ.get("CC")
        candidates = [Path(env_cc)] if env_cc else []
        which = shutil.which("gcc")
        if which:
            candidates.append(Path(which))
        candidates.append(COMMON_GCC)
        for candidate in candidates:
            if candidate and candidate.exists():
                return candidate
        return None

    def import_c_file(self) -> None:
        path = filedialog.askopenfilename(
            title="选择 C 源文件",
            filetypes=[("C source", "*.c *.h"), ("All files", "*.*")],
        )
        if not path:
            return
        content = Path(path).read_text(encoding="utf-8", errors="replace")
        self.set_text(self.code_text, content)
        self.title_var.set(Path(path).stem)
        self.topics_var.set(self.topics_var.get() or "导入代码")
        self.highlight_code()
        self.status_var.set(f"已导入：{path}")

    def choose_images(self) -> None:
        paths = filedialog.askopenfilenames(
            title="选择要加入笔记的图片",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")],
        )
        if not paths:
            return
        target = self.focused_note_text()
        self.add_images_to_text([Path(path) for path in paths], target)

    def focused_note_text(self) -> Text:
        focused = self.root.focus_get()
        if focused in (self.summary_text, self.reflection_text):
            return focused
        return self.summary_text

    def enable_image_drop(self, text: Text) -> None:
        text.bind("<Control-i>", lambda _event: self.choose_images())
        if DND_FILES is None or not hasattr(text, "drop_target_register"):
            return
        text.drop_target_register(DND_FILES)

        def on_drop(event) -> str:
            try:
                text.mark_set(INSERT, text.index(f"@{event.x},{event.y}"))
            except Exception:
                pass
            self.add_images_to_text(self.parse_dropped_paths(event.data), text)
            return "break"

        text.dnd_bind("<<Drop>>", on_drop)

    def parse_dropped_paths(self, data: str) -> list[Path]:
        paths: list[Path] = []
        try:
            raw_paths = self.root.tk.splitlist(data)
        except Exception:
            raw_paths = data.split()
        for raw in raw_paths:
            value = str(raw).strip().strip("{}")
            if value.startswith("file:///"):
                value = value[8:]
            paths.append(Path(value))
        return paths

    def add_images_to_text(self, paths: list[Path], text: Text) -> None:
        image_paths = [path for path in paths if is_image_path(path)]
        if not image_paths:
            self.status_var.set("没有识别到可加入笔记的图片文件。")
            return
        note_id = self.save_current_note()
        inserted = 0
        for source in image_paths:
            stored = self.copy_image_to_note(source, note_id)
            area = self.text_area(text)
            self.store.add_image(note_id, area, source.name, stored)
            inserted += 1
        self.save_current_note()
        self.render_note_images()
        hint = "已加入图片。"
        if DND_FILES is None:
            hint += " 当前环境未启用拖放库，可继续用“添加图片”按钮。"
        self.status_var.set(f"{hint} 数量：{inserted}")

    def copy_image_to_note(self, source: Path, note_id: int) -> Path:
        target_dir = image_store_dir(note_id)
        stem = safe_filename(source.stem)
        suffix = source.suffix.lower()
        target = target_dir / f"{stem}{suffix}"
        counter = 1
        while target.exists() and source.resolve() != target.resolve():
            target = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)
        return target

    def text_area(self, text: Text) -> str:
        return "reflection" if text == self.reflection_text else "summary"

    def migrate_legacy_image_markers(self, note_id: int, area: str, value: str) -> str:
        changed = False

        def replace_marker(match: re.Match[str]) -> str:
            nonlocal changed
            path = Path(match.group(1).strip())
            if path.exists() and not self.store.image_exists(note_id, area, path):
                stored = self.copy_image_to_note(path, note_id)
                self.store.add_image(note_id, area, path.name, stored)
            changed = True
            return ""

        cleaned = IMAGE_MARKER_RE.sub(replace_marker, value)
        if changed:
            cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
        return cleaned

    def render_note_images(self) -> None:
        self.clear_rendered_images()
        self.image_refs = []
        self.render_images_in_text(self.summary_text)
        self.render_images_in_text(self.reflection_text)

    def render_images_in_text(self, text: Text) -> None:
        if Image is None or ImageTk is None:
            return
        if self.current_note_id is None:
            return
        area = self.text_area(text)
        images = self.store.list_images(self.current_note_id, area)
        legacy_paths = [Path(match.group(1).strip()) for match in IMAGE_MARKER_RE.finditer(self.get_text(text))]
        paths: list[Path] = [Path(row["stored_path"]) for row in images]
        paths.extend(path for path in legacy_paths if path.exists())
        if not paths:
            return

        panel = Frame(text, bg="#fbfcfe", padx=4, pady=8)
        self.image_panels.append((text, panel))
        for path in paths:
            if not path.exists():
                continue
            try:
                preview = self.make_thumbnail(path)
            except Exception:
                continue
            label = Label(panel, image=preview, bg="#fbfcfe", cursor="hand2", bd=1, relief="solid")
            label.pack(anchor="w", pady=(0, 8))
            label.bind("<Button-1>", lambda _event, image_path=path: self.open_image_viewer(image_path))
            self.image_refs.append(preview)
        text.window_create(END, window=panel, padx=8, pady=8)

    def clear_rendered_images(self) -> None:
        for text, panel in self.image_panels:
            panel_name = str(panel)
            try:
                for kind, name, index in text.dump("1.0", END, window=True):
                    if kind == "window" and name == panel_name:
                        text.delete(index)
                        break
            except Exception:
                pass
            try:
                panel.destroy()
            except Exception:
                pass
        self.image_panels = []

    def make_thumbnail(self, path: Path):
        if Image is None or ImageTk is None:
            raise RuntimeError("Pillow is not available.")
        image = Image.open(path)
        image.thumbnail((420, 280))
        return ImageTk.PhotoImage(image)

    def open_image_viewer(self, path: Path) -> None:
        if Image is None or ImageTk is None:
            messagebox.showinfo("无法预览", "当前环境没有可用的图片预览库。")
            return
        if not path.exists():
            messagebox.showwarning("图片不存在", "这张图片文件已经不存在。")
            return

        viewer = Toplevel(self.root)
        viewer.title(path.name)
        viewer.geometry("900x680")
        viewer.minsize(520, 360)

        container = Frame(viewer, bg="#111827")
        container.pack(fill=BOTH, expand=True)
        canvas = ttk.Frame(container)
        canvas.pack(fill=BOTH, expand=True, padx=12, pady=12)

        image = Image.open(path)
        image.thumbnail((1200, 900))
        photo = ImageTk.PhotoImage(image)
        label = Label(canvas, image=photo, bg="#111827")
        label.image = photo
        label.pack(fill=BOTH, expand=True)

        footer = Frame(viewer, bg="#f6f7f9", padx=10, pady=8)
        footer.pack(fill="x")
        Label(footer, text=path.name, bg="#f6f7f9", fg="#374151").pack(side=LEFT)
        ttk.Button(footer, text="关闭", command=viewer.destroy).pack(side=RIGHT)

    def export_markdown(self) -> None:
        note_id = self.save_current_note()
        note = self.store.get_note(note_id)
        if note is None:
            return
        default = f"{note['note_date']}_{safe_filename(note['title'])}.md"
        path = filedialog.asksaveasfilename(
            title="导出 Markdown",
            defaultextension=".md",
            initialfile=default,
            filetypes=[("Markdown", "*.md")],
        )
        if not path:
            return
        markdown = (
            f"# {note['title']}\n\n"
            f"- 日期：{note['note_date']}\n"
            f"- 知识点：{note['topics'] or '未填写'}\n\n"
            f"## 今天笔记\n\n{note['summary']}\n\n"
            f"## codex总结\n\n{note['codex_summary']}\n\n"
            f"## C 代码\n\n```c\n{note['code']}\n```\n\n"
            f"## 复盘\n\n{note['reflection']}\n"
        )
        Path(path).write_text(markdown, encoding="utf-8")
        self.status_var.set(f"已导出 Markdown：{path}")

    def schedule_highlight(self, _event=None) -> None:
        if self._highlight_after:
            self.root.after_cancel(self._highlight_after)
        self._highlight_after = self.root.after(180, self.highlight_code)

    def highlight_code(self) -> None:
        self._highlight_after = None
        text = self.code_text
        code = self.get_text(text)
        for tag in ("kw", "str", "comment", "pre", "number", "function"):
            text.tag_remove(tag, "1.0", END)
        text.tag_configure("kw", foreground="#7dd3fc")
        text.tag_configure("str", foreground="#86efac")
        text.tag_configure("comment", foreground="#8b9bb3")
        text.tag_configure("pre", foreground="#fbbf24")
        text.tag_configure("number", foreground="#fca5a5")
        text.tag_configure("function", foreground="#c4b5fd")

        for match in re.finditer(r"\b(" + "|".join(sorted(C_KEYWORDS)) + r")\b", code):
            self.tag_match(text, "kw", match)
        for match in re.finditer(r"\b[A-Za-z_]\w*(?=\s*\()", code):
            if match.group(0) not in C_KEYWORDS:
                self.tag_match(text, "function", match)
        for match in re.finditer(r"\b(?:0x[0-9A-Fa-f]+|\d+(?:\.\d+)?)\b", code):
            self.tag_match(text, "number", match)
        for match in re.finditer(r'"(?:\\.|[^"\\])*"', code):
            self.tag_match(text, "str", match)
        for match in re.finditer(r"//.*|/\*.*?\*/", code, flags=re.S):
            self.tag_match(text, "comment", match)
        for match in re.finditer(r"^\s*#.*", code, flags=re.M):
            self.tag_match(text, "pre", match)

    def tag_match(self, text: Text, tag: str, match: re.Match[str]) -> None:
        start = f"1.0+{match.start()}c"
        end = f"1.0+{match.end()}c"
        text.tag_add(tag, start, end)

    def write_readonly(self, text: Text, value: str) -> None:
        text.configure(state=NORMAL)
        text.delete("1.0", END)
        text.insert("1.0", value)
        text.configure(state=DISABLED)

    def format_codex_summary(self) -> None:
        """Give the saved plain-text summary a clean, chat-like reading hierarchy."""
        text = self.codex_summary_text
        for tag in ("summary_heading", "summary_code", "summary_bullet"):
            text.tag_remove(tag, "1.0", END)
        text.tag_configure(
            "summary_heading",
            font=("Microsoft YaHei UI", 13, "bold"),
            foreground="#175cd3",
            spacing1=12,
            spacing3=7,
        )
        text.tag_configure(
            "summary_code",
            font=("Cascadia Code", 10),
            foreground="#172b4d",
            background="#f1f5f9",
            lmargin1=14,
            lmargin2=14,
            rmargin=14,
            spacing1=1,
            spacing2=1,
            spacing3=1,
        )
        text.tag_configure(
            "summary_bullet",
            foreground="#344054",
            lmargin1=8,
            lmargin2=24,
        )
        in_code = False
        line_count = int(text.index("end-1c").split(".")[0])
        for number in range(1, line_count + 1):
            start = f"{number}.0"
            end = f"{number}.end"
            line = text.get(start, end)
            stripped = line.strip()
            if re.fullmatch(r"【.+】", stripped):
                in_code = stripped == "【示例代码】"
                text.tag_add("summary_heading", start, end)
            elif in_code and stripped:
                text.tag_add("summary_code", start, f"{number + 1}.0")
            elif re.match(r"^(?:[-•] |\d+[.、])", stripped):
                text.tag_add("summary_bullet", start, end)

    def set_text(self, text: Text, value: str) -> None:
        state = str(text.cget("state"))
        if state == DISABLED:
            text.configure(state=NORMAL)
        text.delete("1.0", END)
        text.insert("1.0", value or "")
        if state == DISABLED:
            text.configure(state=DISABLED)

    def get_text(self, text: Text) -> str:
        return text.get("1.0", "end-1c")

    def on_close(self) -> None:
        try:
            self.save_current_note()
        except Exception:
            pass
        try:
            self.store.close()
        except Exception:
            pass
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def run_self_test() -> None:
    assert safe_filename("a/b:c") == "a_b_c"
    assert is_image_path(Path("example.png")) is False
    print("CNotes self-test passed.")


if __name__ == "__main__":
    if os.environ.get("CNOTES_TEST") == "1":
        run_self_test()
        sys.exit(0)
    CNotesApp().run()
