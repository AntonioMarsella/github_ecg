#!/bin/bash
for filename in ./edfs/*.edf; do
	echo $filename
	file=${filename##*/}
	base=${file%.*}
	echo $base
	edf2mit -i "$filename" -r $base
done


