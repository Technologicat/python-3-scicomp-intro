/* compile with
   gcc call_by_value.c -o call_by_value
*/

#include <stdio.h>

void f(int r)
{
    r = 42;  /* modifies the local copy only */
}

int main()
{
    int a = 23;
    f(a);
    printf("%d\n", a);  /* still 23 */
    return 0;
}

