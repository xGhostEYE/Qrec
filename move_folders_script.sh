#!/bin/bash

source_dir="/u2/users/mel196/cmpt470_after_semester/Qrec/train/allennlp_training"
target_dir="/u2/users/mel196/cmpt470_after_semester/Qrec/test/allennlp_testing"

cd $source_dir

my_array=($(ls))

for folder in ${my_array[@]:0:243}
do
mv "${source_dir}/${folder}" "${target_dir}/${folder}"
done
