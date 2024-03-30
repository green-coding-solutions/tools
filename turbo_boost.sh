#!/bin/bash

# Credit to Maythux: https://askubuntu.com/questions/619875/disabling-intel-turbo-boost-in-ubuntu

if [[ -z $(which rdmsr) ]]; then
    echo "msr-tools is not installed. Run 'sudo apt-get install msr-tools' to install it." >&2
    exit 1
fi

if [[ ! -z $1 && $1 != "enable" && $1 != "disable" ]]; then
    echo "Invalid argument: $1" >&2
    echo ""
    echo "Usage: $(basename $0) [disable|enable]"
    exit 1
fi

cores=$(cat /proc/cpuinfo | grep processor | awk '{print $3}')


for core in $cores; do
    if [[ $1 == "disable" ]]; then
        sudo wrmsr -p${core} 0x1a0 0x4000850089
    fi
    if [[ $1 == "enable" ]]; then
        sudo wrmsr -p${core} 0x1a0 0x850089
    fi
    state=$(sudo rdmsr -p${core} 0x1a0 -f 38:38)
    echo "core ${core}:"
    if [[ $state -eq 1 ]]; then
        echo -e "\t TurboBoost (MSR): \t\t\t disabled"
    else
        echo -e "\t TurboBoost (MSR): \t\t\t enabled"
    fi
    echo -e "\t scaling_governor: \t\t\t" $(cat "/sys/devices/system/cpu/cpu${core}/cpufreq/scaling_governor")
    echo -e "\t scaling_driver: \t\t\t" $(cat "/sys/devices/system/cpu/cpu${core}/cpufreq/scaling_driver")
    echo -e "\t energy_performance_preference: \t" $(cat "/sys/devices/system/cpu/cpu${core}/cpufreq//energy_performance_preference")

done

echo "CPU-wide settings"
echo -e "\t P_State status (off,active,passive): \t" $(cat "/sys/devices/system/cpu/intel_pstate/status")
echo -e "\t P_State no_turbo (0=allowed,1=off): \t" $(cat "/sys/devices/system/cpu/intel_pstate/no_turbo")
echo -e "\t P_State max-turbo (%): \t\t" $(cat "/sys/devices/system/cpu/intel_pstate/max_perf_pct")


echo -e "\nAvailable drivers for CPU DVFS: "
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors

echo -e "\nPlease be aware that the scaling_governors will change depending on which scaling_driver is active"
echo "You can force changing the driver from the intel_pstate (default) to intel_cpufreq (legacy) by setting "
echo "See further https://wiki.archlinux.org/title/CPU_frequency_scaling and https://www.kernel.org/doc/html/v5.17/admin-guide/pm/intel_pstate.html#user-space-interface-in-sysfs"
echo "$ echo passive | sudo tee /sys/devices/system/cpu/intel_pstate/status"

echo -e "\nThis is however only recommeded for testing, as this is not a real-world production setting"

echo -e"\n\nTry stressing your system and look where turbo boost is going: "
echo 'watch -n 0.5 "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"'
echo "taskset 0x01 stress-ng -c 1"