echo "ITGSend -a 10.0.3.1 -C $1 -u 16 1400 -t 100000"
ITGSend -a 10.0.3.1 -C $1 -u 16 1400 -t 100000
mkdir $1'pps'
chmod 777 $1'pps'
