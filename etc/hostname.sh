#!/usr/bin/env bash

echo "Running RasperryPi hostname configuration script..." 1>&2

HOSTNAME="tsOS-base"
ID=`cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2 | cut -c9-16`

if [ "$ID" == "" ]; then
    echo "Error reading Raspberry Pi serial number, defaulting to $HOSTNAME" 1>&2
else
    HOSTNAME=${HOSTNAME}-$ID
fi

echo "Scanning kernel commandline for hostname" 1>&2
CMDLINE=( $(cat /proc/cmdline) )
for arg in "${CMDLINE[@]}"; do
    case "${arg}" in
        systemd.hostname=*)
            HOSTNAME="${arg#systemd.hostname=}"
            echo "Found '${arg}'" 1>&2
            ;;
    esac
done

echo "Setting via hostnamectl: $HOSTNAME." 1>&2
hostnamectl set-hostname $HOSTNAME

echo "Setting in /etc/hosts" 1>&2
cat > /etc/hosts <<EOF
127.0.0.1	localhost
::1		localhost ip6-localhost ip6-loopback
ff02::1		ip6-allnodes
ff02::2		ip6-allrouters

127.0.1.1	$HOSTNAME
EOF

echo "Appending /boot/firmware/hosts" 1>&2
cat /boot/firmware/hosts >> /etc/hosts

echo "Done." 1>&2
