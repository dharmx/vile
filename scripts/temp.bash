#!/usr/bin/env bash
nouveau="$(sensors nouveau-pci-0100 | rg -o '[0-9.°C]+' | sed -n 4p)"
cannonlake="$(sensors pch_cannonlake-virtual-0 | rg -o '[0-9.°C]+ | tail -n1')"
echo "$cannonlake $nouveau"
