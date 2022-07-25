ITGDec recv_log_file > recv_log

echo "recv_log"
ITGDec recv_log_file

echo "ctl_record last 6 line"
tail -n 6 ctl_record.txt

mv ctl_record.txt ./$1
mv recv_log ./$1
