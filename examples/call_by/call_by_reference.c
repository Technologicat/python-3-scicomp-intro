/* compile with
   gcc call_by_reference.c -o call_by_reference
*/
#include <stdio.h>
void f(int *r)
{
    *r = 42;  /* modifies the caller's variable */
}
int main()
{
    int a = 23;
    f(&a);
    printf("%d\n", a);  /* 42 */
    return 0;
}

