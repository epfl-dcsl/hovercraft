#!/usr/bin/python

from fabric.tasks import execute
from fabric.api import env
from fabfile import *
from distbenchr import *
import time
import signal

PEERS = [
        ("10.90.44.216", 8000),
        ("10.90.44.217", 8000),
        ("10.90.44.220", 8000),
        ]

PATTERNS = {
        10: "step:10000:200000:5000:20000",
        "redis": "step:1000:180000:2000",
        }

CFGS = {
        "unrep": (
            [0],
            [
                ("vanilla", "")
            ]
            ),
        "rep": (
            [3],
            [
                ("vanilla", "WITH_RAFT=1")
                ("lb_rep_skip_no_se_smart", "WITH_RAFT=1 LB_REPLIES=1 SMART_LB=1 SKIP_NO_SE=1"),
            ]
            ),
        "rep_accel": (
            [3],
            [
                ("vanilla", "WITH_RAFT=1 ACCELERATED=1")
                ("lb_rep_skip_no_se_smart", "WITH_RAFT=1 ACCELERATED=1 LB_REPLIES=1 SMART_LB=1 SKIP_NO_SE=1"),
            ]
            )
        }

FOLLOWERS_FN = {
        3: run_followers3,
    }

NO_SE_RATIO = 0.75

def synthetic_time():
    program = "stss"
    service_times = [10]
    for mode, info in CFGS.iteritems():
        if "rep_accel" in mode:
            target = "multicast"
        else:
            target = "master"
        for p in info[0]:
            for cname, cflags in info[1]:
                execute(build, program, flags=cflags)
                execute(deploy, program)
                for s in service_times:
                    if mode == "switch_accel":
                        execute(run_p4)
                    mnt = Monitor()
                    if p > 0:
                        mnt.bg_execute(run_master, program, should_wait=False)
                        time.sleep(2)
                        mnt.bg_execute(FOLLOWERS_FN[p], program, should_wait=False)
                        proto = "stssr_fixed:{}_fixed:0_fixed:0_{}".format(s, NO_SE_RATIO)
                    else:
                        mnt.bg_execute(run_unrep, program, should_wait=False)
                        proto = "stss_fixed:{}_fixed:0_fixed:0".format(s)
                    time.sleep(60)
                    fname = "st_fixed_{}_NO_SE_{}_{}_peers_{}_{}.txt".format(s, NO_SE_RATIO, mode, p, cname)
                    mnt.bg_execute(run_lancet_sym_hw, PATTERNS[s],
                            proto, fname, target=target, should_wait=True)
                    mnt.monitor()
                    mnt.killall()

def main():
    execute(build_raft)
    execute(prepare_clients)
    execute(configure_peers, PEERS)

    print "Execute synthetic time experiment"
    synthetic_time()


if __name__ == "__main__":
    os.setpgrp() # create new process group, become its leader
    try:
        main()
    except:
        import traceback
        traceback.print_exc()
    finally:
        os.killpg(0, signal.SIGKILL) # kill all processes in my group
