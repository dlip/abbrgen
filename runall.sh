#!/usr/bin/env bash
set -euo pipefail

declare -a scripts=(
  # abbrgen
  # training
  # qmk-chorded
  # zmk-chorded
  # kanata-chorded
  # espanso-text-expansion
  qmk-autocorrect
)
for script in "${scripts[@]}"; do
  echo "Running ${script}.py"
  python ${script}.py
done

# cp abbr.def ../qmk_firmware/keyboards/tenshi/keymaps/engram

QMK_HOME=~/code/qmk_firmware qmk generate-autocorrect-data qmk-autocorrect.txt -o ../qmk_firmware/users/dlip/autocorrect_data.h
# cp abbr.yml ../nixconfig/home/espanso/config/match/abbr.yml
# cp abbr.def ../qmk_firmware/keyboards/mushi/keymaps/engram
# cp abbr.def ../qmk_firmware/keyboards/tamatama/keymaps/engram
# cp abbr.def ../qmk_firmware/keyboards/tenshi/keymaps/engram
# cp combos.dtsi ../zmk-sweep/config
# cp macros.dtsi ../zmk-sweep/config
