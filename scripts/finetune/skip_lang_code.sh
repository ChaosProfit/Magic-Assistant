#!/bin/bash

src_file=$1
target_file="$1_skipped"
python3 -m fastchat.data.optional_clean --in $src_file --out $target_file --keep-lang en,zh,zh_Hant


#src_file=$1
#target_file="$1_skipped"

#for lang_code in 'da', 'unknown', 'ro', 'hi', 'cs', 'la', 'ca', 'ik', 'uz', 'bn', 'nn', 'sl', 'it', 'uk', 'ja', 'vi', 'pl', 'bg', 'te', 'or', 'es', 'th', 'no', 'fr', 'ru', 'iw', 'ms', 'et', 'haw', 'sn', 'jw', 'tl', 'el', 'fy', 'sv', 'fo', 'ko', 'af', 'lv', 'ta', 'gl', 'hu', 'hr', 'ar', 'de', 'sq', 'nl', 'sw', 'fi', 'id', 'sa', 'tr', 'bs', 'sr', 'fa', 'pt', 'sk', 'nl'
#do
#    echo "begin to skip $lang_code"
#    python3 -m fastchat.data.optional_clean --in $src_file --out $target_file --skip-lang $lang_code
#    mv $target_file $src_file
#    echo "suc to skip $lang_code"
#done
