from __future__ import annotations

import datetime as dt
import os
import shutil
import sqlite3
from pathlib import Path


LESSONS = [
    (
        "1.4 算法与算法分析 1",
        "算法的概念与特性",
        r'''#include <stdio.h>

int max_of_two(int a, int b)
{
    return a > b ? a : b;
}

int main(void)
{
    printf("%d\n", max_of_two(7, 12));
    return 0;
}''',
        "算法是解决特定问题的有限步骤序列。一个合格算法应有输入、输出、确定性、有限性和可行性：每一步都明确，最终一定结束，而且能用有限操作执行。程序是算法的具体实现，同一个算法可以用不同语言表达。阅读代码时先找输入、状态变化和输出，再判断循环是否必然结束。\n\n数据结构解决“数据如何组织”，算法解决“如何处理这些数据”；二者共同决定程序效率。",
        ["先明确问题和输入输出，再写步骤。", "把复杂问题拆成可验证的小步骤。", "用小规模样例手算，检查每一步状态。"],
        "不要把一段能运行的代码直接等同于好算法；还要检查是否正确、是否会终止、是否能处理边界。",
        "算法 = 有限、确定、可执行的解决步骤。",
    ),
    (
        "1.4 算法与算法分析 2",
        "算法正确性与复杂度",
        r'''#include <stdio.h>

int linear_search(const int a[], int n, int target)
{
    for (int i = 0; i < n; i++)
        if (a[i] == target) return i;
    return -1;
}

int main(void)
{
    int a[] = {4, 8, 15, 16, 23, 42};
    printf("index=%d\n", linear_search(a, 6, 23));
    return 0;
}''',
        "算法分析先看正确性，再看效率。线性查找从头到尾逐个比较，最好情况一次找到，最坏情况要比较 n 次，因此时间复杂度为 O(n)，额外空间为 O(1)。\n\n复杂度描述输入规模变大时资源如何增长，不等同于某台电脑上的实际秒数。分析时关注基本操作的执行次数，并保留增长最快的项。",
        ["确定输入规模 n。", "数核心比较、赋值或循环次数。", "分别考虑最好、平均和最坏情况。"],
        "不要只用一个小样例判断效率；小数据下 O(n) 和 O(n²) 可能看不出差别。",
        "复杂度看增长趋势，不看一次运行的偶然时间。",
    ),
    (
        "1.4 算法与算法分析 3",
        "时间复杂度与空间复杂度",
        r'''#include <stdio.h>

void print_pairs(const int a[], int n)
{
    for (int i = 0; i < n; i++)
        for (int j = i + 1; j < n; j++)
            printf("(%d,%d) ", a[i], a[j]);
}

int main(void)
{
    int a[] = {1, 2, 3, 4};
    print_pairs(a, 4);
    return 0;
}''',
        "双重循环通常意味着乘法级增长。上面的代码输出所有不同元素对，执行次数约为 n(n-1)/2，因此是 O(n²)。如果函数只使用固定数量的临时变量，空间复杂度仍是 O(1)。\n\n时间和空间是两种资源：用额外数组换取更快查找，可能降低时间复杂度但增加空间复杂度。分析算法时要把循环、递归、临时容器和输入规模一起考虑。",
        ["单层遍历常见 O(n)，嵌套两层常见 O(n²)。", "常数倍和低阶项在大 O 表示中通常省略。", "额外数组、递归调用栈也属于空间开销。"],
        "不能看到两个 for 就机械判定 O(n²)，还要看内层循环实际迭代范围是否依赖 n。",
        "时间看操作次数，空间看额外占用。",
    ),
    (
        "1.4 算法与算法分析 4",
        "算法设计与性能比较",
        r'''#include <stdio.h>

int binary_search(const int a[], int n, int target)
{
    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (a[mid] == target) return mid;
        if (a[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}

int main(void)
{
    int a[] = {2, 4, 8, 16, 32, 64};
    printf("index=%d\n", binary_search(a, 6, 32));
    return 0;
}''',
        "算法设计常常是在正确性、时间和空间之间做权衡。二分查找每次把有序区间缩小一半，时间复杂度为 O(log n)，但前提是数据已经按升序排列，并且能够通过下标快速访问。\n\n优化不是盲目追求更复杂的算法，而是先确认瓶颈和前提条件。先写出清晰的基线版本，再比较复杂度、可维护性和实际数据规模。",
        ["维护 left、right 两个边界。", "每轮计算中点并排除一半区间。", "循环结束时确认目标确实不存在。"],
        "二分查找最常见的错误是忘记有序前提、边界更新不正确或中点计算导致溢出。",
        "更快的算法往往需要更强的前提。",
    ),
    (
        "2.1 线性表的定义和特点",
        "线性表",
        r'''#include <stdio.h>

#define CAPACITY 8
typedef struct {
    int data[CAPACITY];
    int length;
} SeqList;

int insert(SeqList *list, int index, int value)
{
    if (index < 0 || index > list->length || list->length == CAPACITY)
        return 0;
    for (int i = list->length; i > index; i--)
        list->data[i] = list->data[i - 1];
    list->data[index] = value;
    list->length++;
    return 1;
}

int main(void)
{
    SeqList list = {{10, 20, 30}, 3};
    insert(&list, 1, 15);
    for (int i = 0; i < list.length; i++) printf("%d ", list.data[i]);
    return 0;
}''',
        "线性表是 n 个数据元素的有限序列，元素之间是一对一的前后关系。除第一个元素没有直接前驱、最后一个没有直接后继外，中间元素各有一个前驱和一个后继。\n\n线性表的逻辑定义与具体存储无关；代码中的 SeqList 是顺序表实现。插入时必须从后向前搬移，避免覆盖尚未搬走的数据；删除则通常从前向后覆盖空位。",
        ["length 表示当前元素个数，不是数组容量。", "插入位置允许在 0 到 length 之间。", "顺序表随机访问 O(1)，中间插入/删除通常 O(n)。"],
        "越界、把 length 和 capacity 混用、搬移方向错误，都会造成数据丢失或未定义行为。",
        "线性表描述顺序，数组只是它的一种实现。",
    ),
]


