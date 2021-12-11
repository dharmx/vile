#!/usr/bin/env bash

line_count () {
    echo -n $(wc -l < "$1")
}

random_line () {
    echo -n $(shuf -i1-$(line_count $1) -n1)
}

random_path () {
    echo $(sed -n $(random_line "$1")p "$1")
}

echo -n $(random_path "$1")

