
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <asm/unistd.h>
#include <sys/syscall.h>
#include <sys/time.h>

// these two should be identical on Intel machines.
// However only the latter one may work on other CPUs
#define cpu_relax() asm volatile("pause" : : : "memory")
//#define cpu_relax() asm volatile("rep; nop") 

int main(int argc, char *argv[])
{

  
   while(1)
    {
        cpu_relax();
    }
}