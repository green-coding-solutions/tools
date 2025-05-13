#!/bin/bash

# CPU to read from (typically CPU 0 is enough)
CPU=0

# RAPL MSR addresses
MSR_POWER_UNIT=0x606
MSR_PKG_ENERGY=0x611
MSR_PP0_ENERGY=0x639
MSR_PP1_ENERGY=0x641
MSR_DRAM_ENERGY=0x619
MSR_PSYS_ENERGY=0x642

# Load msr kernel module
if ! lsmod | grep -q msr; then
    sudo modprobe msr || { echo "Failed to load msr module"; exit 1; }
fi

# Read energy unit
RAW_HEX=$(sudo rdmsr -p $CPU $MSR_POWER_UNIT)
RAW_DEC=$(( 0x$RAW_HEX ))
ESU=$(( (RAW_DEC >> 8) & 0x1F ))
ENERGY_UNIT=$(awk "BEGIN { printf \"%.8f\", 2^(-$ESU) }")

echo "Energy Unit (2^(-$ESU)): $ENERGY_UNIT Joules"
echo "----------------------------"

# Function to read and decode MSR
read_energy() {
    local name=$1
    local addr=$2
    if sudo rdmsr -p $CPU $addr &>/dev/null; then
        local raw=$(sudo rdmsr -p $CPU $addr)
        local dec=$(( 0x$raw ))
        local joules=$(awk -v val=$dec -v unit=$ENERGY_UNIT 'BEGIN { printf "%.6f", val * unit }')
        printf "%-10s: %s (%.6f J)\n" "$name" "0x$raw" "$joules"
    else
        echo "$name      : Not supported"
    fi
}

# Dump all supported RAPL domains
read_energy "Package" $MSR_PKG_ENERGY
read_energy "PP0 (Cores)" $MSR_PP0_ENERGY
read_energy "PP1 (GPU/Uncore)" $MSR_PP1_ENERGY
read_energy "DRAM" $MSR_DRAM_ENERGY
read_energy "PSys" $MSR_PSYS_ENERGY