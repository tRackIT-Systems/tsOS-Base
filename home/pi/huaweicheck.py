#!/usr/bin/env python3

import glob
import os
import logging
import subprocess
import requests
import xml.etree.ElementTree
import argparse


def match_usb_manuf(target: str) -> tuple[str]:
    return (
        os.path.split(p)[0]
        for p in glob.glob("/sys/bus/usb/devices/*/manufacturer")
        if target in open(p, encoding="ascii").read()
    )


def get_paths(targets: tuple[str] = ("HUAWEI_MOBILE", "Mobile")) -> list[tuple[str, str]]:
    huawei_paths = []
    for target in targets:
        huawei_paths += [os.path.split(p)[1].split(".") for p in match_usb_manuf(target)]

    if huawei_paths:
        logging.info("Found %s devices at %s", targets, huawei_paths)
        return huawei_paths
    else:
        logging.warning("Did not find %s devices.", targets)
        exit(1)


def cycle_paths(huawei_paths: list[tuple[str, str]], uhubctl_port: bool):
    # power cycle hub
    for location, port in huawei_paths:
        cmd = ["uhubctl", "--location", location, "--action", "2"]
        if uhubctl_port:
            cmd += ["--port", port]
        logging.info("Power cycling cmd: `%s`", " ".join(cmd))
        p = subprocess.Popen(cmd)
        p.wait()
        if p.returncode:
            logging.warning("Device %s cycling failed (%s), please check if hardware is working", location, p.returncode)


def ping_find_iface(candidates: tuple[str]) -> list[str]:
    return [i for i in os.listdir('/sys/class/net/') if i in candidates]


def ping_cmd(ping_target: str = "8.8.8.8", iface_candidates: tuple[str] = ("eth1", "usb0"), count: int = 10) -> list[str]:
    # define basic ping command
    cmd = ["ping", ping_target, "-c", f"{count}"]

    # find huawei ethernet device
    ifaces = ping_find_iface(iface_candidates)
    if len(ifaces):
        logging.info("Found Huawei interface candidates: %s, using first.", ifaces)
        cmd += ["-I", ifaces[0]]
    else:
        logging.warning("Did not find Huawei interface candidates, ignoring binding.")

    return cmd


def ping_evaluate(cmd: list[str]) -> int:
    logging.info("Running ping test: `%s`", " ".join(cmd))
    p = subprocess.Popen(cmd)
    p.wait()
    if not p.returncode:
        logging.info("Ping test succeeded, exiting.")
        return 0

    logging.info("Ping test failed...")
    return p.returncode


def huawei_reset_api(huawei_addr: str = "192.168.8.1", timeout: float = 10) -> bool:
    session = requests.session()

    session.get(f"http://{huawei_addr}/", timeout=timeout)
    logging.debug("Session cookies: %s", session.cookies)

    tokinfo_resp = session.get(f"http://{huawei_addr}/api/webserver/SesTokInfo", timeout=timeout)
    token = xml.etree.ElementTree.fromstring(tokinfo_resp.content).find("TokInfo").text
    logging.debug("__RequestVerificationToken: %s", token)

    post_resp = session.post(
        f"http://{huawei_addr}/api/device/control",
        data="<?xml version=\"1.0\" encoding=\"UTF-8\"?><request><Control>1</Control></request>",
        headers={"__RequestVerificationToken": token},
        timeout=timeout,
    )

    logging.debug(post_resp.content)
    post_xml = xml.etree.ElementTree.fromstring(post_resp.content)

    if post_xml.tag == "error":
        logging.info("Reseting huawei failed: %s (%s)", post_xml.find("message").text, post_xml.find("code").text)
        return False
    else:
        logging.info("Reseting huawei successful.")
        return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser("huaweicheck", "Check and handle Huawei E3372 Device hangs")

    parser.add_argument("-v", "--verbose", help="increase verbosity", action="store_true", default=False)
    parser.add_argument("--test", help="Run ping check before resetting", default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument("--uhubctl", help="use uhubctl for reset", default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument("--uhubctl-port", help="use uhubctl port-level addressing (not supported on most devices)", default=False, action=argparse.BooleanOptionalAction)
    parser.add_argument("--api", help="use huawei http api for reset", default=True, action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.debug("Running in configuration: %s", args)

    # run ping test
    if args.test:
        ping_ret = ping_evaluate(ping_cmd())
        if not ping_ret:
            exit(0)

    if args.api:
        api_ret = huawei_reset_api()

    if args.uhubctl:
        paths = get_paths()
        cycle_paths(paths, uhubctl_port=args.uhubctl_port)

    logging.info("Finished.")
