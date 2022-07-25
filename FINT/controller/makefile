
TOPO = ../topology/topology.json
PORT_MAPPING = ../dataplane/port_mapping.json

ENTRY_DIR = entries

INST_SCRIPT = ./install_entries.py

inst_args += -e $(ENTRY_DIR)

ifdef TOPO
inst_args += -t $(TOPO)
endif

ifdef PORT_MAPPING
inst_args += -p $(PORT_MAPPING)
endif

# for delete .pyc files
pyc_files = $(wildcard *.pyc)

all: run

run: msg

msg: dirs
	sudo python $(INST_SCRIPT) $(inst_args) -c msg

msr: dirs
	sudo python $(INST_SCRIPT) $(inst_args) -c msr

dirs:
	mkdir -p $(ENTRY_DIR)

clean:
	rm -rf $(ENTRY_DIR)
	rm -f $(pyc_files)
