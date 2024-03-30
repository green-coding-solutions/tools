# Setting this govenor has different behaviours depending of which scaling_driver is active
# intel_pstate knows only perfomance and powersave and will behave differently as when for instance
# acpi_cpufreq is active, which knows also schedutil
# See https://wiki.archlinux.org/title/CPU_frequency_scaling
# See further: https://www.kernel.org/doc/html/v5.17/admin-guide/pm/intel_pstate.html#user-space-interface-in-sysfs

echo schedutil | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu1/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu2/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu3/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu4/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu5/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu6/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu7/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu8/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu9/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu10/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu11/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu12/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu13/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu14/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu15/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu16/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu17/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu18/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu19/cpufreq/scaling_governor
echo schedutil | sudo tee /sys/devices/system/cpu/cpu20/cpufreq/scaling_governor
