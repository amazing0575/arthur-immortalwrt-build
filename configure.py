import os
import sys
from pathlib import Path

features = {
    'OPENCLASH': ['luci-app-openclash'],
    'PASSWALL2': ['luci-app-passwall2', 'xray-core'],
    'HOMEPROXY': ['luci-app-homeproxy', 'sing-box'],
    'UPNP': ['luci-app-upnp'],
    'DDNS': ['luci-app-ddns', 'ddns-scripts', 'ddns-scripts-services', 'ddns-scripts-cloudflare'],
    'SAMBA': ['luci-app-samba4', 'samba4-server'],
}

def enabled(name):
    return os.environ.get('OPT_' + name, 'true').lower() == 'true'

path = Path(sys.argv[1])
if '--verify' in sys.argv:
    config = set(path.read_text().splitlines())
    missing = []
    for feature, packages in features.items():
        if enabled(feature):
            missing += [p for p in packages if f'CONFIG_PACKAGE_{p}=y' not in config]
    for required in ['CONFIG_TARGET_qualcommax=y', 'CONFIG_TARGET_qualcommax_ipq60xx=y', 'CONFIG_TARGET_DEVICE_qualcommax_ipq60xx_DEVICE_jdcloud_re-ss-01=y']:
        if required not in config:
            missing.append(required)
    if missing:
        raise SystemExit('Required selections missing after make defconfig: ' + ', '.join(missing))
    print('Device and requested package selections validated')
    raise SystemExit(0)

lines = [
    'CONFIG_TARGET_qualcommax=y',
    'CONFIG_TARGET_qualcommax_ipq60xx=y',
    'CONFIG_TARGET_MULTI_PROFILE=y',
    'CONFIG_TARGET_PER_DEVICE_ROOTFS=y',
    'CONFIG_TARGET_DEVICE_qualcommax_ipq60xx_DEVICE_jdcloud_re-ss-01=y',
    'CONFIG_TARGET_ROOTFS_INITRAMFS=n',
    'CONFIG_DEVEL=y',
    'CONFIG_FEED_video=n',
    'CONFIG_FEED_pon_drivers=n',
    'CONFIG_FEED_pon_userspace=n',
    'CONFIG_LUCI_LANG_zh_Hans=y',
    'CONFIG_PACKAGE_luci=y',
    'CONFIG_PACKAGE_luci-theme-bootstrap=y',
    'CONFIG_PACKAGE_luci-compat=y',
    'CONFIG_PACKAGE_luci-app-attendedsysupgrade=n',
    'CONFIG_PACKAGE_kmod-tun=y',
    'CONFIG_PACKAGE_kmod-nft-tproxy=y',
    'CONFIG_PACKAGE_kmod-nft-socket=y',
    'CONFIG_PACKAGE_kmod-inet-diag=y',
    'CONFIG_PACKAGE_ip-full=y',
    'CONFIG_PACKAGE_dnsmasq=n',
    'CONFIG_PACKAGE_dnsmasq-full=y',
    'CONFIG_PACKAGE_curl=y',
    'CONFIG_PACKAGE_ca-bundle=y',
    'CONFIG_PACKAGE_openssh-sftp-server=y',
    'CONFIG_PACKAGE_sgdisk=y',
    'CONFIG_PACKAGE_lsblk=y',
    'CONFIG_PACKAGE_block-mount=y',
    'CONFIG_PACKAGE_e2fsprogs=y',
    'CONFIG_PACKAGE_kmod-fs-ext4=y',
    'CONFIG_PACKAGE_luci-app-passwall=n',
]
for feature, packages in features.items():
    for package in packages:
        lines.append(f'CONFIG_PACKAGE_{package}={"y" if enabled(feature) else "n"}')
if enabled('PASSWALL2'):
    lines += ['CONFIG_PACKAGE_luci-app-passwall2_Nftables_Transparent_Proxy=y', 'CONFIG_PACKAGE_luci-app-passwall2_INCLUDE_Xray=y']
ipv6 = 'y' if enabled('IPV6') else 'n'
lines += [f'CONFIG_IPV6={ipv6}', f'CONFIG_PACKAGE_odhcp6c={ipv6}', f'CONFIG_PACKAGE_odhcpd-ipv6only={ipv6}', f'CONFIG_PACKAGE_luci-proto-ipv6={ipv6}']
path.write_text('\n'.join(lines) + '\n')

# Compile Wi-Fi support for this 512 MiB device using upstream device defaults.
# Leave the initial wireless settings to LuCI; do not publish a user's credentials.
defaults = Path('files/etc/uci-defaults')
defaults.mkdir(parents=True, exist_ok=True)
service_defaults = defaults / '99-arthur-proxy-defaults'
service_defaults.write_text('#!/bin/sh\nfor service in openclash passwall2 homeproxy; do\n  [ ! -x "/etc/init.d/$service" ] || "/etc/init.d/$service" disable\ndone\nexit 0\n')
service_defaults.chmod(0o755)
print('Configured RE-SS-01; Wi-Fi retained; proxy autostart disabled')
