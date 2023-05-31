#!/bin/bash

directories=$(find /Users/elias6970/Desktop/22/archivo/Arhivo\ digital/ -mindepth 1 -type f)

#echo "Number of directories: $directories"

for i in $directories; do
  #f=$(basename "$i")
  #echo $f
  echo "$i" >> out.txt
  #"\n" > out.txt
done
exit

# Iterate over the directories in the directory
for dir in /Users/elias6970/Desktop/22/archivo/Arhivo\ digital/*; do
    if ! [ -d "$dir" ]; then
        # Get the directory name without the path
        dir_name=$(basename "$dir")
        
        # Process each directory here
        echo "Processing directory: $dir_name"
    fi
done
