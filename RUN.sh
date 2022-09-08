#!/bin/bash

#main
scripts_path="/data/local/tmp"
adb root
adb wait-for-device

adb push busybox $scripts_path
adb shell chmod 755 $scripts_path/busybox
adb push monitor.sh $scripts_path
adb shell <command
