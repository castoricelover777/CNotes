from __future__ import annotations

import datetime as dt
import os
import re
import shutil
import sqlite3
from pathlib import Path


def example_for(topic: str) -> str:
    t = topic.lower()
    if "hello" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    printf("Hello, C!\\n");\n    return 0;\n}'
    if any(k in t for k in ("复杂计算", "计算", "运算符")):
        return '#include <stdio.h>\n\nint main(void)\n{\n    int a = 66, b = 12;\n    printf("和=%d 差=%d 积=%d 余数=%d\\n",\n           a + b, a - b, a * b, a % b);\n    return 0;\n}'
    if "浮点" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    double price = 12.5;\n    int count = 3;\n    printf("总价：%.2f\\n", price * count);\n    return 0;\n}'
    if "优先级" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int x = 2 + 3 * 4;\n    int y = (2 + 3) * 4;\n    printf("x=%d, y=%d\\n", x, y);\n    return 0;\n}'
    if any(k in t for k in ("复合赋值", "递增", "递减")):
        return '#include <stdio.h>\n\nint main(void)\n{\n    int n = 5;\n    n += 3;\n    printf("%d\\n", n++);\n    printf("%d\\n", n);\n    return 0;\n}'
    if "注释" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    // 单行注释：说明下一行为什么这样写\n    int score = 90;\n    /* 多行注释：适合较长说明 */\n    printf("%d\\n", score);\n    return 0;\n}'
    if "switch" in t or "swich" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int choice = 2;\n    switch (choice) {\n    case 1: printf("开始\\n"); break;\n    case 2: printf("设置\\n"); break;\n    default: printf("无效选项\\n");\n    }\n    return 0;\n}'
    if "else" in t or "if" in t or "条件判断" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int score;\n    scanf("%d", &score);\n    if (score >= 90) printf("优秀\\n");\n    else if (score >= 60) printf("及格\\n");\n    else printf("继续努力\\n");\n    return 0;\n}'
    if "do while" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int n = 3;\n    do {\n        printf("%d ", n);\n        n--;\n    } while (n > 0);\n    return 0;\n}'
    if "随机" in t or "猜数" in t:
        return '#include <stdio.h>\n#include <stdlib.h>\n#include <time.h>\n\nint main(void)\n{\n    srand((unsigned)time(NULL));\n    int answer = rand() % 100 + 1, guess;\n    do {\n        scanf("%d", &guess);\n        if (guess < answer) puts("小了");\n        else if (guess > answer) puts("大了");\n    } while (guess != answer);\n    puts("猜对了");\n    return 0;\n}'
    if "求和" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int n, sum = 0;\n    while (scanf("%d", &n) == 1 && n != -1)\n        sum += n;\n    printf("sum=%d\\n", sum);\n    return 0;\n}'
    if "整数翻转" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int n = 12345, reversed = 0;\n    while (n != 0) {\n        reversed = reversed * 10 + n % 10;\n        n /= 10;\n    }\n    printf("%d\\n", reversed);\n    return 0;\n}'
    if "阶乘" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int n = 5;\n    long long result = 1;\n    for (int i = 2; i <= n; i++)\n        result *= i;\n    printf("%d! = %lld\\n", n, result);\n    return 0;\n}'
    if "素数" in t or "循环控制" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int n = 29, is_prime = n >= 2;\n    for (int i = 2; i * i <= n; i++) {\n        if (n % i == 0) { is_prime = 0; break; }\n    }\n    puts(is_prime ? "是素数" : "不是素数");\n    return 0;\n}'
    if "goto" in t or "嵌套" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    for (int a = 1; a <= 10; a++) {\n        for (int b = 1; b <= 10; b++) {\n            if (a + b == 10) {\n                printf("a=%d b=%d\\n", a, b);\n                return 0;  // 找到后直接结束\n            }\n        }\n    }\n    return 0;\n}'
    if "整数分解" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int n = 13425, mask = 10000;\n    while (mask > 0) {\n        printf("%d ", n / mask);\n        n %= mask;\n        mask /= 10;\n    }\n    return 0;\n}'
    if "水仙花" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    for (int n = 100; n <= 999; n++) {\n        int a = n / 100, b = n / 10 % 10, c = n % 10;\n        if (a*a*a + b*b*b + c*c*c == n)\n            printf("%d ", n);\n    }\n    return 0;\n}'
    if "公约数" in t or "辗转" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int a = 48, b = 18;\n    while (b != 0) {\n        int r = a % b;\n        a = b;\n        b = r;\n    }\n    printf("最大公约数=%d\\n", a);\n    return 0;\n}'
    if "16进制" in t or "8进制" in t or "二进制" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    unsigned n = 26;\n    printf("十进制=%u 八进制=%o 十六进制=%X\\n", n, n, n);\n    printf("最低位=%u\\n", n & 1u);\n    return 0;\n}'
    if any(k in t for k in ("整数类型", "整数范围", "数据类型")):
        return '#include <stdio.h>\n#include <limits.h>\n\nint main(void)\n{\n    printf("int占%zu字节，范围%d到%d\\n",\n           sizeof(int), INT_MIN, INT_MAX);\n    return 0;\n}'
    if "逃逸" in t or "字符" == t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    char grade = \'A\';\n    printf("字符：%c\\n制表符：\\t路径：C:\\\\temp\\n", grade);\n    return 0;\n}'
    if "短路" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int p = 0;\n    if (p != 0 && 100 / p > 2)\n        puts("成立");\n    return 0;\n}'
    if "逻辑" in t or "与或非" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int age = 20, has_id = 1;\n    printf("可进入：%d\\n", age >= 18 && has_id);\n    printf("不满足：%d\\n", !(age >= 18));\n    return 0;\n}'
    if "条件运算符" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int a = 7, b = 12;\n    int max = a > b ? a : b;\n    printf("max=%d\\n", max);\n    return 0;\n}'
    if "参数传递" in t:
        return '#include <stdio.h>\n\nvoid swap(int *a, int *b)\n{\n    int temp = *a; *a = *b; *b = temp;\n}\n\nint main(void)\n{\n    int x = 3, y = 8;\n    swap(&x, &y);\n    printf("%d %d\\n", x, y);\n    return 0;\n}'
    if "本地变量" in t or "全局变量" in t or "静态本地" in t:
        return '#include <stdio.h>\n\nint global_count = 0;\nvoid visit(void)\n{\n    static int times = 0;\n    int local = 10;\n    printf("times=%d local=%d global=%d\\n", ++times, local, ++global_count);\n}\nint main(void) { visit(); visit(); return 0; }'
    if "函数" in t:
        return '#include <stdio.h>\n\nint add(int a, int b)\n{\n    return a + b;\n}\n\nint main(void)\n{\n    printf("%d\\n", add(3, 5));\n    return 0;\n}'
    if "二维数组" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int grid[2][3] = {{1, 2, 3}, {4, 5, 6}};\n    for (int r = 0; r < 2; r++) {\n        for (int c = 0; c < 3; c++) printf("%d ", grid[r][c]);\n        putchar(\'\\n\');\n    }\n    return 0;\n}'
    if "数组大小" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int numbers[] = {10, 20, 30, 40};\n    size_t count = sizeof(numbers) / sizeof(numbers[0]);\n    printf("元素个数=%zu\\n", count);\n    return 0;\n}'
    if "数组" in t and "字符串" not in t and "可变" not in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int scores[5] = {86, 92, 75, 88, 90};\n    int sum = 0;\n    for (size_t i = 0; i < 5; i++) sum += scores[i];\n    printf("平均分=%.1f\\n", sum / 5.0);\n    return 0;\n}'
    if "取地址" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int value = 42;\n    int *p = &value;\n    printf("值=%d 地址=%p 指针取值=%d\\n", value, (void *)&value, *p);\n    return 0;\n}'
    if "指针与const" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int a = 10, b = 20;\n    const int *p = &a;  // 不能通过p改值\n    p = &b;             // 可以改变p的指向\n    printf("%d\\n", *p);\n    return 0;\n}'
    if "指针运算" in t or "数组和指针" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int a[] = {10, 20, 30};\n    int *p = a;\n    for (size_t i = 0; i < 3; i++)\n        printf("%d ", *(p + i));\n    return 0;\n}'
    if "指针" in t:
        return '#include <stdio.h>\n\nvoid double_value(int *p) { *p *= 2; }\nint main(void)\n{\n    int n = 7;\n    double_value(&n);\n    printf("%d\\n", n);\n    return 0;\n}'
    if "动态内存" in t:
        return '#include <stdio.h>\n#include <stdlib.h>\n\nint main(void)\n{\n    size_t n = 5;\n    int *a = malloc(n * sizeof *a);\n    if (a == NULL) return 1;\n    for (size_t i = 0; i < n; i++) a[i] = (int)i * 10;\n    free(a);\n    a = NULL;\n    return 0;\n}'
    if "程序参数" in t:
        return '#include <stdio.h>\n\nint main(int argc, char *argv[])\n{\n    printf("参数个数=%d\\n", argc);\n    for (int i = 0; i < argc; i++)\n        printf("argv[%d]=%s\\n", i, argv[i]);\n    return 0;\n}'
    if "strlen" in t:
        return '#include <stdio.h>\n#include <string.h>\n\nint main(void)\n{\n    const char text[] = "hello";\n    printf("长度=%zu，占用=%zu\\n", strlen(text), sizeof(text));\n    return 0;\n}'
    if "strcmp" in t:
        return '#include <stdio.h>\n#include <string.h>\n\nint main(void)\n{\n    const char *a = "apple", *b = "banana";\n    int result = strcmp(a, b);\n    puts(result < 0 ? "a排在b前" : result > 0 ? "a排在b后" : "相等");\n    return 0;\n}'
    if "strcpy" in t or "strcat" in t:
        return '#include <stdio.h>\n#include <string.h>\n\nint main(void)\n{\n    char result[32] = "Hello";\n    strcat(result, ", C");\n    printf("%s\\n", result);\n    return 0;\n}'
    if "搜索函数" in t:
        return '#include <stdio.h>\n#include <string.h>\n\nint main(void)\n{\n    const char *text = "learn C language";\n    const char *found = strstr(text, "C");\n    if (found != NULL) printf("找到：%s\\n", found);\n    return 0;\n}'
    if "字符串输入输出" in t:
        return '#include <stdio.h>\n#include <string.h>\n\nint main(void)\n{\n    char line[100];\n    if (fgets(line, sizeof line, stdin) != NULL) {\n        line[strcspn(line, "\\n")] = \'\\0\';\n        printf("你输入了：%s\\n", line);\n    }\n    return 0;\n}'
    if "字符串数组" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    const char *colors[] = {"red", "green", "blue"};\n    size_t count = sizeof colors / sizeof colors[0];\n    for (size_t i = 0; i < count; i++) puts(colors[i]);\n    return 0;\n}'
    if "字符串常量" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    const char *message = "Hello";\n    printf("%s\\n", message);\n    return 0;\n}'
    if "字符串" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    char name[] = "Codex";\n    for (size_t i = 0; name[i] != \'\\0\'; i++)\n        printf("%c ", name[i]);\n    return 0;\n}'
    if "枚举" in t:
        return '#include <stdio.h>\n\nenum Day { MON = 1, TUE, WED };\nint main(void)\n{\n    enum Day today = TUE;\n    printf("%d\\n", today);\n    return 0;\n}'
    if "结构和函数" in t:
        return '#include <stdio.h>\n\ntypedef struct { int x, y; } Point;\nvoid move(Point *p, int dx, int dy) { p->x += dx; p->y += dy; }\nint main(void)\n{\n    Point p = {2, 3};\n    move(&p, 4, -1);\n    printf("(%d, %d)\\n", p.x, p.y);\n    return 0;\n}'
    if "结构" in t:
        return '#include <stdio.h>\n\nstruct Student { char name[20]; int score; };\nint main(void)\n{\n    struct Student s = {"Lele", 95};\n    printf("%s：%d\\n", s.name, s.score);\n    return 0;\n}'
    if "定义类型" in t:
        return '#include <stdio.h>\n\ntypedef unsigned long ulong;\ntypedef struct { int x, y; } Point;\nint main(void)\n{\n    ulong count = 100; Point p = {3, 4};\n    printf("%lu (%d,%d)\\n", count, p.x, p.y);\n    return 0;\n}'
    if "联合" in t:
        return '#include <stdio.h>\n\nunion Value { int number; float decimal; };\nint main(void)\n{\n    union Value v;\n    v.number = 42;\n    printf("%d，联合大小=%zu\\n", v.number, sizeof v);\n    return 0;\n}'
    if "参数宏" in t:
        return '#include <stdio.h>\n\n#define SQUARE(x) ((x) * (x))\n#define MAX(a, b) ((a) > (b) ? (a) : (b))\nint main(void)\n{\n    printf("%d %d\\n", SQUARE(5), MAX(3, 8));\n    return 0;\n}'
    if "宏" in t:
        return '#include <stdio.h>\n\n#define PI 3.1415926\n#define ARRAY_LEN(a) (sizeof(a) / sizeof((a)[0]))\nint main(void)\n{\n    int a[] = {1, 2, 3};\n    printf("PI=%.2f 个数=%zu\\n", PI, ARRAY_LEN(a));\n    return 0;\n}'
    if "源代码文件" in t or "声明" in t:
        return '// math_utils.h\n#ifndef MATH_UTILS_H\n#define MATH_UTILS_H\nint add(int a, int b);\n#endif\n\n// math_utils.c\n#include "math_utils.h"\nint add(int a, int b) { return a + b; }'
    if "格式化输入输出表格" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    printf("%-10s %6s\\n", "姓名", "分数");\n    printf("%-10s %6d\\n", "Lele", 95);\n    printf("%-10s %6.1f\\n", "平均", 88.5);\n    return 0;\n}'
    if "格式化输入输出" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    int age; double height;\n    if (scanf("%d %lf", &age, &height) == 2)\n        printf("年龄=%d 身高=%.2f\\n", age, height);\n    return 0;\n}'
    if "文件输入输出" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    FILE *fp = fopen("note.txt", "w");\n    if (fp == NULL) { perror("fopen"); return 1; }\n    fprintf(fp, "Hello, file!\\n");\n    if (fclose(fp) != 0) return 1;\n    return 0;\n}'
    if "位段" in t:
        return '#include <stdio.h>\n\nstruct Flags { unsigned ready : 1; unsigned mode : 2; };\nint main(void)\n{\n    struct Flags f = {1, 2};\n    printf("ready=%u mode=%u\\n", f.ready, f.mode);\n    return 0;\n}'
    if "自动增长" in t:
        return 'if (array->size == array->capacity) {\n    size_t new_capacity = array->capacity ? array->capacity * 2 : 4;\n    int *new_data = realloc(array->data, new_capacity * sizeof *new_data);\n    if (new_data == NULL) return 0;\n    array->data = new_data;\n    array->capacity = new_capacity;\n}'
    if "可变数组的缺陷" in t:
        return '// 中间插入需要搬动后面的元素\nfor (size_t i = array->size; i > index; i--)\n    array->data[i] = array->data[i - 1];\narray->data[index] = value;\narray->size++;'
    if "可变数组" in t:
        return '#include <stdlib.h>\n\ntypedef struct {\n    int *data;\n    size_t size;\n    size_t capacity;\n} IntArray;\n\nvoid destroy(IntArray *a)\n{\n    free(a->data);\n    *a = (IntArray){0};\n}'
    if "链表" in t:
        return '#include <stdio.h>\n#include <stdlib.h>\n\ntypedef struct Node { int value; struct Node *next; } Node;\nint main(void)\n{\n    Node *head = malloc(sizeof *head);\n    if (head == NULL) return 1;\n    *head = (Node){42, NULL};\n    printf("%d\\n", head->value);\n    free(head);\n    return 0;\n}'
    if "for循环" in t:
        return '#include <stdio.h>\n\nint main(void)\n{\n    for (int i = 1; i <= 5; i++)\n        printf("%d ", i);\n    return 0;\n}'
    return '#include <stdio.h>\n\nint main(void)\n{\n    /* 在这里补充本节练习 */\n    puts("继续练习 C 语言");\n    return 0;\n}'


