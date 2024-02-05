#!/usr/bin/env bash

cd ~/python/peloton
source ~/python/peloton/.venv/bin/activate

while getopts 'hcm' OPTION; do
  case "$OPTION" in
    h)
      python ~/python/peloton/main.py -h
      exit 1
      ;;
    c)
      python ~/python/peloton/main.py -c
      exit 1
      ;;
    m)
      python ~/python/peloton/main.py -m
      exit 1
      ;;
    ?)
      echo "script usage: $(basename \$0) [-l] [-h] [-a somevalue]" >&2
      exit 1
      ;;
  esac
done
shift "$(($OPTIND -1))"

python ~/python/peloton/main.py
