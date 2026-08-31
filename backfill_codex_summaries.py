from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path


SUMMARIES: dict[int, tuple[str | None, str]] = {
    56: (
        None,
        """【总结】&是取地址运算符，用来取得一个已存在变量在内存中的地址。例如 int n=10; int *p=&n; 中，&n是n的地址，p保存这个地址。地址输出应使用 printf(\"%p\", (void *)&n)，不要用%d。
【用法】scanf要通过地址修改变量，所以读取整数时写 scanf(\"%d\", &n)。字符数组名在传参时本身就会转换为首元素地址，因此 scanf(\"%19s\", name) 通常不再加&。
【易错点】&后面通常应是可定位的对象，不能对数字常量随意取地址。数组中a和&a[0]的起始地址数值相同，但&a的类型是“指向整个数组”，不能在所有场景中混用。要记住：地址是对象在内存中的位置标记，不是对象当前保存的数值。""".strip(),
    ),
    57: (
        None,
        """【总结】指针是专门保存地址的变量。int *p表示p指向int类型数据；p=&number把number的地址交给p；*p叫解引用，表示访问p指向地址中的整数。如果*p=20，实际修改的就是number。
【用法】常见模式是 int number=10; int *p=&number; printf(\"%d\", *p);。指针使函数能间接修改调用者的变量，也能高效访问数组、字符串和动态内存。输出指针本身使用%p，输出所指整数使用%d和*p。
【易错点】指针必须先指向有效对象再解引用。int *p; 只定义了指针，其中是不确定地址，直接*p=10可能崩溃。暂时没有指向时应初始化为NULL，使用前判断p!=NULL，并保证指针类型与目标数据类型匹配。""".strip(),
    ),
    58: (
        None,
        """【总结】C函数默认是值传递，形参只是实参的副本。要让函数修改外部变量，应把变量地址传入，再通过指针解引用。例如 void swap(int *a,int *b) 通过*a和*b交换调用者的两个整数。
【用法】调用时写 swap(&x,&y)，函数内部写 int t=*a; *a=*b; *b=t;。同一思路还可用于minmax函数，通过int *min和int *max一次带回多个结果。数组传入函数也是传入首元素地址，所以函数能直接修改原数组。
【易错点】形参是int *时，实参应给int变量的地址，不要把普通整数直接传进去。函数如果允许接收NULL，应在解引用前检查。只需读取不修改时，形参可写成const int *p，防止误改外部数据。""".strip(),
    ),
    59: (
        None,
        """【总结】数组名在大多数表达式中会转换为指向首元素的指针，所以int a[5]中a通常等价于&a[0]。根据指针运算，a[i]等价于*(a+i)，&a[i]等价于a+i。这是下标访问和指针遍历能够互换的原因。
【用法】函数参数中的int a[]和int *a效果相同，例如 void print(const int a[],int len)。函数内可用a[i]或*(a+i)访问元素。因为传入的是地址，修改a[i]会影响调用者的原数组；只读函数应加const。
【易错点】数组并不等同于指针变量：数组名不能a++，也不能被重新赋值。在调用者中sizeof(a)能得到整个数组的字节数，但进入函数后a已经是指针，sizeof(a)只得到指针大小，因此必须另外传入长度。""".strip(),
    ),
    60: (
        None,
        """【总结】const放在*左边时，限制的是指针所指数据；放在*右边时，限制的是指针本身。const int *p和int const *p含义相同：p可以改指向，但不能通过*p修改数据。int *const p=&n表示p不能改指向，但*p可修改。
【用法】只读函数形参常写成 void print(const int *a,int len)，表明函数只查看数组，不改内容。如果数据和指向都要固定，写 const int *const p=&n。阅读声明时可以从变量名向左读：先看*p还是p const，再看数据类型。
【易错点】const int *p不表示原变量永远不能改，只表示不能经由p去改。不要通过强制类型转换去掉const后修改本来只读的对象。const指针必须在定义时完成初始化，否则之后无法改变它的指向。""".strip(),
    ),
    61: (
        None,
        """【总结】指针加减是按“元素”移动，不是简单按字节加1。int *p执行p+1会前进sizeof(int)个字节，指向下一个int。两个指针在同一数组中相减，结果是它们相隔的元素数，可用ptrdiff_t接收并用%td输出。
【用法】遍历数组可写 for(int *p=a;p<a+len;p++) printf(\"%d\",*p);。a+len是数组末尾后一个位置，可以用于比较和判断结束，但不能解引用。*p++等价于*(p++)，表示先使用当前元素，再让指针后移。
【易错点】只有在同一数组或同一段连续空间中，指针的大小比较和相减才有明确意义。不能解引用NULL、越界指针或未初始化指针。(*p)++是数据加1，p++是地址后移，括号不同会完全改变含义。""".strip(),
    ),
    64: (
        None,
        """【总结】动态内存分配用于运行时才知道数据数量的场景。malloc在堆上申请指定字节数的连续空间，成功返回首地址，失败返回NULL。推荐写 int *a=malloc((size_t)n*sizeof *a);，并包含<stdlib.h>。申请到的空间可用a[i]访问。
【用法】标准流程是：先检查n是否合法，再调用malloc，然后判断a!=NULL，使用结束后free(a); a=NULL;。如果需要移动指针遍历，应保留malloc返回的原始首地址，最后只向free传这个首地址。
【易错点】malloc的参数是字节数，不是元素个数；申请n个int必须乘sizeof(int)。常见问题有忘记free导致内存泄漏、free后继续使用、同一地址重复free、未检查NULL以及改变首地址后错误释放。纯C语言中malloc返回的void *通常不必强制转换。""".strip(),
    ),
    65: (
        None,
        """【总结】C语言没有独立的string基本类型，字符串是一段以'\\0'结尾的char数组。char s[]=\"Hello\";实际包含'H','e','l','l','o','\\0'六个字节。'\\0'是数值为0的终止字符，而'0'是可见的数字字符，两者不同。
【用法】可用下标逐字符处理：for(int i=0;s[i]!='\\0';i++)，也可用指针遍历：for(char *p=s;*p;p++)。printf(\"%s\",s)会从首地址开始输出，直到遇到'\\0'。sizeof(s)统计整个数组字节数，strlen(s)只统计终止字符之前的长度。
【易错点】char s[]={'A','B','C'}只是字符数组，没有'\\0'就不是合法C字符串，用%s或strlen处理会越界读取。缓冲区容量必须为结尾'\\0'预留一个位置。对UTF-8中文来说，一个汉字可能占多个字节，strlen得到的不一定是肉眼看到的字符个数。""".strip(),
    ),
    66: (
        None,
        """【总结】双引号中的\"Hello\"是字符串字面量，程序会在内存中保存这串字符及结尾'\\0'。字面量不应被修改，所以推荐写 const char *p=\"Hello\";。如果需要修改内容，应写 char s[]=\"Hello\";，这会把内容复制到可修改的数组。
【用法】固定提示语、菜单名或星期名等只读文字适合用const char *。需要接收输入或修改字符时使用char buffer[20]=\"\";。指针p可以重新指向另一个字符串，但数组名s不能被赋值为另一个地址。
【易错点】不要对const char *p=\"Hello\"执行p[0]='Y'，修改字面量属于未定义行为。sizeof(p)得到指针本身大小，不是字符串长度；sizeof(s)才是数组大小。char *只表示字符指针，只有它指向以'\\0'结尾的有效序列时，才能当字符串处理。""".strip(),
    ),
    68: (
        None,
        """【总结】字符串数组用来保存多个字符串，常见有两种形式。char names[][10]={\"Tom\",\"Alice\"};是二维字符数组，每行固定10字节且内容可修改。const char *names[]={\"Tom\",\"Alice\"};是指针数组，每个元素保存一个字符串地址。
【用法】需要固定容量并修改各个字符时，使用二维数组；保存长短不同的只读文字时，使用const char *数组更节省空间。访问整个字符串用names[i]，访问某个字符用names[i][j]。计算条目数可用sizeof names/sizeof names[0]。
【易错点】二维字符数组的第二维必须给出，并且行容量要包含结尾'\\0'。指针数组如果指向字面量，只能更换某个指针的指向，不应修改字面量内容。把二维数组传给函数时，同样需要让编译器知道每行的宽度。""".strip(),
    ),
    67: (
        None,
        """【总结】printf和scanf使用%s处理以'\\0'结尾的字符串。printf(\"%s\",s)从首地址输出到'\\0'。scanf(\"%s\",s)读取一个单词，遇到空格、Tab或换行就停止。数组名会转换为首地址，所以%s输入时通常不写&s。
【用法】char name[20];应配合 scanf(\"%19s\",name)，19限制最多读取19个字节，留一格给'\\0'。需要读取含空格的整行时，使用 fgets(line,sizeof line,stdin)。fgets可能保留换行符，必要时可用 line[strcspn(line,\"\\n\")]='\\0'; 去掉。
【易错点】不限制%s输入宽度容易造成数组越界。未初始化的char buffer[100]不保证存在'\\0'，不能直接用%s输出；可先写char buffer[100]=\"\";。char buffer[]=\"\";只创建1字节数组，不能用来存放后续长输入。同时要检查scanf或fgets的返回值。""".strip(),
    ),
    72: (
        None,
        """【总结】命令行程序可以通过main的参数接收外部信息：int main(int argc,char *argv[])。argc是参数总数，argv是字符串指针数组，每个argv[i]指向一个以'\\0'结尾的参数。通常argv[0]是程序名，用户给出的第一个参数从argv[1]开始。
【用法】例如运行 tool.exe input.txt 3，通常argc为3，argv[1]是\"input.txt\"，argv[2]是\"3\"。使用前先判断argc，例如if(argc<3)就输出用法并return 1。命令行数字本质上仍是字符串，需通过strtol等函数转换后才能进行数值运算。
【易错点】不要在未检查argc时直接访问argv[1]或argv[2]，否则可能越界。不能把argv[i]当成整数直接计算，atoi无法明确报告错误，更稳妥的方式是strtol并检查结束指针。参数中如果包含空格，通常需要在命令行中使用引号把它包成一个参数。""".strip(),
    ),
    73: (
        None,
        """【总结】strlen用来计算C字符串的长度，声明在<string.h>中，原型为 size_t strlen(const char *s)。它从s指向的位置开始向后查找，返回第一个'\\0'之前的字节数，结尾'\\0'不计入长度。返回类型size_t是无符号整数类型，printf应使用%zu。
【用法】char s[]=\"Hello\";时，strlen(s)为5，而sizeof(s)为6。strlen适合判断字符串是否为空、计算复制所需空间，或作为循环边界。动态复制字符串时常申请strlen(src)+1字节，多出的1用于保存'\\0'。
【易错点】strlen要求s指向有效且以'\\0'结尾的字符串，对NULL、未初始化数组或没有终止符的字符序列调用会越界。strlen每次都要扫描到'\\0'，不要在大循环条件中重复计算不变的长度。UTF-8中strlen统计字节，不是汉字个数。""".strip(),
    ),
    74: (
        "字符串函数strcmp",
        """【总结】strcmp用于按字典顺序比较两个C字符串，声明在<string.h>中，原型为 int strcmp(const char *s1,const char *s2)。它从左到右比较对应字节，直到出现不同字符或遇到'\\0'。相等返回0，s1较小返回负数，s1较大返回正数。
【用法】判断相等应写 if(strcmp(a,b)==0)，排序时可根据返回值正负决定顺序。例如strcmp(\"apple\",\"banana\")<0。只想比较前n个字节时可用strncmp(a,b,n)。比较区分大小写，因此\"ABC\"和\"abc\"不相等。
【易错点】不能用a==b判断两个字符串内容是否相同，因为指针使用==比较的是地址。也不要假设strcmp只会返回-1、0或1；标准只保证负数、0和正数三种符号。两个参数都必须是有效、以'\\0'结尾的字符串，不能传NULL。""".strip(),
    ),
    75: (
        "字符串函数strcpy与strcat",
        """【总结】strcpy和strcat都声明在<string.h>中。strcpy(dst,src)把src的全部内容连同结尾'\\0'复制到dst，并返回dst。strcat(dst,src)先找到dst末尾的'\\0'，再把src连同'\\0'接到后面。两者都要求目标缓冲区可写且空间足够。
【用法】char dst[20]; strcpy(dst,\"Hello\"); 可得到\"Hello\"。若再执行strcat(dst,\" C\")，得到\"Hello C\"。动态复制时，申请大小应是strlen(src)+1；拼接所需容量至少是strlen(dst)+strlen(src)+1。如果只复制限定数量字节，可了解strncpy，但截断时仍要自己确保结尾'\\0'。
【易错点】strcpy和strcat本身不知道dst的容量，空间不足会写越界，因此不能把它们用在大小不明的缓冲区上。dst不能指向字符串字面量，源和目标空间也不应重叠。不能用赋值语句dst=src来复制字符数组，那只是处理地址，不会复制字符内容。""".strip(),
    ),
}


