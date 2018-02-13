/* compile using
  gcc sol1_1c.c -o sol1_1c
*/

#include <stdio.h>

void main()
{
    int x = 1;
    printf("0x%p\n", &x);
    x = x + 1;
    printf("0x%p\n", &x);
}

