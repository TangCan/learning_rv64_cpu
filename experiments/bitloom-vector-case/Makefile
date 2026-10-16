BITLOOM_ROOT := $(abspath ../../target/bitloom-cli)
BITLOOM_BIN := $(BITLOOM_ROOT)/bin
OUT_DIR := $(CURDIR)/target/bitloom-out
RTL := $(OUT_DIR)/BitloomVectorCase.v
SIM := $(CURDIR)/target/vector_case_tb.vvp

.PHONY: test-icarus
test-icarus:
	@cargo install --list --root "$(BITLOOM_ROOT)" | grep -Fqx 'bitloom v1.2.4:' || { echo "Bitloom CLI 1.2.4 is required under target/bitloom-cli" >&2; exit 1; }
	PATH="$(BITLOOM_BIN):$$PATH" cargo bitloom build --package bitloom_vector_case --manifest-dir "$(CURDIR)" --out-dir "$(OUT_DIR)"
	iverilog -g2012 -s vector_case_tb -o "$(SIM)" "$(RTL)" tests/vector_case_tb.sv
	vvp "$(SIM)"