def notes_for(topic: str) -> tuple[str, list[str], str, str]:
    t = topic or "本节内容"
    if any(k in t for k in ("动态内存", "可变数组", "链表")):
        return (f"{t}在运行时管理数据规模。核心不是“申请到内存”，而是明确所有权、容量变化和释放时机。", ["malloc/realloc 返回的地址必须检查。", "扩容时先保存 realloc 的临时返回值，成功后再替换旧指针。", "每次成功申请最终都应对应一次 free。"], "不要丢失原指针，不要重复释放，也不要在 free 后继续访问。", "谁申请，谁负责释放；谁扩容，谁维护容量。")
    if any(k in t for k in ("指针", "地址")):
        return (f"本节核心是用地址间接访问数据。指针变量保存地址，* 用来读取或修改该地址中的值。", ["&value 取得变量地址，赋给类型匹配的指针。", "*p 是解引用；修改 *p 就是在修改原变量。", "指针参与数组访问时，每次加 1 会前进一个元素。"], "指针必须先指向有效对象；不要解引用 NULL、野指针或已经释放的地址。", "指针存地址，解引用取数据。")
    if any(k in t for k in ("数组", "字符串")):
        return (f"{t}把一组同类型数据按顺序保存。访问时要同时盯住容量、有效长度和结尾标记。", ["数组下标从 0 开始，最后一个有效下标是元素个数减 1。", "字符串本质是以 \\0 结束的 char 数组。", "遍历条件应由实际长度或结束符控制。"], "最常见错误是越界；字符串还要给结尾的 \\0 留一个字节。", "容量决定能放多少，长度决定现在用了多少。")
    if any(k in t for k in ("循环", "求和", "阶乘", "素数", "整数翻转", "整数分解", "水仙花", "公约数", "猜数")):
        return (f"{t}的关键是确定循环变量如何开始、何时继续、每轮怎样变化，以及最终怎样退出。", ["循环前准备初始值。", "循环条件只表达“还要不要继续”。", "循环体完成一次工作并推进状态，避免死循环。"], "先用最小值、0、负数和边界值手算几轮，再运行程序。", "循环就是：初始化—判断—执行—更新。")
    if any(k in t for k in ("if", "else", "switch", "swich", "逻辑", "条件")):
        return (f"{t}负责让程序根据真假选择不同路径。C 中 0 为假，非 0 为真。", ["先计算关系表达式，再得到 0 或 1。", "&& 要求两边都真，|| 只需一边真，! 负责取反。", "分支顺序要从更具体的条件写到更宽泛的条件。"], "混用 = 与 ==、忘记括号或依赖复杂优先级都容易出错；复杂条件应主动加括号。", "条件算真假，分支选道路。")
    if any(k in t for k in ("函数", "参数", "本地变量", "全局变量")):
        return (f"{t}用于拆分职责和控制数据作用范围。函数应完成一件清楚的事，并通过参数接收输入、通过返回值或指针给出结果。", ["声明告诉编译器函数长什么样。", "调用时普通参数按值复制，修改副本不会改变原变量。", "需要修改调用者数据时传入地址，并在函数内解引用。"], "避免让函数依赖过多全局状态；变量应放在能够满足需求的最小作用域。", "参数传输入，返回值传结果，指针传可修改对象。")
    if any(k in t for k in ("结构", "枚举", "联合", "定义类型")):
        return (f"{t}把相关数据组织成更清楚的自定义类型，让代码表达业务含义而不是只堆基础类型。", ["enum 为一组命名整数赋予含义。", "struct 的成员各自占空间并同时存在。", "union 的成员共享同一片空间，同一时刻只应把一个成员当作有效值。"], "结构体通过 . 访问，结构体指针通过 -> 访问；联合体必须额外记录当前有效成员。", "类型设计得清楚，后面的代码自然更好读。")
    if any(k in t for k in ("宏", "源代码文件", "声明")):
        return (f"{t}发生在编译前后不同阶段：预处理器负责展开宏和包含头文件，编译器根据声明检查类型。", ["对象宏适合常量，参数宏必须给参数和整体加括号。", "头文件放声明并使用 include guard。", ".c 文件放实现，多个源文件最后由链接器组合。"], "宏只是文本替换，参数可能被求值多次；能用 const 或函数时通常更安全。", "头文件讲接口，源文件写实现。")
    if any(k in t for k in ("文件", "格式化")):
        return (f"{t}的重点是格式与类型匹配，并检查每一步输入输出是否成功。", ["printf 控制显示宽度和精度，scanf 读取时通常需要变量地址。", "fopen 成功后得到 FILE*，失败时返回 NULL。", "使用完成后 fclose，并检查重要操作的返回值。"], "格式符写错会造成未定义行为；文件路径、权限和磁盘错误也必须考虑。", "输入输出都可能失败，返回值就是第一道保险。")
    if any(k in t for k in ("类型", "浮点", "字符", "进制", "位段", "二进制")):
        return (f"{t}决定数据如何编码、占多少空间以及能表示什么范围。选择类型时应先看数据含义，再看范围和精度。", ["sizeof 查看对象或类型占用的字节数。", "整数运算会截断小数，浮点数通常只能近似表示十进制小数。", "不同进制只是同一个整数的不同书写或显示方式。"], "不要假设所有平台上的类型大小完全相同；格式符必须与实际类型对应。", "类型决定解释数据的方式。")
    return (f"本节学习“{t}”。先用一段最小程序验证语法，再观察每个变量在执行过程中的变化。", ["从 main 函数入口开始阅读。", "找出输入、核心处理和输出三部分。", "修改一个值并预测结果，再编译验证。"], "不要只背语法；每次至少运行一个正常值和一个边界值。", "先读懂数据怎么变，再记住语法怎么写。")


