#!/bin/bash

cd "$(dirname "$0")/ikemen-go-stable"

chmod +x ./Ikemen_GO_MacOS
./Ikemen_GO_MacOS -AppleMagnifiedMode YES -s stages/stage0-720.def -log debug.log

echo "Game launched. Check ikemen-go-stable/debug.log for any issues."
echo "Press Ctrl+C to exit the game."
