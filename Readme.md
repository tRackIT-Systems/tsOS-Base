# tsOS-base
[![Build tsOS-base Images](https://github.com/trackIT-Systems/tsOS-base/actions/workflows/build.yml/badge.svg)](https://github.com/trackIT-Systems/tsOS-base/actions/workflows/build.yml)
![GitHub Release](https://img.shields.io/github/v/release/trackIT-Systems/tsOS-base)

tsOS-base is the basis for trackIT Systems operating system distributions for sensor stations in stand-alone operation in the field. It is based on a Raspberry Pi OS and installs some software that is required for the various purposes.

## Download

The image of tsOS-base can be downloaded in the [GitHub Releases](https://github.com/trackIT-Systems/tsOS-base/releases) section of this repository. 

## Build tsOS base

tsOS-base is available in two versions for a) arm64 (Raspberry Pi 3+ and newer) and b) armhf (< Raspberry Pi 3) devices. The images can be built using [pimod](https://github.com/Nature40/pimod).

```sh
$ docker-compose run --rm pimod pimod.sh tsOS-base.Pifile
### FROM https://downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2023-10-10/2023-10-10-raspios-bookworm-arm64-lite.img.xz
Using cache: .cache/downloads.raspberrypi.com/raspios_lite_arm64/images/raspios_lite_arm64-2023-10-10/2023-10-10-raspios-bookworm-arm64-lite.img.xz
### TO tsOS-base-arm64.img
Moving temporary /tmp/tmp.PoPljJLbOK to tsOS-base-arm64.img
...
```

## Configuration

The system can be configured through different files in the `/boot` partition.

### [`boot/cmdline.txt`](boot/cmdline.txt)

`cmdline.txt` holds the kernel boot commandline, which allows to configure the hostname in newer systemd versions. This behavioud is emulated and a hostname can be configured by setting `systemd.hostname=workshop-test-00001`

### [`/boot/firmware/mqttutil.conf`](boot/mqttutil.conf)

Mqttutil reports system statistics via MQTT, [see example config](https://github.com/trackIT-Systems/pymqttutil/blob/main/etc/mqttutil.conf).

### `/boot/firmware/wireguard.conf`

A wireguard configuration can be set using this configuration file. 

### [`/boot/firmware/mosquitto.d/`](boot/firmware/mosquitto.d/)

Files in this directory are loaded by mosquitto. E.g. mqtt brokers for reporting can be set using files in this folder.