TOPIC_FIXES = {
    "swich case": "switch case",
    "级连elseif": "级联 else if",
    "位段（略": "位段",
    "二进制相关（略": "二进制相关",
    "day1之1": "计算与 printf",
}


def clean_topic(topic: str) -> str:
    topic = (topic or "").strip()
    return TOPIC_FIXES.get(topic, topic)


def build_note_title(day: int, index: int, topic: str) -> str:
    return f"第{day:02d}天-{index:02d}：{topic}"


def old_note_index(title: str, fallback: int) -> int:
    match = re.search(r"之(\d+)", title or "")
    return int(match.group(1)) if match else fallback


def build_summary(title: str, topic: str) -> str:
    concept, steps, pitfall, memory = notes_for(topic)
    code = example_for(topic)
    return (
        f"【笔记名称】\n{title}\n\n"
        f"【对应课程】\n翁凯《C语言程序设计》B站网课 · {topic}\n\n"
        f"【核心概念】\n{concept}\n\n"
        f"【示例代码】\n{code}\n\n"
        "【代码拆解】\n" + "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1)) + "\n\n"
        f"【容易踩坑】\n- {pitfall}\n\n"
        f"【一句话记忆】\n{memory}"
    )


def main() -> None:
    app_dir = Path(os.environ.get("APPDATA", Path.home())) / "CNotes"
    database = app_dir / "notes.db"
    backup_dir = app_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_dir / f"notes-before-summary-rewrite-{stamp}.db"
    shutil.copy2(database, backup)

    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        rows = list(connection.execute(
            """
            SELECT id, note_date, title, topics
            FROM notes
            ORDER BY CAST(note_date AS INTEGER), id
            """
        ).fetchall())
        rows.sort(
            key=lambda row: (
                int(row["note_date"]) if str(row["note_date"]).isdigit() else 0,
                old_note_index(row["title"], int(row["id"])),
                int(row["id"]),
            )
        )
        per_day_index: dict[int, int] = {}
        with connection:
            for row in rows:
                day = int(row["note_date"]) if str(row["note_date"]).isdigit() else 0
                per_day_index[day] = per_day_index.get(day, 0) + 1
                topic = clean_topic(row["topics"].strip() or row["title"])
                title = build_note_title(day, per_day_index[day], topic)
                connection.execute(
                    """
                    UPDATE notes
                    SET title = ?, topics = ?, codex_summary = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        title,
                        topic,
                        build_summary(title, topic),
                        dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        row["id"],
                    ),
                )
        count, minimum, maximum = connection.execute(
            "SELECT COUNT(*), MIN(LENGTH(codex_summary)), MAX(LENGTH(codex_summary)) FROM notes"
        ).fetchone()
        print(f"updated={count} min_length={minimum} max_length={maximum}")
        print(f"backup={backup}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
