#!/bin/bash

current_directory=$( readlink -f $( dirname $0 ) )

if [[ ! -d "${current_directory}/plugins/multeval" ]]; then
    git clone https://github.com/aeceou/multeval.git $( dirname $0 )/plugins/multeval
fi

gold_standard=$1
# if there are several reference texts:
# gold_standard=${gold_standard}*
# However, we normally have a single reference text
mt_baseline=$2
# it can be the given raw MT outputs or the baseline APE system's hypothesis texts
system_hypotheses=$3

multeval_directory=${current_directory}/plugins/multeval
ln -s ${current_directory}/data ${multeval_directory}/data
cd ${multeval_directory}
bash ./multeval.sh \
    eval \
    --refs ${gold_standard} \
    --hyps-baseline ${mt_baseline} ${mt_baseline} \
    --hyps-sys1 ${system_hypotheses} ${system_hypotheses} \
    --metrics bleu ter length
