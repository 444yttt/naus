#!/bin/bash
# Resume native Z pipeline for one shot; stop on any failure/Traceback.
set -u
cd /work/hj/handoff_dataset
B=/opt/blender/blender-4.5.9-linux-x64/blender
s=$1
step(){ name=$1; shift; log=out_Z3/${s}_native_${name}.log; echo "$(date -u +%FT%TZ) START $s $name" >> /work/progress_Z3.log
  "$@" > $log 2>&1; rc=$?
  if [ $rc -ne 0 ] || grep -q Traceback $log; then echo "$(date -u +%FT%TZ) FAIL $s $name rc=$rc" >> /work/progress_Z3.log; exit 1; fi
  echo "$(date -u +%FT%TZ) OK $s $name" >> /work/progress_Z3.log; }
step foreground $B -b --python-exit-code 1 --python render_Z3.py -- $s
step background $B -b --python-exit-code 1 --python render_Z3.py -- $s --background
step reflection $B -b --python-exit-code 1 --python photo_floor_reflection_Z3.py -- $s
step contact $B -b --python-exit-code 1 --python photo_contact_Z3.py -- $s
step transform python3 transform_reflection_Z3.py $s full
step composite python3 photo_composite_Z3.py $s full
echo "$(date -u +%FT%TZ) DONE $s" >> /work/progress_Z3.log
