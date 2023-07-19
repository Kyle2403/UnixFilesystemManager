in=$1
exp_out=$2
touch $in
cat > $in
python ../nautilus.py < $in > $exp_out
cat $exp_out