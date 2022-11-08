#!/usr/bin/env python3
import os
import sys
import psutil
import subprocess
import time
import re
import math

def read_proc_stat():
    # Read /proc/stat file (for first datapoint)
    # psutil already gives us the value in time, not jiffies.
    reading = psutil.cpu_times()

    if reading.steal > 0 or reading.guest > 0 or reading.guest_nice > 0:
        print("Warning: Process had positive time readings for steal / guest! This is not expected")
        os.exit()


    # compute active and total utilizations
    reading_active=reading.user+reading.system+reading.nice+reading.softirq+reading.irq+reading.steal
    reading_total=reading.user+reading.system+reading.nice+reading.softirq+reading.irq+reading.steal+reading.idle+reading.iowait

    return reading_active, reading_total

def read_proc_pid_stat(pid):
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

    ps = psutil.Process(pid)
    reading = ps.cpu_times()

    if reading.children_user > 0 or reading.children_system > 0:
        print("Warning: Process had positive time readings for children! This is not expected")
        os.exit()

    # compute active and total utilizations
    reading_active=reading.user+reading.system+reading.children_user+reading.children_system
    reading_total=reading.user+reading.system+reading.children_user+reading.children_system+reading.iowait

    return reading_active, reading_total


def main(duration, threads, metric, debug, unsafe):

    print(f"Starting with {duration=} {threads=} {metric=} {debug=}")

    cpu_active_prev, cpu_total_prev = read_proc_stat()

    # Sysbench parameters are mostly taken from https://www.brendangregg.com/blog/2014-01-10/benchmarking-the-cloud.html
    # the cpu-max-prime may not get too low as the thread does only interrupt if an event is fired. If no event is fired
    # at the "duration" time limit then the process will take longer, which is what we want to avoid!

    ps_sysbench = subprocess.Popen(
        ["sysbench", "--cpu-max-prime=25000", f"--threads={threads}", f"--time={duration+1}", "--test=cpu", "--events=0", "--rate=0", "--debug=on", "run"],
        preexec_fn=os.setsid,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="UTF-8"
    )

    # TODO: Check if time from the benchmark in real time is accurate! it may only be 1% above duration

    print(f"PID is {ps_sysbench.pid}")

    ps_perf_pid = subprocess.Popen(
        ["perf", "stat", "-a", "-e", f"{metric}:uk", "--timeout", f"{duration}000", "--pid", f"{ps_sysbench.pid}"],
        preexec_fn=os.setsid,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="UTF-8"
    )

    ps_perf_system = subprocess.Popen(
        ["perf", "stat", "-a", "-e", f"{metric}:uk,power/energy-pkg/", "--timeout", f"{duration}000"],
        preexec_fn=os.setsid,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        encoding="UTF-8"
    )

    time.sleep(duration+1)

    cpu_active_after, cpu_total_after = read_proc_stat()
    pid_active, pid_total = read_proc_pid_stat(ps_sysbench.pid)

    print(f"Now parsing outputs:")

    output = ps_sysbench.stdout.read()
    if(debug): print(output)
    events = float(re.search(r"total number of events:\s*(\d+)", output)[1].replace(",",""))
    total_time = float(re.search(r"total time:\s*([\d.,]+)s", output)[1].replace(",",""))
    execution_time_avg = float(re.search(r"execution time \(avg/stddev\):\s*([\d.,]+)/[\d.,]+", output)[1].replace(",",""))

    output = ps_perf_pid.stderr.read()
    if(debug): print(output)
    metric_pid = float(re.search(rf"([\d,]+)\s*{metric}:uk", output)[1].replace(",",""))

    if(re.search(r"%", output)):
        print('\033[91m') # start red color
        print("\n----------------------------------------ERROR !!!!!!!!!!!!!!!!!! ----------------------------------------------------------")
        print("perf_events were multiplexed!")
        print("This happens when more counters are used than are physically available. Please reduce the amounts of PMUs used")
        print('\033[0m') # end red color
        sys.exit(-1)


    output = ps_perf_system.stderr.read()
    if(debug): print(output)
    metric_system = float(re.search(rf"([\d,]+)\s*{metric}:uk", output)[1].replace(",",""))
    energy_system = float(re.search(r"([\d.,]+)\s*Joules power/energy-pkg/", output)[1].replace(",",""))

    if(re.search(r"%", output)):
        print('\033[91m') # start red color
        print("\n----------------------------------------ERROR !!!!!!!!!!!!!!!!!! ----------------------------------------------------------")
        print("perf_events were multiplexed!")
        print("This happens when more counters are used than are physically available. Please reduce the amounts of PMUs used")
        print('\033[0m') # end red color
        sys.exit(-1)

    if(not unsafe and not math.isclose(total_time, duration+1, abs_tol=0.005)): # deviation up than 5 ms allowed
        print('\033[91m') # start red color
        print("\n----------------------------------------ERROR !!!!!!!!!!!!!!!!!! ----------------------------------------------------------")
        print(f"{total_time=} was more than 5 ms larger than maximum allowed duration of {duration+1=}")
        print("This might indicate a too high / too low thread number or a too high cpu-max-prime for your system (modify source code for the latter)")
        print("Please adjust the threads, duration and background load, so that the benchmark gets enough processing time and overhead is reduced.")
        print("The reason for this guard clause is to maximize reproducibility and generality of the test")
        print('\033[0m') # end red color
        sys.exit(-1)
    elif(not unsafe and not math.isclose(execution_time_avg, duration+1, abs_tol=0.01)): # deviation up than 10 ms allowed
        print('\033[91m') # start red color
        print("\n----------------------------------------ERROR !!!!!!!!!!!!!!!!!! ----------------------------------------------------------")
        print(f"{execution_time_avg=} was more than 10 ms larger than maximum allowed duration of {duration+1=}")
        print("This might indicate a too high thread number for your system, because the threads are getting not enough compute time.")
        print("Also this might indicate a compile problem on your system. We see this strong deviation for instance on macOS and believe it is a bug.")
        print("Please adjust the threads, duration and background load, so that the benchmark gets enough processing time and overhead is reduced.")
        print("The reason for this guard clause is to maximize reproducibility and generality of the test")
        print('\033[0m') # end red color
        sys.exit(-1)
    else: # show results
        cpu_active = cpu_active_after-cpu_active_prev
        cpu_total = cpu_total_after-cpu_total_prev

        energy_diff = (energy_system*metric_pid/metric_system) - (energy_system*(pid_active)/(cpu_active))
        energy_diff_rel = energy_diff / energy_system

        print(f"""
------------ PROCESS ------------------
Total wall time: {total_time}s
Active time: {pid_active} (Time the process was NOT waiting)
Total time: {pid_total} (CPU + waiting time)
Total events: {events}
{metric}_pid={metric_pid:.6E}
CPU % active share: {100*(pid_active)/(cpu_active):.4}
-> (Share of time the process was calculating on the CPU vs. time the whole system was calculating on the CPU)
CPU % total share: {100*(pid_total)/(cpu_total):.4}
-> (Share of CPU+waiting time of the process vs. total time of the system)

--------- SYSTEM --------------------
Active time: {cpu_active}
Total time: {cpu_total}
CPU %: {100*(cpu_active)/(cpu_total):.4}
{metric}_system={metric_system:.6E}
{energy_system=} J

----------- DIFFERENT SPLITTING -------------------
CPU % active share: {100*(pid_active)/(cpu_active):.4} (explanation see top)
CPU % total share: {100*(pid_total)/(cpu_total):.4} (explanation see top)
{metric} Share: {100*metric_pid/metric_system:.4}

Energy difference: {energy_diff:.4} J ({100*energy_diff_rel:.4} %)
        """)

    if unsafe:
        print('\033[91m') # start red color
        print("\nWarning: Code has been run with --unsafe flag and calculations might have high std.dev.")
        print('\033[0m') # end red color

if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()

    parser.add_argument("--metric", type=str, default="instructions", choices=["instructions", "cycles", "context-switches"], help="Choose metric")
    parser.add_argument("--duration", type=int, default=1, help="Time for the test in seconds")
    parser.add_argument("--threads", type=int, default=1, help="Amount of threads")
    parser.add_argument("--debug", action="store_true", help="Show debug output")
    parser.add_argument("--unsafe", action="store_true", help="Do not run error checks")
    args = parser.parse_args()

    main(args.duration, args.threads, args.metric, args.debug, args.unsafe)
