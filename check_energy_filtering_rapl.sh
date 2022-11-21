#!/bin/bash

echo "Resulting value must be 1. If it is 0 then energy filtering is off."
echo "Remember to also check if SGX is enabled."
sudo rdmsr -d 0xbc
