from __future__ import annotations

import datetime as dt
import os
import shutil
import sqlite3
from pathlib import Path


SUMMARY = """本集主题：数据类型、抽象数据类型（ADT）及其形式化定义。

数据类型 = 一组性质相同的值 + 这组值上允许的一组操作。

抽象数据类型 = 从具体问题抽象出的数据模型 + 数据关系 + 基本操作；它描述“能表示什么、能做什么”，不描述“内部如何存储”。

ADT 的形式通常写成三元组：
ADT 名称 {
    数据对象；
    数据关系；
    基本操作；
} ADT 名称
"""

CODE = r'''#include <stdio.h>

typedef struct {
    double radius;
    double x;
    double y;
} Circle;

Circle circle_create(double radius, double x, double y)
{
    return (Circle){radius, x, y};
}

double circle_area(Circle c)
{
    const double pi = 3.141592653589793;
    return pi * c.radius * c.radius;
}

double circle_perimeter(Circle c)
{
    const double pi = 3.141592653589793;
    return 2.0 * pi * c.radius;
}

int main(void)
{
    Circle c = circle_create(2.0, 0.0, 0.0);
    printf("area=%.2f perimeter=%.2f\n",
           circle_area(c), circle_perimeter(c));
    return 0;
}
'''

CODEX = """【本集定位】
本集《1.2 基本概念和术语 2》把上一集的“逻辑结构—存储结构—数据运算”继续抽象成两个重要概念：数据类型和抽象数据类型（ADT）。重点不是背英文缩写，而是学会把一个具体问题描述成“数据对象 + 关系 + 操作”。

【一、数据类型到底规定了什么】
在高级程序设计语言中，变量、常量、表达式、函数参数和返回值都必须有类型。类型至少隐含规定两件事：

1. 取值范围：这个对象允许保存哪些值；
2. 可进行的操作：这些值允许参与哪些运算。

例如 int 不只是告诉编译器“这里放整数”，还告诉编译器应该按整数的存储方式解释它，并允许进行加、减、乘、整除和求模等整数操作。char 表示字符集合，float/double 表示近似实数，数组、结构体、联合体和指针则是在基础类型上组合出来的更复杂类型。

因此，数据类型不是一个孤立的名字，而是“值的集合”和“值上的操作”的共同约定。

【二、为什么需要抽象数据类型】
C 语言自带的 int、char、double、数组和结构体足以表示很多基础数据，但复杂的数据结构往往不能直接由一个基础类型表达。例如栈、队列、线性表等，除了保存数据，还要明确入栈、出栈、插入、删除等操作。

这时需要先从具体问题中抽取共同本质，忽略颜色、大小、内部布局等暂时无关的细节。这个思维过程就是抽象。

抽象的结果不是某一段 C 代码，而是一个独立于具体实现的数学模型和操作规范。英文叫 Abstract Data Type，缩写为 ADT。

【三、数据类型与抽象数据类型的区别】
数据类型更接近语言和编译器：它通常涉及存储大小、取值范围、表达式规则和底层实现。

抽象数据类型更接近问题建模：它只关心对象的意义、对象之间的关系，以及外部允许调用的操作；它不要求现在就决定使用数组、链表还是其他存储方式。

可以这样记：
- 数据类型回答“这个值是什么类型，能做哪些运算”；
- ADT 回答“这个抽象对象是什么，外部能对它做什么”。

【四、ADT 的三个组成部分】
一个抽象数据类型至少包含：

1. 数据对象
说明这个抽象类型的对象由哪些数据构成。

2. 数据关系
说明对象内部各部分之间必须满足什么逻辑关系。

3. 基本操作
说明允许对数据对象做哪些操作，以及操作的输入、前提和结果。

形式化地说，可以把 ADT 看成三元组：

ADT = （数据对象，数据关系，基本操作）

它是一份接口和规则说明，而不是内部实现。

【五、基本操作的描述格式】
每个操作要交代四件事：

- 操作名：调用这个操作时使用什么名字；
- 参数表：需要哪些输入；
- 初始条件：操作开始前，数据和参数必须满足什么条件；
- 操作结果：操作成功后返回什么，或数据结构发生什么变化。

初始条件为空时可以省略。若条件不满足，应返回错误信息或规定的失败结果。

参数还可以分为普通输入参数和引用型参数。引用型参数通过地址让操作把结果带回调用者，这对应 C 语言中常见的指针参数。

【六、例子：把圆抽象成 ADT】
圆的本质属性可以用半径 r 和圆心坐标（x，y）表示。圆的颜色、画在纸上还是屏幕上、线条粗细，都不是这个抽象模型的必要部分。

圆的基本操作可以设计为：

- Create(r, x, y)：根据半径和圆心创建一个圆，结果是新圆对象；
- Area(c)：前提是圆 c 已存在，结果是 πr²；
- Perimeter(c)：前提是圆 c 已存在，结果是 2πr；
- Scale(c, n)：根据缩放比例生成缩放后的圆。

这里的重点是操作契约：调用者只需要知道“传入什么、得到什么”，不需要先知道圆对象在内存中是结构体、数组还是其他表示。

【七、例子：复数 ADT】
复数可以抽象成一对有顺序的实数（实部，虚部）。实部和虚部的顺序不能交换，因为（a，b）与（b，a）通常表示不同的复数。

复数的操作可以包括：
- 创建复数；
- 复数加法；
- 复数减法；
- 复数乘法；
- 复数除法；
- 取实部和虚部。

ADT 先规定这些对象和操作的数学含义，至于最终用两个 double、一个结构体，还是其他方式实现，可以留到后续设计阶段。

【八、代码如何体现“抽象”和“实现分离”】
代码区用 Circle 结构体保存半径和圆心，用 circle_create、circle_area、circle_perimeter 表示外部操作。

从 ADT 角度看：
- Circle 是数据对象的一个具体实现；
- radius、x、y 体现数据关系和约束；
- 三个函数是对外提供的基本操作；
- main 只调用操作，不重复计算面积公式。

如果以后把 Circle 改成指针、动态内存或隐藏结构体，只要操作名和行为保持一致，调用者的使用方式就可以基本不变。这正是抽象数据类型带来的好处。

【九、易错点】
- ADT 不是某种固定的 C 语法，而是一种建模和接口描述方法。
- 数据类型要考虑取值范围和允许操作，ADT 还要考虑对象关系和操作契约。
- 形式定义不能只写数据对象，还必须写关系和基本操作。
- 先写清楚操作的初始条件，再写代码，能减少非法输入和未定义行为。
- “能实现”不等于“抽象得好”：好的 ADT 应隐藏不必要的存储细节。

【复习检查】
1. 数据类型由哪两部分共同构成？
2. ADT 为什么可以不考虑内部存储？
3. ADT 三元组分别是什么？
4. 一个基本操作需要描述哪些内容？
5. 如何把圆或复数写成“数据对象 + 关系 + 操作”？

【一句话记忆】
数据类型规定值和运算，ADT 规定对象、关系和操作；先定义“能做什么”，再决定“内部怎么做”。
"""


def main() -> None:
    app_dir = Path(os.environ.get("APPDATA", Path.home())) / "CNotes"
    database = app_dir / "notes.db"
    backup_dir = app_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_dir / f"notes-before-data1-note3-{stamp}.db"
    shutil.copy2(database, backup)
    data1 = "数据1"
    title = "数据1之3"
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = sqlite3.connect(database)
    try:
        with con:
            cur = con.execute(
                """UPDATE notes SET topics=?, summary=?, codex_summary=?, code=?, updated_at=?
                   WHERE note_date=? AND title=?""",
                ("1.2 数据类型与抽象数据类型", SUMMARY, CODEX, CODE, now, data1, title),
            )
        if cur.rowcount != 1:
            raise RuntimeError(f"Expected one note, updated {cur.rowcount}")
        print("updated=1", "backup=" + str(backup))
    finally:
        con.close()


if __name__ == "__main__":
    main()
