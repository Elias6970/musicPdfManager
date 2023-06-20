#!/bin/bash

#Check if the outputfile exists
if [ -f "./path_uncompressed_files.txt" ]; then
  rm "./path_uncompressed_files.txt"
fi

file_list=()

# Find all files inside the directory and its subdirectories
while IFS= read -r -d '' file; do
  file_list+=("$file")
done < <(find "$1" -type f -print0)

extensions=()
values=()
found=false 
ocultos=0

for file in "${file_list[@]}"; do
  actual_extension="${file##*.}"

  if [[ $file =~ ".zip" ]]; then
    echo "${file}"
  fi

  #Uncoment this 3 lines to create a list of pdf
  #if [[ "$actual_extension" == "rar" ]]; then
  #  echo $file >> firstOut.txt
  #elif [[ "$actual_extension" == "zip" ]]; then
  #  echo $file >> firstOut.txt
  if [[ "$actual_extension" == "PDF" ]]; then 
    new_path="${file//PDF/}pdf"
    mv "$file" "$new_path"
  fi
  #Compare if the file already exists in the type known
  for i in "${!extensions[@]}"; do
    if [[ "$actual_extension" == "${extensions[$i]}" ]]; then

      ((values[$i]++))
      found=true 
    fi
  done
  
  if [[ "$found" == true ]]; then
    found=false
    continue
  else
    #Append a new file type to the array and create its value in 0
    extensions+=($actual_extension)
    values+=($((1)))
  fi

done
echo ocultos: $ocultos
