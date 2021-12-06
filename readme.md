# FINT: Flexible In-band Network Telemetry Architecture



## 1. Abstract







## 2. Experiment

### 2.1 FINT

#### 2.1.1 different background bandwidth

1.  To start data plane:

   ```shell
   cd /dataplane/p4src
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

   change int_switch_cmg.p4 to int_switch_cmr.p4 for CMR.

2. To install entries and set register value:

   ```sh
   cd /controller
   make
   ```

   change `make` to `make cmr` for CMR

3. In mininet CLI:

   ```
   xterm h1 h9
   ```

4. In xterm of 'h9':

   ```sh
   cd ../experiment/1\ bandwidth/bw_cmg
   sh receiver.sh
   ```

   change bw_cmg to bw_cmr for CMR.

5. Start a new terminal, and:

   ```sh
   cd ../experiment/1\ bandwidth/bw_cmg
   sudo python int_count_cmg.py
   ```

   change bw_cmg and bandwidth_cmg.py to bw_cmr and bandwidth_cmr.py for CMR.

6. In xterm of 'h1':

   ```
   cd ../experiment/1\ bandwidth/bw_cmg
   sh sender.sh 100
   ```

   (100 refers to the packet send ratio of D-ITG (pps))
   
   change bw_cmg to bw_cmr for CMR.
   
7.  Get the result, start a new terminal, and:

    ```
    cd ../experiment/1\ bandwidth/bw_cmg
    sh parser.sh 100
    ```

    

For change background bandwidth, restart the step 4-6 and change the value of **100** in step 6.



#### 2.1.2 different period

1. To start data plane:

   ```shell
   cd /dataplane/p4src
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

   change **int_switch_cmg.p4** to **int_switch_cmr.p4** for CMR.

2. To install entries and set register value:

   ```sh
   cd /controller
   make
   ```

   change `make` to `make cmr` for CMR

3. In mininet CLI:

   ```
   xterm h1 h9
   ```

4. In xterm of 'h9':

   ```sh
   cd ../experiment/2\ period/period_cmg
   sh receiver.sh
   ```

   change **period_cmg** to **period_cmr** for CMR.

5. Start a new terminal, and:

   ```sh
   cd ../experiment/2\ period/period_cmg
   sudo python int_count_cmg.py
   ```

   change **period_cmg** and **int_count_cmg.py** to **period_cmr** and **int_count_cmr.py** for CMR.

6. In xterm of 'h1':

   ```sh
   cd ../experiment/2\ period/period_cmg
   sh sender.sh 100
   ```

   (100 refers to the telemetry period (ms))
   
   change **period_cmg** to **period_cmr** for CMR.



For change period, in the terminal of step 2: (20000us)

```
python change_int_parameters.py -a -p 20000
```

and restart step 4-6 (in step 6, change the value of **100** to **20**).



#### 2.1.3 different parameter n

1. To start data plane:

   ```shell
   cd /dataplane/p4src
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

   change **int_switch_cmg.p4** to **int_switch_cmr.p4** for CMR.

2. To install entries and set register value:

   ```sh
   cd /controller
   make
   ```

3. Change bitmap task: open a new terminal and

   (in terminal of step 2)

   ```shell
   python change_int_parameters.py -a -bt 48643
   ```

   change **48643** to **55435** for CMR.

4. In mininet CLI:

   ```
   xterm h1 h9
   ```

5. In xterm of 'h9':

   ```sh
   cd ../experiment/3\ para_n/para_n_cmg
   sh receiver.sh
   ```

   change **para_n_cmg** to **para_n_cmr** for CMR.

6. Open a new terminal, and:

   ```sh
   cd ../experiment/3\ para_n/para_n_cmg
   sudo python int_count_cmg.py
   ```

   change **para_n_cmg** and **int_count_cmg.py** to **para_n_cmr** and **int_count_cmr.py** for CMR.

7. In xterm of 'h1':

   ```sh
   cd ../experiment/3\ para_n/para_n_cmg
   sh sender.sh 3
   ```

   (3 refers to the *n* value)
   
   change **para_n_cmg** to **para_n_cmr** for CMR.



For change period, in the terminal of step 2: (para_n = 1, 2, ...)

```shell
python change_int_parameters.py -a -n 2
```

and restart step 4-6 (in step 6, change the value of **3** to **2**).



#### 2.1.4 FCT with different n

1. To start data plane:

   ```shell
   cd /dataplane/p4src
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

   change **int_switch_cmg.p4** to **int_switch_cmr.p4** for CMR.

