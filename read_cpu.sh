#!/bin/bash


# Function to extract CPU utilization from /proc/stat file
get_cpu_utilization() {
    read cpu user nice system idle iowait irq softirq steal guest < /proc/stat

    # compute active and total utilizations
    cpu_active_1=$((user+system+nice+softirq+irq+steal))
    cpu_total_1=$((user+system+nice+softirq+irq+steal+idle+iowait))

    sleep 0.01

    read cpu user nice system idle iowait irq softirq steal guest < /proc/stat

    # compute active and total utilizations
    cpu_active_2=$((user+system+nice+softirq+irq+steal))
    cpu_total_2=$((user+system+nice+softirq+irq+steal+idle+iowait))

    cpu_ratio=$(awk "BEGIN { print ($cpu_active_2-$cpu_active_1)*100 / ($cpu_total_2-$cpu_total_1) }")
    echo "CPU utilization: $cpu_ratio %"

}


while true; do
  get_cpu_utilization
done