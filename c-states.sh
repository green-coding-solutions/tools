if [[ ! -z $1 && $1 != "enable" && $1 != "disable" ]]; then
    echo "Invalid argument: $1" >&2
    echo ""
    echo "Usage: $(basename $0) [disable|enable]"
    exit 1
fi


for file in /sys/devices/system/cpu/cpu*/cpuidle/state*/disable; do
    if [[ $1 == "enable" ]]; then
        echo "0" | sudo tee "$file"
        echo "Value 0 written to $file"
    else
        echo "1" | sudo tee "$file"
        echo "Value 1 written to $file"
    fi
done