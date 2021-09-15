undo_BPE () {

	sentencepiece_model=$1
	hypothesis_file=$2
	echo "Undoing BPE... (sentencepiece)"
	spm_decode \
		--model=${sentencepiece_model} \
		--input_format=piece \
		< ${hypothesis_file} > \
		${hypothesis_file}.unBPE
	echo "BPE undone..."

	raw_hypothesis=${hypothesis_file}.unBPE
	echo "Restoring special characters..."
	cat ${raw_hypothesis} | sed 's/ TM / ™ /g' > ${raw_hypothesis}.special
	cat ${raw_hypothesis}.special | sed 's/ ? / ? /g' > ${raw_hypothesis}.special
	cat ${raw_hypothesis}.special | sed 's/′′/″/g' > ${raw_hypothesis}.special
	mv ${raw_hypothesis}.special ${raw_hypothesis}
	rm ${raw_hypothesis}.special
	echo "All special characters have been restored!"

}

if [ $# -ne 5 ]; then
  echo "Five arguments must be entered"
  exit
fi
hypothesis_path=$1
reference_path=$2
sentencepiece_model=$3
output_directory=$4
evaluation_result=$5

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