2. To install entries and set register value:

   ```sh
   cd /controller
   make
   ```

3. Change bitmap task: open a new terminal and

   (in terminal of step 2)

   ```shell
   python change_int_parameters.py -a -bt 48643
   ```

   change **48643** to **55435** for CMR.

4. In mininet CLI:

   ```
   xterm h1 h9
   ```

5. In xterm of 'h9':

   ```sh
   cd ../experiment/4\ FCT/fct_cmg
   sh receiver.sh
   ```

   change **fct_cmg** to **fct_cmr** for CMR.

6. In xterm of 'h1':

   ```sh
   cd ../experiment/4\ FCT/para_n_cmg
   sh sender.sh 3
   ```

   (3 refers to the *n* value)
   
   change **fct_cmg** to **fct_cmr** for CMR.



For change period, in the terminal of step 2: (para_n = 1, 2, ...)

```shell
python change_int_parameters.py -a -n 2
```

and restart step 4-6 (in step 6, change the value of **3** to **2**).



#### 2.1.5 different support ratio

1. To start data plane:

   ```shell
   cd /dataplane/p4src
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

   change **int_switch_cmg.p4** to **int_switch_cmr.p4** for CMR.

2. To install entries and set register value:

   ```sh
   cd /controller
   make
   ```

   change `make` to `make cmr` for CMR

3. In mininet CLI:

   ```
   xterm h1 h9
   ```

4. In xterm of 'h9':

   ```sh
   cd ../experiment/5\ support/support_cmg
   sh receiver.sh
   ```

   change **period_cmg** to **period_cmr** for CMR.

5. Start a new terminal, and:

   ```sh
   cd ../experiment/5\ support/support_cmg
   sudo python int_count_cmg.py
   ```

   change **support_cmg** and **int_count_cmg.py** to **support_cmr** and **int_count_cmr.py** for CMR.

6. In xterm of 'h1':

   ```sh
   cd ../experiment/5\ support/support_cmg
   sh sender.sh 100
   ```

   (100 refers to the percentage of switches that support FINT)

   change **support_cmg** to **support_cmr** for CMR.



For change the switch to support FINT or not:

```
python change_int_parameters.py -s <switch_id> -sp 0
```

(1 for support and 1 for not.)

and restart step 4-6 (in step 6, change the value of **100** to corresponding proportion).



#### 2.1.6 INT packet number and bandwidth occupation (compare)

1. To start data plane:

   ```shell
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

2. To install entries and set register value: (bitmap task: 1110 1000 0001 1011 = 59419)

   ```shell
   cd /controller
   make
   python change_int_parameters.py -a -bt 59419
   ```

3. In mininet CLI:

   ```shell
   xterm h1 controller
   ```

4. In xterm of "controller":

   ```shell
   cd ../packet
   python receive_1.py
   ```

5. In xterm of "h1":

   ```shell
   cd ../packet
   python send_udp_packet.py lr
   ```



For change INT sampling period:

```
cd /controller
python change_int_parameters.py -a -p 100000
```

then do step 4 and 5.



#### 2.1.7 average INT length (compare)

1. To start data plane:

   ```shell
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

2. To install entries and set register value: (bitmap task: 1110 1000 0001 1011 = 59419)

   ```shell
   cd /controller
   make
   python change_int_parameters.py -a -bt 59419
   ```

3. In mininet CLI:

   ```shell
   xterm h1 controller
   ```

4. In xterm of "controller":

   ```shell
   cd ../packet
   python receive_2.py
   ```

   (s17-eth1)

5. In xterm of "h1":

   ```shell
   cd ../packet
   python send_udp_packet.py lr
   ```



For change INT sampling period:

```
cd /controller
python change_int_parameters.py -a -p 100000
```

then do step 4 and 5.

#### 2.1.8 bandwidth occupation between controller and switch (compare)

1. To start data plane:

   ```shell
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

2. To install entries and set register value: (bitmap task: 1110 1000 0001 1011 = 59419)

   ```shell
   cd /controller
   make
   python change_int_parameters.py -a -bt 59419
   ```

