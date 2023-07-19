in=$1
exp_out=$2
python ../nautilus.py < $in > $exp_out
cat $exp_out
python -m coverage run -a ../nautilus.py < $in | diff $exp_out -
python -m coverage html
