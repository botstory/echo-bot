#!/usr/bin/env bash
echo "Compiling..."

rm -rf out/* out/**/* || exit 0
mkdir -p out
cp -r static/* out

echo "Compiling README.rst..."
rst2html5 --bootstrap-css --pretty-print-code --jquery --embed-content README.rst > out/readme.html
