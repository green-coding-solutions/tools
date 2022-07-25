import subprocess
import argparse
import re
import time
import pandas as pd
import numpy as np # for statistical tests
import scipy.stats #for statistical tests


def get_conf_interval(x):
    m = x.mean()
    s = x.std()

    dof = len(x)-1
    alpha = .05
    confidence = 1- alpha

    t_crit = np.abs(scipy.stats.t.ppf((1-confidence)/2,dof)) # for two sided!

    return (m-s*t_crit/np.sqrt(len(x)), m+s*t_crit/np.sqrt(len(x)))

def main(n, cmd):

    print("cmd: ", cmd)
    measurements = {"time": [], "energy": []}
    for i in range(0,n):
        print("Run ", i)
        ps = subprocess.run(["sudo", "perf", "stat", "-e", "power/energy-ram/", *cmd.split(" ")], stderr=subprocess.PIPE, encoding='UTF-8')

        match_2 = re.search("(\d*\.\d+) seconds time elapsed", ps.stderr)
        measurements['time'].append(float(match_2[1]))
        match_1 = re.search("(\d*\.\d+) Joules", ps.stderr)
        measurements['energy'].append( float(match_1[1]))

        print("Sleeping 1 s")
        time.sleep(1)

    df = pd.DataFrame(measurements)
    df['time-energy-coefficient'] = df.energy / df.time
    print("\n\n", df.describe())

    print("\n\nConfidence intervals:")
    print("Time", get_conf_interval(df.time))
    print("Energy", get_conf_interval(df.energy))
    print("time-energy-coefficient", get_conf_interval(df['time-energy-coefficient']))

    breakpoint()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", type=int, help="The amount of times to run the command")
    parser.add_argument("cmd", type=str, help="The command to run")
    args = parser.parse_args()

    main(args.runs, args.cmd)
