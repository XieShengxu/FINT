ITGDec recv_log_file > recv_log

echo "recv_log"
mv recv_log ./$1'pps'
grep -E 'packets|bitrate' ./$1'pps'/recv_log

echo "ctl_record last 4 line"
tail -n 4 ctl_record.txt

mv ctl_record.txt ./$1'pps'
