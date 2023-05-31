#!/usr/bin/env python3

import glob
import os
import logging
import subprocess
from typing import List, Tuple


def match_usb_manuf(target) -> Tuple[str, str]:
    return [os.path.split(p)[0] for p in glob.glob("/sys/bus/usb/devices/*/manufacturer") if target in open(p, encoding="ascii").read()]


def get_paths(targets: Tuple[str] = ("HUAWEI_MOBILE", "Mobile")) -> List[Tuple[str, str]]:
    huawei_paths = []
    for target in targets:
        huawei_paths += [os.path.split(p)[1].split(".") for p in match_usb_manuf(target)]

    if huawei_paths:
        logging.info("Found %s devices at %s", targets, huawei_paths)
        return huawei_paths
    else:
        logging.warning("Did not find %s devices.", targets)
        exit(1)


def cycle_paths(huawei_paths: List[Tuple[str, str]]):
    # power cycle hub
    for location, port in huawei_paths:
        cmd = ["uhubctl", "--location", location, "--action", "2"]
        logging.info("Power cycling cmd: `%s`", " ".join(cmd))
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode:
            logging.warning("Device %s cycling failed (%s), please check if hardware is working", location, p.returncode)


def ping_find_iface(candidates: Tuple[str]) -> List[str]:
    return [i for i in os.listdir('/sys/class/net/') if i in candidates]


def ping_cmd(ping_target: str = "8.8.8.8", iface_candidates: Tuple[str] = ("eth1", "usb0")) -> List[str]:
    # define basic ping command
    cmd = ["ping", ping_target, "-c", "1"]

    # find huawei ethernet device
    ifaces = ping_find_iface(iface_candidates)
    if len(ifaces):
        logging.info("Found Huawei interface candidates: %s, using first.", ifaces)
        cmd += ["-I", ifaces[0]]
    else:
        logging.warning("Did not find Huawei interface candidates, ignoring binding.")

    return cmd


def ping_evaluate(cmd: List[str]):
    logging.info("Running ping test: `%s`", " ".join(cmd))
    p = subprocess.Popen(cmd)
    p.wait()
    if not p.returncode:
        logging.info("Ping test succeeded, exiting.")
        exit(0)

    logging.info("Ping test failed...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # run ping test
    ping_evaluate(ping_cmd())

    # get huawei usb path
    cycle_paths(get_paths())

    logging.info("Finished.")
