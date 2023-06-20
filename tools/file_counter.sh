#!/bin/bash

#Check if the outputfile exists
if [ -f "./paths_all_files.txt" ]; then
  rm "./paths_all_files.txt"
fi

file_list=()

# Find all files inside the directory and its subdirectories
while IFS= read -r -d '' file; do
  file_list+=("$file")
done < <(find "$1" -type f -print0)

extensions=()
values=()
found=false 

for file in "${file_list[@]}"; do
  actual_extension="${file##*.}"

  echo $file >> "./paths_all_files.txt"
  #Uncoment this 3 lines to create a list of pdf
  #if [[ "$actual_extension" == "pdf" ]]; then
   # echo $file >> firstOut.txt
  #fi

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

total=0

#Print the file types and how much are
for i in "${!values[@]}"; do
  ((total+=${values[$i]]}))
  echo "${extensions[$i]}" : "${values[$i]}"
done

echo total:$total


: '
rar=0
zip=0
pdf=0
m=0
# Print the file list
for file in "${file_list[@]}"; do
  if [[ $file == *".rar"* ]]; then
    #echo "$file" >> out.txt
    ((rar++))
  elif [[ $file == *".zip"* ]]; then
    ((zip++))
  elif [[ $file ==  *".pdf"* || $file == *".PDF"* ]]; then
    ((pdf++))
    echo $file >> secondOut.txt
  fi
  #echo $(basename "$file") >> out.txt
  ((m++))
done

echo Pdf: $pdf, Rar: $rar, Zip: $zip, total: $m
'
if [[ "$actual_extension" == "PDF" ]]; then 
    new_path="${file//PDF/}pdf"
    mv "$file" "$new_path"
  fi
if [[ $file =~ ".." ]]; then
    echo $file
  fi