3. In mininet CLI:

   ```shell
   xterm h1 controller
   ```

4. In xterm of "controller":

   ```shell
   cd ../packet
   python receive_3.py
   ```

5. In xterm of "h1":

   ```shell
   cd ../packet
   python send_udp_packet.py lr
   ```



For change INT sampling period:

```
cd /controller
python change_int_parameters.py -a -p 100000
```

then do step 4 and 5.





#### 2.1.9 packet loss (compare)

1. To start data plane:

   ```shell
   cd /dataplane/p4src
   rm -r *.p4
   cp ./other/int_switch_cmg.p4 .
   cd ..
   make
   ```

2. To install entries and set register value: (bitmap task: 1110 1000 0001 1011 = 59419)

   ```shell
   cd /controller
   make
   python change_int_parameters.py -a -bt 59419
   ```

3. In mininet CLI:

   ```
   xterm h1 h9
   ```

4. In xterm of "h9":

   ```shell
   cd ../packet
   python receive_4.py
   ```

5. In xterm of "h1":

   ```shell
   cd ../packet
   python send_udp_packet.py r
   ```



For change INT sampling period:

```
cd /controller
python change_int_parameters.py -a -p 100000
```

then do step 4 and 5.



### 2.2 INT-label

base on INT-label Pro.

Note: All experiment data are saved in the folder 'experiment_data'.

#### 2.2.1 INT packet number and bandwidth occupation

1. build 

   ```shell
   cd controller/
   python coverage.py
   python detect1.py
   python detect2.py
   cd topology/
   sudo python clos.py
   ```

2. in mininet CLI:

   ```xterm p1_t1_1 p3_t1_1```

3. in xterm of 'p3_t1_1':

   ```shell
   cd ../packet
   python receive_1.py
   ```

4. in xterm of 'p1_t1_1':

   ```shell
   cd ../packet
   python send_sr_packet.py lr
   ```



For change INT sampling period:

stop all terminal, and

```shell
cd /p4_source_code
gedit my_int.p4   (then change the T value at line 249, defaut is 100000us)
sh ./run.sh
```

then do the step all above.



#### 2.2.2 average INT length

1. build 

   ```shell
   cd controller/
   python coverage.py
   python detect1.py
   python detect2.py
   cd topology/
   sudo python clos.py
   ```

2. in mininet CLI:
   
   ```shell
   xterm p1_t1_1 p3_t1
   ```

3. in xterm of 'p3_t1':

   ```shell
   cd ../packet
   python receive_2.py
   ```

   (p3_t1-eth1)

4. in xterm of 'p1_t1_1':

   ```shell
   cd ../packet
   python send_sr_packet.py lr
   ```



For change INT sampling period:

stop all terminal, and

```shell
cd /p4_source_code
gedit my_int.p4   (then change the T value at line 249, defaut is 100000us)
sh ./run.sh
```

then do the step all above.



#### 2.2.3 bandwidth occupation between controller and switch

1. build 

   ```shell
   cd controller/
   python coverage.py
   python detect1.py
   python detect2.py
   cd topology/
   sudo python clos.py
   ```

2. in mininet CLI:

```xterm p1_t1_1 p3_t1_1```

3. in xterm of 'p3_t1_1':

   ```shell
   cd ../packet
   python receive_3.py
   ```

4. in xterm of 'p1_t1_1':

   ```shell
   cd ../packet
   python send_sr_packet.py lr
   ```



For change INT sampling period:

stop all terminal, and

```shell
cd /p4_source_code
gedit my_int.p4   (then change the T value at line 249, defaut is 100000us)
sh ./run.sh
```

then do the step all above.



#### 2.2.4. packet loss 

1. build

   ```shell
   cd controller/
   python coverage.py
   python detect1.py
   python detect2.py
   cd topology/
   sudo python clos.py
   ```

2. in mininet CLI:

   ```xterm p1_t1_1 p3_t1_1```

3. in xterm of 'p3_t1_1':

   ```shell
   cd ../packet
   python receive_4.py
   ```

4. in xterm of 'p1_t1_1':

   ```shell
   cd ../packet
   python send_sr_packet.py r
   ```



For change INT sampling period:

stop all terminal, and

```shell
cd /p4_source_code
gedit my_int.p4   (then change the T value at line 249, defaut is 100000us)
sh ./run.sh
```

then do the step all above.
