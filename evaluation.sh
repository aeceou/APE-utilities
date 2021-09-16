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
    raw_hypotheses=${output_directory}/raw_hypotheses
    echo "Undoing BPE... (sentencepiece)"
    spm_decode \
        --model=${sentencepiece_model} \
        --input_format=piece \
        < ${hypothesis_file} > \
        ${raw_hypotheses}
    echo "BPE undone..."

    echo "Restoring special characters..."
    cat ${raw_hypotheses} | sed 's/ TM / ™ /g' > ${raw_hypotheses}
    cat ${raw_hypotheses} | sed 's/ ? / ? /g' > ${raw_hypotheses}
    cat ${raw_hypotheses} | sed 's/′′/″/g' > ${raw_hypotheses}
    echo "All special characters have been restored!"

}

script_directory=$( dirname $0 )
BLEU_script=${script_directory}/multi-bleu.perl
TER_script=${script_directory}/runTER.sh

undo_BPE ${sentencepiece_model} ${hypothesis_path}

echo "TER scoring..."
bash ${TER_script} \
    -h ${hypothesis_path} \
    -r ${reference_path} \
    -o ${output_directory} \
    -s ${evaluation_result}
echo "TER scoring done..."

echo "BLEU scoring..."
perl ${BLEU_script} \
    ${reference_path} \
    < ${hypothesis_path} > \
    ${output_directory}/${evaluation_result}.BLEU
echo "BLEU scoring done!"
