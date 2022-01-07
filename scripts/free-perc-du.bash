#!/usr/bin/env bash

used() {
	df --output=pcent "$1" | grep -Eo '[0-9]+'
}

result="$(used "$1")"
echo "$((100 - result))"
