import os
import shutil
import sqlite3
from datetime import datetime


db_path = os.path.expandvars(r"%APPDATA%\CNotes\notes.db")
backup = db_path + ".bak-day11-1-ep96-" + datetime.now().strftime("%Y%m%d-%H%M%S")
shutil.copy2(db_path, backup)

text = """【总结】第96集主要讲字符串搜索函数。C语言字符串本质上是以 '\\0' 结尾的 char 数组，搜索函数不会复制字符串，而是返回一个指向原字符串中匹配位置的 char*。因此返回结果可以直接当作字符串使用，也可以通过解引用读取匹配到的字符。常用函数包括 strchr、strrchr 和 strstr：strchr 从左到右查找字符，strrchr 从右到左查找字符，strstr 查找一段子字符串。\n\n【用法一：strchr 查找字符】函数原型是 char *strchr(const char *s, int c);。s 是要搜索的字符串，c 是要查找的字符，返回值是第一次出现该字符的位置。例如：char s[] = \"hello world\"; char *p = strchr(s, 'o');。此时 p 指向字符串中的第一个 o，printf(\"%s\\n\", p) 会输出 \"o world\"，*p 则是字符 'o'。因为返回的是地址，所以可以用 p - s 计算字符下标：if (p != NULL) printf(\"位置=%td\\n\", p - s);。\n\n【用法二：连续查找同一个字符】strchr 返回第一次匹配的位置，要找下一次出现的位置，可以从上一次结果之后继续查找：p = strchr(s, 'l'); if (p != NULL) p = strchr(p + 1, 'l');。这里 p + 1 表示跳过已经找到的字符，从下一个字符开始搜索。这个写法可以放进循环，依次统计字符出现次数或打印所有位置。\n\n【用法三：strrchr 从右侧查找】函数原型是 char *strrchr(const char *s, int c);，作用是返回字符最后一次出现的位置。例如 char path[] = \"C:/work/main.c\"; char *dot = strrchr(path, '.');，dot 指向最后一个点号，printf(\"%s\\n\", dot) 会输出 \".c\"。它常用于获取文件扩展名、最后一个目录分隔符或字符串最后一个分隔位置。\n\n【用法四：strstr 查找子字符串】函数原型是 char *strstr(const char *s1, const char *s2);，在 s1 中查找 s2 第一次出现的位置。例如 char sentence[] = \"I like C language\"; char *p = strstr(sentence, \"C\");，p 指向 \"C language\"；若写 strstr(sentence, \"Java\")，找不到时返回 NULL。判断是否包含某个单词可以写 if (strstr(sentence, \"C\") != NULL)。找到后还可以用 p - sentence 得到子串起始下标。\n\n【综合用法】搜索函数返回的是原数组内部的指针，不会新建字符串。若想把匹配位置之后的内容复制出来，可以先计算 strlen(p) + 1 申请空间，再用 strcpy；若只想截取匹配位置以前的内容，可以用下标或长度配合 memcpy。使用 strchr 处理输入时，还可以用它寻找 fgets 保存的换行符，再把换行符改成 '\\0'。这些函数适合做文件名后缀判断、命令关键字识别、路径解析、文本过滤和简单的字符串分割。"""

conn = sqlite3.connect(db_path)
try:
    row = conn.execute("SELECT id FROM notes WHERE id=77").fetchone()
    if not row:
        raise RuntimeError("找不到 day11之1 对应记录(id=77)")
    conn.execute(
        "UPDATE notes SET codex_summary=?, updated_at=datetime('now','localtime') WHERE id=77",
        (text,),
    )
    conn.commit()
finally:
    conn.close()

print(f"updated_id=77 chars={len(text)} backup={backup}")
