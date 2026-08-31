from __future__ import annotations

import datetime as dt
import os
import shutil
import sqlite3
from pathlib import Path


SUMMARY = """本集主题：抽象数据类型的表示与实现。

ADT 的形式定义只说明数据对象、数据关系和基本操作；要让计算机真正运行，还必须选择具体语言表示存储结构，并实现每个操作。

实现路线：
1. 用 C 已有类型定义新的数据类型；
2. 用函数实现 ADT 的基本操作；
3. 用函数声明和头文件组织接口；
4. 在 main 中调用这些操作完成问题。
"""

CODE = r'''#include <stdio.h>

typedef struct {
    double real;
    double imag;
} Complex;

Complex complex_make(double real, double imag);
Complex complex_add(Complex a, Complex b);
int complex_divide(Complex a, Complex b, Complex *result);

Complex complex_make(double real, double imag)
{
    return (Complex){real, imag};
}

Complex complex_add(Complex a, Complex b)
{
    return complex_make(a.real + b.real, a.imag + b.imag);
}

int complex_divide(Complex a, Complex b, Complex *result)
{
    double denominator = b.real * b.real + b.imag * b.imag;
    if (denominator == 0.0) return 0;
    result->real = (a.real * b.real + a.imag * b.imag) / denominator;
    result->imag = (a.imag * b.real - a.real * b.imag) / denominator;
    return 1;
}

int main(void)
{
    Complex a = complex_make(8.0, 6.0);
    Complex b = complex_make(4.0, 3.0);
    Complex sum = complex_add(a, b);
    Complex quotient;
    printf("sum=%.1f%+.1fi\n", sum.real, sum.imag);
    if (complex_divide(a, b, &quotient))
        printf("quotient=%.2f%+.2fi\n", quotient.real, quotient.imag);
    return 0;
}
'''

CODEX = """【本集定位】
本集《1.3 抽象数据类型的表示与实现》解决一个关键问题：上一集定义出的 ADT 只是形式模型，怎样才能变成计算机中真正可运行的程序？

答案是：选择具体语言和存储方式来表示数据对象，再用函数把基本操作实现出来。

【一、从现实问题到可运行程序】
数据结构课程的主线可以串起来：

现实信息 → 逻辑结构 → 存储结构 → 数据运算 → 算法与程序

逻辑结构描述对象之间的关系，与具体机器无关；存储结构把这种关系映射到内存；算法和程序则真正对存储的数据执行操作。

ADT 处在“逻辑模型”和“具体程序”之间：它先规定对象、关系和操作，再交给 C 语言完成表示与实现。

【二、ADT 的表示】
表示就是回答“数据对象在程序里怎么保存”。

例如复数可以抽象为一对有顺序的实数：

复数 = （实部，虚部）

在 C 中可以用结构体表示：
- real 保存实部；
- imag 保存虚部。

这里的结构体是实现手段，不是 ADT 本身。ADT 关心复数具有实部、虚部以及复数运算；结构体只是把这些内容放进内存的一种选择。

【三、ADT 的实现】
ADT 的每个基本操作通常用一个函数实现：

- 构造操作：接收数据项，返回一个合法的新对象；
- 查询操作：接收对象，返回某个计算结果；
- 修改操作：接收对象或对象指针，改变对象状态；
- 组合操作：接收多个对象，返回新的对象。

上一集的“圆”可以实现成 create、area、perimeter 函数；本集使用复数演示 make、add 和 divide 函数。

【四、为什么要先声明函数】
C 语言按源文件顺序编译。如果 main 或其他函数在调用一个函数时，编译器还没有见过它的返回类型、名字和参数列表，就可能产生隐式声明或类型不匹配问题。

因此通常先写函数原型：

返回类型 函数名(参数类型 参数名);

声明只告诉编译器接口长什么样，函数体才是具体实现。实际项目中，声明通常放在头文件，函数实现放在 .c 文件，调用者只包含头文件即可。

【五、复数加法的实现】
设 a = ar + ai·i，b = br + bi·i，则：

a + b = (ar + br) + (ai + bi)·i

代码中分别读取 a.real、b.real 相加，再分别读取 a.imag、b.imag 相加，最后把两个结果放入一个新的 Complex 对象返回。

普通结构体变量使用点运算符：a.real、a.imag。

【六、结构体指针与 ->】
如果函数需要把结果写回调用者提供的对象，可以传入结构体指针：

Complex *result

此时 result 是地址，访问成员要使用 ->：

result->real
result->imag

两种写法等价：

(*result).real
result->real

要点是：
- 普通结构体对象使用 .；
- 指向结构体的指针使用 ->。

【七、复数除法为什么要检查零】
复数除法的分母是：

b.real² + b.imag²

当 b 的实部和虚部都为 0 时，分母为 0，除法没有定义。因此函数先计算 denominator，再判断是否为 0。

代码返回 0 表示失败，返回 1 表示成功；成功时通过 result 指针把商写回调用者。这是“返回状态 + 输出参数”的常见 C 语言接口设计。

【八、类 C 语言与真正 C 语言】
教材中的算法描述常使用类 C 语言。它故意省略一些与算法思想无关的语法细节，所以更简洁、更接近伪代码。

类 C 语言不能直接复制到编译器运行。真正实现时必须补充：
- 头文件；
- 类型声明；
- 函数返回类型和参数类型；
- 分号、花括号和完整表达式；
- 内存和错误处理细节。

因此读算法时关注思想，写程序时再补齐语言细节。

【九、代码阅读顺序】
阅读本集示例时，建议按这个顺序：
1. 先看 typedef struct，确定对象的内部表示；
2. 再看函数声明，确认每个操作的输入和输出；
3. 看函数实现，检查它是否遵守 ADT 定义；
4. 最后看 main，观察多个操作如何组合成程序。

【易错点】
- 结构体变量用 .，结构体指针用 ->，不要混用。
- 函数声明中的返回类型和参数类型必须与定义一致。
- 用指针返回结果时，要确保指针指向有效对象。
- 复数除法必须检查分母是否为 0。
- ADT 的接口和 C 的内部结构不是同一层概念，修改实现不应破坏接口行为。

【复习检查】
1. ADT 为什么还需要“表示”和“实现”？
2. 结构体在复数实现中扮演什么角色？
3. 函数声明解决了什么问题？
4. . 和 -> 的使用场景分别是什么？
5. 为什么复数除法需要返回成功/失败状态？

【一句话记忆】
ADT 先定接口和规则，C 语言再用结构体表示数据、用函数实现操作。
"""


def main() -> None:
    app_dir = Path(os.environ.get("APPDATA", Path.home())) / "CNotes"
    database = app_dir / "notes.db"
    backup_dir = app_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = backup_dir / f"notes-before-data1-note4-{stamp}.db"
    shutil.copy2(database, backup)
    data1 = "数据1"
    title = "数据1之4"
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    con = sqlite3.connect(database)
    try:
        with con:
            cur = con.execute(
                """UPDATE notes SET topics=?, summary=?, codex_summary=?, code=?, updated_at=?
                   WHERE note_date=? AND title=?""",
                ("1.3 抽象数据类型的表示与实现", SUMMARY, CODEX, CODE, now, data1, title),
            )
        if cur.rowcount != 1:
            raise RuntimeError(f"Expected one note, updated {cur.rowcount}")
        print("updated=1", "backup=" + str(backup))
    finally:
        con.close()


if __name__ == "__main__":
    main()
