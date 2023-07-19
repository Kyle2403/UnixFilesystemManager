#!/bin/bash


diff_out=diff.txt
err_log=err.txt
command="python -m coverage run --append nautilus.py"

rm -f .coverage $diff_out $err_log

for in in $(find e2e_tests -mindepth 1 -wholename '*.in' 2> /dev/null)
do
    out=$(echo $in | sed -e "s/\.in$/\.out/g")
    cat $in | $command 2>> $err_log | diff - $out >> $diff_out
done

python -m coverage report
python -m coverage html