
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <asm/unistd.h>
#include <sys/syscall.h>
#include <sys/time.h>

#define PID_ANY -1 
#define CPU_ANY 0 
#define CPU_0 0

static long int user_hz;

int longer_func() {
    double a = 52;
    double b = 74;
    double c =4;
    int i =0;
    while(i<10000000){
        c=a*b;
        c+=c;
        i++;
    }
    //printf("%f", c);
    return c;
}

int fib(int n) {
    if (n <= 1)
        return n;
    else
        return fib(n-1) + fib(n-2);
}

static long int read_cpu_proc() {
    FILE* fd = NULL;
    long int user_time, nice_time, system_time, idle_time, iowait_time, irq_time, softirq_time, steal_time, guest_time;

    fd = fopen("/proc/stat", "r");

    fscanf(fd, "cpu %ld %ld %ld %ld %ld %ld %ld %ld %ld", &user_time, &nice_time, &system_time, &idle_time, &iowait_time, &irq_time, &softirq_time, &steal_time, &guest_time);

    // printf("Read: cpu %ld %ld %ld %ld %ld %ld %ld %ld %ld\n", user_time, nice_time, system_time, idle_time, iowait_time, irq_time, softirq_time, steal_time, guest_time);
    if(idle_time <= 0) fprintf(stderr, "Idle time strange value %ld \n", idle_time);

    fclose(fd);

    // after this multiplication we are on microseconds
    // integer division is deliberately, cause we don't loose precision as *1000000 is done before
    return ((user_time+nice_time+system_time+idle_time+iowait_time+irq_time+softirq_time+steal_time+guest_time)*1000)/user_hz;
}


static long int read_cpu_proc_pid(pid_t pid) {
    FILE* fd = NULL;
    long int user_time, system_time;

    char filename[BUFSIZ];
    sprintf(filename, "/proc/%d/stat", pid);
    printf("Filename: %s\n", filename);

    fd = fopen(filename, "r");

    fscanf(fd, "%*s %*s %*s %*s %*s %*s %*s %*s %*s %*s %*s %*s %*s %lu %lu", &user_time, &system_time);
  //            21810 (stress)    R    21809  21809  13106  34832  21809  4194368 15     0     0      0      210214 1
    printf("Read: user_time: %ld and system_time: %ld\n", user_time, system_time);

    fclose(fd);


    // after this multiplication we are on microseconds
    // integer division is deliberately, cause we don't loose precision as *1000000 is done before
    return ((user_time+system_time)*1000)/user_hz;
}


static int perf_event_open(int event_type, pid_t pid, int cpu)
{
    int fd;
    struct perf_event_attr hw_event;

    int group_fd = -1;
    unsigned long flags = 0;

    memset(&hw_event, 0, sizeof(hw_event));
    hw_event.type = PERF_TYPE_HARDWARE;
    hw_event.size = sizeof(hw_event);
    hw_event.config = event_type;
    hw_event.disabled = 1; // because we start it later with ioctl, so we have enough time for setup
    hw_event.exclude_kernel = 0;
    hw_event.exclude_hv = 0;
    
    fd = syscall(__NR_perf_event_open, &hw_event, pid, cpu, group_fd, flags);
    

    if (fd == -1) {
      fprintf(stderr, "Error opening process %d %llx\n", pid, hw_event.config);
      exit(EXIT_FAILURE);
    }
           
    return fd;
}

void read_instructions(pid_t pid)
{
    long long cycles_pid;
    long long cycles_system;
    long long instructions_pid;
    long long instructions_system;
    
    int fd;
    
    int fd_cycles_pid = perf_event_open(PERF_COUNT_HW_CPU_CYCLES, pid, CPU_ANY);
    int fd_instructions_pid = perf_event_open(PERF_COUNT_HW_INSTRUCTIONS, pid, CPU_ANY);
    int fd_cycles_system = perf_event_open(PERF_COUNT_HW_CPU_CYCLES, PID_ANY, CPU_0);
    int fd_instructions_system = perf_event_open(PERF_COUNT_HW_INSTRUCTIONS, PID_ANY, CPU_0);

    long int proc_time = read_cpu_proc();
    long int proc_time_pid = read_cpu_proc_pid(pid);
    ioctl(fd_cycles_pid, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd_cycles_pid, PERF_EVENT_IOC_ENABLE, 0);
    ioctl(fd_instructions_pid, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd_instructions_pid, PERF_EVENT_IOC_ENABLE, 0);
    ioctl(fd_cycles_system, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd_cycles_system, PERF_EVENT_IOC_ENABLE, 0);
    ioctl(fd_instructions_system, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd_instructions_system, PERF_EVENT_IOC_ENABLE, 0);

    //fib(12);
    //fib(42);
    //longer_func();
    usleep(1000 * 1000);



    ioctl(fd_cycles_pid, PERF_EVENT_IOC_DISABLE, 0);
    ioctl(fd_instructions_pid, PERF_EVENT_IOC_DISABLE, 0);
    ioctl(fd_cycles_system, PERF_EVENT_IOC_DISABLE, 0);
    ioctl(fd_instructions_system, PERF_EVENT_IOC_DISABLE, 0);
    
    long int proc_time_after = read_cpu_proc();
    long int proc_time_pid_after = read_cpu_proc_pid(pid);

    read(fd_cycles_pid, &cycles_pid, sizeof(cycles_pid));
    read(fd_cycles_system, &cycles_system, sizeof(cycles_system));
    read(fd_instructions_pid, &instructions_pid, sizeof(instructions_pid));
    read(fd_instructions_system, &instructions_system, sizeof(instructions_system));

    printf("Used %lld cycles pid\n", cycles_pid);
    printf("Used %lld cycles system\n", cycles_system);
    printf("Used %lld instructions pid\n", instructions_pid);
    printf("Used %lld instructions system\n", instructions_system);
    
    printf("Time in /proc/stat was %ld ms\n", proc_time_after - proc_time);
    printf("Time in /proc/pid/stat was %ld ms\n", proc_time_pid_after - proc_time_pid);
    printf("Time ratio is %f \n", (double) (proc_time_pid_after - proc_time_pid) / (double) (proc_time_after - proc_time));
    printf("Cycle ratio is %f \n", (double) cycles_pid / (double) cycles_system);
    printf("Instruction ratio is %f \n", (double) instructions_pid / (double) instructions_system);

    close(fd);
}

int main(int argc, char *argv[])
{

    int c;
    user_hz = sysconf(_SC_CLK_TCK); // set global

    setvbuf(stdout, NULL, _IONBF, 0);
    pid_t pid = 0;
    while ((c = getopt (argc, argv, "p:")) != -1) {
        switch (c) {
        case 'p':
            pid = atoi(optarg);
            break;
        default:
            fprintf(stderr,"Unknown option %c\n",c);
            exit(-1);
        }
    }

    // run with: gcc instructions_count.c && sudo ./a.out -p 21810
    // validation call: sudo perf stat -p 21810 --timeout 1000


   for(int i=0;i<1;i++)
    {
        read_instructions(pid);
    }
}