def main() -> None:
    database = Path(os.environ["APPDATA"]) / "CNotes" / "notes.db"
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = database.with_name(f"{database.name}.bak-{stamp}")
    shutil.copy2(database, backup)

    lengths = {note_id: len(text) for note_id, (_topic, text) in SUMMARIES.items()}
    invalid = {note_id: length for note_id, length in lengths.items() if not 300 <= length <= 500}
    if invalid:
        raise ValueError(f"不在300—500字范围内: {invalid}")

    connection = sqlite3.connect(database)
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(notes)")}
        if "codex_summary" not in columns:
            connection.execute("ALTER TABLE notes ADD COLUMN codex_summary TEXT NOT NULL DEFAULT ''")

        with connection:
            for note_id, (topic, text) in SUMMARIES.items():
                row = connection.execute(
                    "SELECT id, note_date, title FROM notes WHERE id = ?", (note_id,)
                ).fetchone()
                if row is None or int(row[1]) < 8:
                    raise RuntimeError(f"目标课程不存在或天数不匹配: {note_id}")
                if topic is None:
                    connection.execute(
                        "UPDATE notes SET codex_summary = ?, updated_at = datetime('now','localtime') WHERE id = ?",
                        (text, note_id),
                    )
                else:
                    connection.execute(
                        "UPDATE notes SET topics = ?, codex_summary = ?, updated_at = datetime('now','localtime') WHERE id = ?",
                        (topic, text, note_id),
                    )
    finally:
        connection.close()

    print(f"backup={backup}")
    for note_id, length in sorted(lengths.items()):
        print(f"id={note_id} length={length}")


if __name__ == "__main__":
    main()
