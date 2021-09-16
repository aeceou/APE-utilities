#!/bin/bash

if [ $# -ne 5 ]; then
    echo "Five arguments must be entered"
    exit
fi
hypothesis_path=$1
reference_path=$2
sentencepiece_model=$3
output_directory=$4
evaluation_result=$5

undo_BPE () {

    sentencepiece_model=$1
    hypothesis_file=$2
    output_file=$3
    echo "Undoing BPE... (sentencepiece)"
    spm_decode \
        --model=${sentencepiece_model} \
        --input_format=piece \
	    --output=${output_file} \
        ${hypothesis_file}
    echo "BPE undone..."

    echo "Restoring special characters..."
    cat ${output_file} | sed 's/ TM / ™ /g' > ${output_file}.tmp.1
    cat ${output_file}.tmp.1 | sed 's/ ? / ? /g' > ${output_file}.tmp.2
    cat ${output_file}.tmp.2 | sed 's/′′/″/g' > ${output_file}.tmp.3
    mv ${output_file}.tmp.3 ${output_file}
    rm ${output_file}.tmp.*
    echo "All special characters have been restored!"

}

raw_hypotheses=${output_directory}/raw_hypotheses

undo_BPE ${sentencepiece_model} ${hypothesis_path} ${raw_hypotheses}

script_directory=$( dirname $0 )
BLEU_script=${script_directory}/multi-bleu.perl
TER_script=${script_directory}/runTER.sh

echo "TER scoring..."
bash ${TER_script} \
    -h ${raw_hypotheses} \
    -r ${reference_path} \
    -o ${output_directory} \
    -s ${evaluation_result}
echo "TER scoring done..."

echo "BLEU scoring..."
perl ${BLEU_script} \
    ${reference_path} \
    < ${raw_hypotheses} > \
    ${output_directory}/${evaluation_result}_BLEU_output_caseInsens.sum
echo "BLEU scoring done!"
