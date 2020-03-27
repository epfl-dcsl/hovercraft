#!/usr/bin/python

from fabric.api import env, roles, run, put, get, local
from fabric.tasks import execute
from fabric.context_managers import cd
from distbenchr import *
import numpy as np

env.roledefs = {
        'master-server': ['icnals16'],
        'followers3': ['icnals17', 'icnals20'],
        'lancet-agents': ['icnals01', 'icnals02', 'icnals03', 'icnals04'],
        'coordinator': ['icnals10'],
        'multicast': ['224.123.123.123']
        }

PROJECT_DIR = "/home/kogias/hovercraft"
DPDK_DIR = "{}/r2p2/dpdk".format(PROJECT_DIR)
APP_DIR = "{}/r2p2/dpdk-apps".format(PROJECT_DIR)
LANCET_DIR = "{}/lancet-tool".format(PROJECT_DIR)
RES_DIR = "{}/results".format(PROJECT_DIR)

def icnals_ip(servername):
    return "10.90.44.2{}".format(servername[-2:])

@roles('coordinator')
def build(program_name, flags=None):
    run("make -C {} {} {}".format(APP_DIR, program_name, flags))

@roles('coordinator')
def build_raft(flags=""):
    run("make -C {}/raft clean && make -C {}/raft {}".format(PROJECT_DIR, PROJECT_DIR, flags))

@roles('lancet-agents')
def prepare_clients():
    run("sudo sh -c 'FREQ=`cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq` && for i in /sys/devices/system/cpu/cpu[0-9]*; do echo userspace > $i/cpufreq/scaling_governor; echo $FREQ > $i/cpufreq/scaling_setspeed; done'")
    run("sudo ethtool -C enp65s0 adaptive-rx off adaptive-tx off rx-usecs 0 rx-frames 0 tx-usecs 0 tx-frames 0 || true")

@roles('master-server', 'followers3')
def deploy(program_name):
    run("mkdir -p /tmp/{}/".format(os.getlogin()))
    put("{}/{}".format(APP_DIR,program_name), "/tmp/{}".format(os.getlogin()))
    run("chmod +x /tmp/kogias/{}".format(program_name))

def _prepare_huge_pages(hugepages):
    run('sudo sh -c "echo never > /sys/kernel/mm/transparent_hugepage/enabled"')
    run('sudo sh -c "echo %d > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages"' % hugepages)
    run('sudo sh -c "echo 4096 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages"')
    run("sudo find /dev/hugepages -name 'rtemap_*' -delete")

def _prepare_dpdk(pcie="01:00.0"):
    #_prepare_huge_pages(4096)
    run("rm -rf /tmp/{} && mkdir -p /tmp/{}".format(os.getlogin(), os.getlogin()))
    put("{}/x86_64-native-linuxapp-gcc/kmod/igb_uio.ko".format(DPDK_DIR), '/tmp/{}'.format(os.getlogin()))
    put("{}/usertools/dpdk-devbind.py".format(DPDK_DIR), '/tmp/{}'.format(os.getlogin()))
    run("sudo ifdown cu0")
    run("sudo sudo modprobe uio")
    run("sudo sudo insmod /tmp/{}/igb_uio.ko || true".format(os.getlogin()))
    run("sudo python /tmp/{}/dpdk-devbind.py --bind=igb_uio {}".format(os.getlogin(), pcie))

@roles('master-server', 'followers3')
def configure_peers(peers):
    _prepare_dpdk()
    # Delete old cfg
    cmd1 = "sudo sed -i '/raft/,$d' /etc/r2p2.conf"
    run(cmd1)

    # if peers cfg accordingly
    if not peers:
        return

    def to_string(peer):
        return "\t{{\n\t\tip : \"{}\"\n\t\tport : {}\n\t}}".format(peer[0], peer[1])
    peers_str = ",\n".join([to_string(x) for x in peers])
    cfg = "raft=(\n{}\n)".format(peers_str)
    cmd2 = "echo \'{}\' | sudo tee -a /etc/r2p2.conf".format(cfg)
    run(cmd2)

    # Set freq
    run("sudo sh -c 'FREQ=`cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq` && for i in /sys/devices/system/cpu/cpu[0-9]*; do echo userspace > $i/cpufreq/scaling_governor; echo $FREQ > $i/cpufreq/scaling_setspeed; done'")
    run('sudo sh -c "echo never > /sys/kernel/mm/transparent_hugepage/enabled"')

@run_bg('master-server')
def run_unrep(program_name):
    run("ulimit -c unlimited && sudo /tmp/kogias/{} -l 2".format(program_name))

@run_bg('master-server')
def run_master(program_name):
    run("ulimit -c unlimited && sudo /tmp/kogias/{} -l 2,4".format(program_name))

@run_bg('followers3')
def run_followers3(program_name):
    run("ulimit -c unlimited && sudo /tmp/kogias/{} -l 2,4".format(program_name))

@run_bg('coordinator')
def run_lancet_sym_hw(pattern, proto, file_dst, target="master"):
    run("mkdir -p {}".format(RES_DIR))
    if target[1:-1] == "master":
        dst = icnals_ip(env.roledefs['master-server'][0])
    elif target[1:-1] == "switch":
        dst = env.roledefs['switch'][0]
    else:
        dst = env.roledefs['multicast'][0]

    agents = ",".join(env.roledefs['lancet-agents'])
    cmd = "{}/coordinator/coordinator -appProto {} -comProto R2P2\
            -loadThreads 15 -symAgents {} -loadPattern {}\
            -targetHost {}:8000\
            -nicTS > {}/{}".format(LANCET_DIR, proto, agents, pattern,
                    dst, RES_DIR, file_dst)
    run(cmd)
