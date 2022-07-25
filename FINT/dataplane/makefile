BMV2_SWITCH_EXE = simple_switch
# simple_switch_grpc for grpc,
# simple_switch for thrift
TOPO = ../topology/topology.json

CONTROL_PLANE = TRUE

TMP_DIR = tmp
SOURCE_DIR = p4src
BUILD_DIR = $(SOURCE_DIR)/build
PCAP_DIR = ./$(TMP_DIR)/pcaps
LOG_DIR = ./$(TMP_DIR)/logs

TOPO_SCALE = 4

P4C = p4c-bm2-ss
P4C_ARGS += --p4runtime-files $(BUILD_DIR)/$(basename $@).p4info.txt

RUN_SCRIPT = ./run_topo/run_mininet.py

ifndef TOPO
TOPO = topology.json
endif

# source = $(wildcard $(SOURCE_DIR)/*.p4)
source = $(notdir $(wildcard $(SOURCE_DIR)/*.p4))
compiled_json := $(source:.p4=.json)

# for delete .pyc files
pyc_files = $(wildcard run_topo/*.pyc run_topo/p4runtime_lib/*.pyc)

ifndef DEFAULT_PROG
DEFAULT_PROG = $(notdir $(wildcard $(SOURCE_DIR)/*.p4))
endif
DEFAULT_JSON = $(BUILD_DIR)/$(DEFAULT_PROG:.p4=.json)

# Define NO_P4 to start BMv2 without a program
ifndef NO_P4
run_args += -j $(DEFAULT_JSON)
endif

# Set BMV2_SWITCH_EXE to override the BMv2 target
ifdef BMV2_SWITCH_EXE
run_args += -b $(BMV2_SWITCH_EXE)
endif

ifdef PCAP_DIR
run_args += -p $(PCAP_DIR)
endif

ifdef LOG_DIR
run_args += -l $(LOG_DIR)
endif

ifdef CONTROL_PLANE
run_args += -c
endif


TOPO_SCRIPT = ../topology/fattree.py

ifdef TOPO_SCALE
topo_args += -k $(TOPO_SCALE)
endif

ifdef TOPO
topo_args += -t $(TOPO)
endif


all: run

run: build
	python $(TOPO_SCRIPT) $(topo_args)
	sudo python $(RUN_SCRIPT) -t $(TOPO) $(run_args)

log: build
	python $(TOPO_SCRIPT) $(topo_args)
	sudo python $(RUN_SCRIPT) -t $(TOPO) $(run_args) -lc

stop:
	sudo mn -c

build: dirs $(compiled_json)

%.json: $(SOURCE_DIR)/%.p4
	$(P4C) --p4v 16 $(P4C_ARGS) -o $(BUILD_DIR)/$@ $<

dirs:
	mkdir -p tmp
	mkdir -p $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)

clean: stop
	rm -f *.pcap
	rm -rf $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)
	rm -rf $(TMP_DIR)
	rm -f $(pyc_files) port_mapping.json