def build_codex(topic: str, concept: str, explanation: str, steps: list[str], pitfall: str, memory: str) -> str:
    return (f"【本集定位】\n{topic}：{concept}。本集把上一阶段的概念落到可执行的 C 语言思考上。\n\n"
            f"【核心讲解】\n{explanation}\n\n【代码拆解】\n" + "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)) +
            f"\n\n【易错点】\n- {pitfall}\n\n【复习检查】\n1. 本集对象的输入和输出是什么？\n2. 关键循环或边界如何保证正确？\n3. 如果数据规模扩大，时间和空间如何变化？\n\n【一句话记忆】\n{memory}")


def main() -> None:
    app_dir = Path(os.environ.get("APPDATA", Path.home())) / "CNotes"
    database = app_dir / "notes.db"
    backup_dir = app_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_dir / f"notes-before-data2-{stamp}.db"
    shutil.copy2(database, backup)
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_date = "数据2"
    marker = chr(0x4e4b)
    con = sqlite3.connect(database)
    try:
        with con:
            for i, (topic, concept, code, explanation, steps, pitfall, memory) in enumerate(LESSONS, 1):
                title = f"{data_date}{marker}{i}"
                codex = build_codex(topic, concept, explanation, steps, pitfall, memory)
                existing = con.execute("SELECT id FROM notes WHERE note_date=? AND title=?", (data_date, title)).fetchone()
                if existing:
                    con.execute("UPDATE notes SET topics=?, summary=?, codex_summary=?, code=?, updated_at=? WHERE id=?", (topic, explanation, codex, code, now, existing[0]))
                else:
                    con.execute("INSERT INTO notes (note_date,title,topics,summary,codex_summary,code,reflection,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)", (data_date,title,topic,explanation,codex,code,"",now,now))
        print(f"updated={len(LESSONS)} backup={backup}")
    finally:
        con.close()


if __name__ == "__main__":
    main()
