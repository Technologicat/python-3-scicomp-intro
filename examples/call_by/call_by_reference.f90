subroutine f(r)
    integer, intent(inout) :: r
    r = 42
end subroutine

program call_by_reference
    implicit none
    integer :: a
    a = 23
    call f(a)
    print *,a
end program

