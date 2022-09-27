
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>
#include <linux/perf_event.h>
#include <asm/unistd.h>
#include <sys/syscall.h>
#include <sys/time.h>

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


static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
           int cpu, int group_fd, unsigned long flags)
{
    int ret;

    ret = syscall(__NR_perf_event_open, hw_event, pid, cpu,
                  group_fd, flags);
    return ret;
}

void read_instructions(pid_t pid)
{
    struct perf_event_attr pe;
    long long count_pid;
    long long count_system;
    int fd;

    memset(&pe, 0, sizeof(pe));
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof(pe);
    pe.config = PERF_COUNT_HW_CPU_CYCLES;
    pe.disabled = 1; // because we start it later with ioctl, so we have enough time for setup
    pe.exclude_kernel = 0;
    pe.exclude_hv = 0;

    fd = perf_event_open(&pe,
        /* pid */ pid,
        /* cpu*/-1,
        /* group_fd*/ -1,
        /* flags*/ 0);

    if (fd == -1) {
      fprintf(stderr, "Error opening leader %llx\n", pe.config);
      exit(EXIT_FAILURE);
    }

    long int proc_time = read_cpu_proc();
    long int proc_time_pid = read_cpu_proc_pid(pid);
    ioctl(fd, PERF_EVENT_IOC_RESET, 0);
    ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);

    //fib(12);
    //fib(42);
    //longer_func();
    usleep(1000 * 1000);
    ioctl(fd, PERF_EVENT_IOC_DISABLE, 0); // end before read, cause read is async
    long int proc_time_after = read_cpu_proc();
    long int proc_time_pid_after = read_cpu_proc_pid(pid);

    read(fd, &count_pid, sizeof(count_pid));

    printf("Used %lld cycles\n", count_pid);
    printf("Time in /proc/stat was %ld ms\n", proc_time_after - proc_time);
    printf("Time in /proc/pid/stat was %ld ms\n", proc_time_pid_after - proc_time_pid);
    printf("Time ratio is %f %\n", (double) (proc_time_pid_after - proc_time_pid) / (double) (proc_time_after - proc_time));
    printf("Cycle ratio is %f %\n", (double) count_pid / (double) count_system);

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