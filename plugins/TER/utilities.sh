#!/bin/bash

measure_overlaps () {
# count how many examples have 0 TER
	count=0
	TER=($(sed '6p' $1 | awk '{print $17}'))
	for y in ${x[@]}; do
		if [ ${y} == 0.000 ]; then
			count=$((${count}+1))
		fi
	done
echo ${count}
}

evaluate_models () {
# when we have several model results
	base_directory=$1
	model_name_prefix=$2
	hypothesis_file=$3
	output_directory=$4
	evaluation_result=$5
	reference_path=$6
	BPE_model_path=$7

	for evaluated_model in $base_directory/* ; do
		model_name=$(basename $evaluated_model)
		if [ -d ${evaluated_model} ] || \
           [ ${model_name} == ${model_name_prefix}* ]; then
			../../evaluation.sh \
				${model_name}/${hypothesis_file} \
				${reference_path} \
				${BPE_model_path} \
				${output_directory} \
				${evaluation_result}
		fi
	done
}
