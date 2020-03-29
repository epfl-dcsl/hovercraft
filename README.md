# HovercRaft

This repository contains the code for the paper:

> HovercRaft: Achieving Scalability and Fault-tolerance for microsecond-scale Datacenter Services  
> Marios Kogias, Edouard Bugnion  
> Eurosys 2020  

You can find the paper [here]()

## Contents

The repository contains several submodules and directories.

<dl>
  <dt>r2p2</dt>
  <dd>The codebase for the Request Response Pair Protocol for datacenter RPCs</dd>

  <dt>raft</dt>
  <dd>The raft codebase used with its modifications.</dd>

  <dt>redis</dt>
  <dd>The redis codebase with the R2P2 modifications</dd>

  <dt>lancet</dt>
  <dd>The lancet latency measuring tool and load generator used for the experiments</dd>

  <dt>redismodule</dt>
  <dd>A redis module that implements the YCSB-E workload used in HovercRaft's evaluation</dd>

  <dt>distbenchr</dt>
  <dd>A python package used to run distributed experiments</dd>

  <dt>scripts</dt>
  <dd>Basic scripts to deploy and run HovercRaft for the synthetic and Redis experiments.</dd>
</dl>

## Build

To get the dependencies and build an example run:
```
git submodule update --init --recursive
make hovercraft-stss
```

Check the Makefile for more build options.

## Experiments
Check the `scipts` directory for running experiments. Configure the `fabfile.py` and `driver.py` scripts accordingly.

Also, configure the `r2p2.conf` for HovercRaft as described in the R2P2 [repository](https://github.com/epfl-dcsl/r2p2).
