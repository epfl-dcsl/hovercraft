# MIT License
#
# Copyright (c) 2019-2021 Ecole Polytechnique Federale Lausanne (EPFL)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# Flags explanation
# ACCELERATED=1 - split request data and metadata
# LB_REPLIES=1  - load balance who replies to the client, default policy rand
# SMART_LB=1    - load balance with JBSQ
# SKIP_NO_SE=1  - skip no side effect operations on all nodes but the replier
# SWITCH_AGG=1  - hovercraft++ (support for in-network aggregation)

.PHONY: vanilla-stss hovercraft-stss hovercraftplus redismodule

ROOTDIR=$(shell git rev-parse --show-toplevel)
R2P2_DIR=$(ROOTDIR)/r2p2

vanilla-stss:
	make clean-all
	make -C raft
	make -C r2p2/dpdk-apps stss

hovercraft-stss:
	make clean-all
	make -C raft
	make -C r2p2/dpdk-apps stss ACCELERATED=1 LB_REPLIES=1 SKIP_NO_SE=1 # SMART_LB=1


hovercraftplus-stss:
	make clean-all
	make -C raft SWITCH_AGG=1
	make -C r2p2/dpdk-apps stss SWITCH_AGG=1 ACCELERATED=1 LB_REPLIES=1 SKIP_NO_SE=1 SMART_LB=1

lancet:
	make -C lancet-tool coordinator
	make -C lancet-tool agents_r2p2_nic_ts R2P2=$(R2P2_DIR)/r2p2
	make -C lancet-tool manager
	make -C lancet-tool deploy HOSTS=icnals01,icnals02,icnals03,icnals04

redismodule:
	make -C redismodule

clean-all:
	make -C raft clean
	make -C r2p2 clean
	make -C redismodule clean
