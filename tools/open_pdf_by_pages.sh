#!/bin/bash 

for i in {1..16}
do
  mupdf-gl $1 $i > /dev/null 2>&1 &

  pid=$!   

  osascript -e 'tell application "System Events" to set frontmost of process "iTerm2" to true'
  
  read hola
  kill $pid 

 done


