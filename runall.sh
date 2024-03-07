#!/usr/bin/env bash
set -euo pipefail

declare -a scripts=(
	# abbrgen
	training
	qmk-chorded
	zmk-chorded
	kanata-chorded
	espanso-text-expansion
)
for script in "${scripts[@]}"; do
	echo "Running ${script}.py"
	python ${script}.py
done

cp abbr.yml ~/.config/espanso/match
cp abbr.def ../qmk_firmware/keyboards/mushi/keymaps/dlip
cp combos.dtsi ../zmk-sweep/config
cp macros.dtsi ../zmk-sweep/config
