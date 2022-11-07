#!/bin/bash

# Read /proc/stat file (for first datapoint)
read cpu user nice system idle iowait irq softirq steal guest< /proc/stat

# compute active and total utilizations
cpu_active_prev_sys=$((user+system+nice+softirq+irq+steal))
cpu_total_prev_sys=$((user+system+nice+softirq+irq+steal+idle+iowait))

#sysbench --cpu-max-prime=50000 --threads=1 --time=6 --test=cpu run 2>/dev/null &
#sleep 0.1
#pid=$(pidof sysbench)
#printf "sysbench pid is %d\n" "$pid"

sleep 6 &
pid=$(pidof sleep)
printf " sleep pid is %d\n" "$pid"

sudo perf stat -a -e instructions,cpu-cycles,context-switches,power/energy-pkg/  --timeout 5000
# sudo perf stat -e instructions,cpu-cycles,context-switches  --timeout 5000 --pid $pid

read pid comm state ppid pgrp session tty_nr tpgid flags minflt cminflt majflt cmajflt utime stime cutime cstime priority < "/proc/$pid/stat"

# (14) utime  %lu
# Amount of time that this process has been scheduled
# in user mode, measured in clock ticks (divide by
# sysconf(_SC_CLK_TCK)).  This includes guest time,
# guest_time (time spent running a virtual CPU, see
# below), so that applications that are not aware of
# the guest time field do not lose that time from
# their calculations.#
#
# (15) stime  %lu
# Amount of time that this process has been scheduled
# in kernel mode, measured in clock ticks (divide by
# sysconf(_SC_CLK_TCK)).#
#
# (16) cutime  %ld
# Amount of time that this process's waited-for chil‐
# dren have been scheduled in user mode, measured in
# clock ticks (divide by sysconf(_SC_CLK_TCK)).  (See
# also times(2).)  This includes guest time,
# cguest_time (time spent running a virtual CPU, see
# below).#
#
# (17) cstime  %ld
# Amount of time that this process's waited-for chil‐
# dren have been scheduled in kernel mode, measured in
# clock ticks (divide by sysconf(_SC_CLK_TCK)).


# Read /proc/stat file (for second datapoint)
read cpu user nice system idle iowait irq softirq steal guest< /proc/stat

# compute active and total utilizations
cpu_active_cur_sys=$((user+system+nice+softirq+irq+steal))
cpu_total_cur_sys=$((user+system+nice+softirq+irq+steal+idle+iowait))

# compute CPU utilization (%)
active_jiffies_sys=$((cpu_active_cur_sys-cpu_active_prev_sys))
total_jiffies_sys=$((cpu_total_cur_sys-cpu_total_prev_sys))
cpu_util_sys=$((100*(active_jiffies_sys) / (total_jiffies_sys) ))

printf "\n ------------- PROCESS -------------------\n"
printf " Self -> utime: %d stime: %d\n" "$utime" "$stime"
printd " Children -> cutime: %d cstime: %d\n" "$cutime" "$cstime"
cpu_util_proc_active_jiffies=$((utime+stime+cutime+cstime))
cpu_util_proc_active=$((100*(cpu_util_proc_active_jiffies) / (active_jiffies_sys) ))
cpu_util_proc_total=$((100*(cpu_util_proc_active_jiffies) / (total_jiffies_sys) ))
printf " (Active = Total) Jiffies : %s\n" "$cpu_util_proc_active_jiffies"
printf " CPU Utilization active: %s\n" "$cpu_util_proc_active"
printf " CPU Utilization total: %s\n" "$cpu_util_proc_total"

printf "\n ------------- SYSTEM -------------------\n"
printf " Active Jiffies : %s\n" "$active_jiffies_sys"
printf " Total Jiffies : %s\n" "$total_jiffies_sys"
printf " CPU Utilization : %s\n" "$cpu_util_sys"

exit 0
