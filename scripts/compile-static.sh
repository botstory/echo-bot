#!/usr/bin/env bash
echo "Compiling..."

rm -rf out/* out/**/* || exit 0
mkdir -p out
cp -r static/* out
