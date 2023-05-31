#!/bin/bash
# Declare an array of numbers
numbers=(10)

# Append a number to the array
numbers+=($((10)))

# Print the updated array
echo "${numbers[@]}"

