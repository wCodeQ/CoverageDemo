#include<stdio.h>

void fun1();
void fun2();

int main(int argc,char* argv[])
{
    if(argc>1)
        fun1();
    else
        fun2();
    return 0;
}

void fun1()
{
    printf("AAAA\n");
}

void fun2()
{
    printf("BBB\n");
}
