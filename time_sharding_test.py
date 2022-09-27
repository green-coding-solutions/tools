import subprocess
import os
import re
import time

def main(args):

    #print(os.get("_SC_CLK_TCK"))

    time_start = read_proc(args.pid)
#    read_inst(args.pid, args.timeout)
    time.sleep(0.1)
    time_start = read_proc(args.pid)
#    read_inst(args.pid, args.timeout)
    time.sleep(0.1)
    time_start = read_proc(args.pid)
#    read_inst(args.pid, args.timeout)


    # first I want to start a process. stress
    # Then I want to attach to /proc/PID/stat and read the values in a pandas stream
    # Then I also want to go to /proc/stat and get that reading
    # Then I want to attach to perf_stat and get the instruction cycles


def read_proc(pid):
    with open(f"/proc/{pid}/stat") as fp:

        """ /proc/$$/stat format
                  (1) pid  %d
                  (2) comm  %s
                  (3) state  %c
                  (4) ppid  %d
                  (5) pgrp  %d
                  (6) session  %d
                  (7) tty_nr  %d
                  (8) tpgid  %d
                  (9) flags  %u
                  (10) minflt  %lu
                  (11) cminflt  %lu
                  (12) majflt  %lu
                  (13) cmajflt  %lu
                  (14) utime  %lu
                  (15) stime  %lu
        """
        match = re.match("^[^\s]+ \([^\)]+\) [^\s]+ [^\s]+ [^\s]+ [^\s]+ [^\s]+ [^\s]+ [^\s]+ [^\s]+ [^\s]+ [^\s]+ [^\s]+ (\d+) (\d+)", fp.read())
        print("User Time in s: ", int(match[1])*10)
        print("System Time in s",  int(match[2])*10)
    return int(match[1])*10 + int(match[2])*10


def read_inst(pid, timeout):
    ps = subprocess.run(
        ["sudo", "perf", "stat", "-d", "-p", pid, "--timeout", timeout],
        stdout=subprocess.PIPE,
        encoding="UTF-8"
    )
    print(ps.stdout)


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("pid",  help="Skip unsafe volume bindings, ports and complex environment vars")
    parser.add_argument("timeout",  help="Skip unsafe volume bindings, ports and complex environment vars")

    args = parser.parse_args()

    main(args)