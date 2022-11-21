# Tools
Small scripts and prototypes for energy measurement


## MSR configurations

### turbo_boost.sh
This script can turn the TurboBoost feature in Intel CPUs on or off.

According to [Brendan Greggs MSR-Tools Repo](https://github.com/brendangregg/msr-cloud-tools/blob/master/showboost) there might be some registers to 
be called when running on different Intel CPUs.

We could not test it on all the possbile, therefore we can only guarantee
functionality for Intel Core i7 with Broadwell architecture.

If our script will not work check out the correct register with Brendan Greggs script.

### RAPL energy filtering

The RAPL accuracy can be be lowered by either having SGX turned on OR by activating
an option in Intel CPUs called "energy filtering".

Source: [https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/advisory-guidance/running-average-power-limit-energy-reporting.html#ipu-2020.2](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/advisory-guidance/running-average-power-limit-energy-reporting.html#ipu-2020.2)

What actually happens is that the energy information returned by RAPL is randomly modified
and will be 0-50% different from the original signal.

This is enough to still have a broad idea of what the total energy budget is but prevents
energy side-channel attacks.

We include a script that can check if the energy filtering switch has been set:

`sudo check_energy_filtering_rapl.sh`

The other possible option when energy filtering kicks in is if **SGX** is activated
in the BIOS. You don't have to have the SGX libraries installed ... just the BIOS
switch suffices.

### cpu_relax

This script will trigger same logic as the `cpu_relax()` function in the linux kernel does.

Originally designed for spin-locks this function can set the processor cycling on 
the lowest power instruction without loosing control of it (C-State, scheduling etc.)

### DVFS

This script will change the cpu frequency govenor in the linux system.

Currently it will just switch to **schedutil** / **performance** or **powersave**.

The possible govenors you can find in:
`/sys/devices/system/cpu/cpuX/cpufreq/scaling_available_governors`

Check if the frequency was really changed by: `watch -d -n 1 "cat /proc/cpuinfo | grep MHz"`

### Read CPU sysbench

In order for this script to work paranoid level should be set to 0:

`sudo sysctl -w kernel.perf_event_paranoid=0`

If you run multiple *perf_events* instances it may happen that the counters get multiplexed.
A warning will be issued in this case.

The script was designed to find out the deviation between time sharding and instruction sharding
when the system background load or is idling.

Currently we see the instruction share strongly deviationg from the time share of 
a process when the system is loaded.

Further research has to be done to conclude if one or the other metric is more helpful
when trying to attribte cumulative metrics like energy to a process.

### nop / pause

The *nop* instruction is the typical "do nothing" instruction in the x86 instruction set.

However Intel introduced also the *pause* instruction which should be used preferrably
when having the CPU in a spin-lock state. 
This instruction will hint the processor that a spin-lock is happening and 
can prevent memory violations and in turn save energy.

In order to create this code you should compile the `empty_loop.c` with: 
`gcc -S empty_loop.c` option. 
This will create an assembler file and you have to inject the `nop`/`pause` 
statements at the correct line.

We have included sample `*.s` files to showcase that. However they might not compile 
directly on your system and should just serve as an example.

Once you have compiled your own `*.s` file create the executable via: `gcc nop.s`

On our test machine the energy difference is the following:
- sudo perf stat -a -e power/energy-pkg/ --timeout 10000 sleep 20
    + 21.80 Joules
- sudo perf stat -a -e power/energy-pkg/ ./nop
    + 87.37 Joules
    + 89.07 Joules
    + 86.97 Joules
- sudo perf stat -a -e power/energy-pkg/ --timeout 10000 ./pause
    + 88.05 Joules
    + 89.79 Joules
    + 88.51 Joules
    
#### Benchmarking an unknown CPU with the nop script

If you want to find out if the CPU speed advertised in the `/proc/cpuinfo` is really
accurate you can just run the `nop` script and time it.

By dividing the runtime through the estimated instructions per cycle (either 3 or 4 on modern CPUs)
you can find out if the CPU has the expected cycle count.

The core should get fully loaded and burst to its maximum frequency as the script
contains no sleeps.