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

### cpu_relax

This script will trigger same logic as the `cpu_relax()` function in the linux kernel does.

Originally designed for spin-locks this function can set the processor cycling on 
the lowest power instruction without loosing control of it (C-State, scheduling etc.)