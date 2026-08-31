# CNotes

CNotes 是一个用于记录每日 C 语言学习笔记的 Windows 桌面应用。

## 已实现功能

- 每日笔记：按日期、标题、知识点保存学习内容。
- C 代码区：适合粘贴当天练习代码，带基础语法高亮。
- 编译运行：自动寻找 GCC，支持 `C:\msys64\ucrt64\bin\gcc.exe` 或 PATH 中的 gcc。
- 程序输入：需要 scanf 时，可在“程序输入”页签里提前填写输入。
- 图片笔记：可把 png、jpg、gif、bmp、webp 图片拖入“今天笔记”或“复盘”，也可点击“添加图片”；正文不会插入图片路径或额外说明文字。
- 图片预览：图片会以缩略图显示在笔记区，点击缩略图可放大查看。
- Markdown 导出：把笔记、翁凯课总结、代码和复盘一起导出。

## 直接运行

如果电脑有 Python：

```powershell
python .\src\c_notes.py
```

或双击：

```text
run_cnotes.bat
```

数据会保存在：

```text
%APPDATA%\CNotes\notes.db
```

拖入的图片会复制到：

```text
%APPDATA%\CNotes\images
```

## 构建 exe

在 PowerShell 中运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\build_portable.ps1
```

成功后会生成：

```text
dist\CNotes.exe
releases\CNotes-Windows.zip
```

构建脚本会使用系统 Python 创建 `.venv`，并通过 PyInstaller 打包。请使用带 Tkinter 的 Python 安装版；从 python.org 安装的 Windows Python 默认包含 Tkinter。

## 使用建议

每天至少记录三件事：

- 今天学到的概念。
- 一段能运行或正在报错的 C 代码。
- 自己最困惑的一点，以及第二天要复习的问题。
