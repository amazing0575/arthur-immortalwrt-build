import hashlib
import json
import os
import shutil
import struct
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
source, output = map(Path, sys.argv[1:3])
output.mkdir(parents=True, exist_ok=True)
images = list(source.glob('*jdcloud_re-ss-01*sysupgrade.bin'))
factories = list(source.glob('*jdcloud_re-ss-01*factory.bin'))
if len(images) != 1 or len(factories) != 1:
    raise SystemExit('Expected exactly one Arthur sysupgrade and factory image')
with tarfile.open(images[0]) as archive:
    members = {x.name.rsplit('/', 1)[-1]: x for x in archive.getmembers() if x.isfile()}
    kernel = members['kernel'].size
    root = members['root'].size
    if not members['root'].name.startswith('sysupgrade-jdcloud_re-ss-01/'):
        raise SystemExit('Wrong board in sysupgrade archive')
    root_bytes = archive.extractfile(members['root']).read()
factory = factories[0].read_bytes()
offset = 6 * 1024 * 1024
if factory[offset:offset+4] != b'hsqs':
    raise SystemExit('Factory rootfs is not at the expected 6 MiB offset')
actual_root = struct.unpack_from('<Q', root_bytes, 40)[0]
if factory[offset:offset+actual_root] != root_bytes[:actual_root]:
    raise SystemExit('Factory and sysupgrade rootfs differ')
if kernel > offset:
    raise SystemExit('Kernel exceeds the source device kernel size')
manifest_path = next(source.glob('*.manifest'))
manifest = manifest_path.read_text()
packages = {line.split(' - ', 1)[0] for line in manifest.splitlines() if ' - ' in line}
required = {'luci-app-openclash': 'OPENCLASH', 'luci-app-passwall2': 'PASSWALL2', 'luci-app-homeproxy': 'HOMEPROXY', 'luci-app-upnp': 'UPNP', 'luci-app-ddns': 'DDNS', 'luci-app-samba4': 'SAMBA'}
missing = [p for p, feature in required.items() if os.environ.get('OPT_' + feature, 'true') == 'true' and p not in packages]
if missing:
    raise SystemExit('Requested packages absent from final manifest: ' + ', '.join(missing))
for path in [*images, *factories, *source.glob('*.manifest'), *source.glob('*.buildinfo')]:
    shutil.copy2(path, output / path.name)
fits = root <= 60 * 1024 * 1024
report = dict(board='jdcloud_re-ss-01', kernel_bytes=kernel, rootfs_bytes=root, fits_existing_6M_60M_layout=fits, source_commit=os.environ.get('SOURCE_COMMIT'), selected={k: os.environ.get('OPT_' + k, 'true') for k in ['OPENCLASH', 'PASSWALL2', 'HOMEPROXY', 'IPV6', 'UPNP', 'DDNS', 'SAMBA']})
(output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
lines = ['JDCloud Arthur RE-SS-01 firmware', '', 'Build completed and images statically verified.', f'Kernel: {kernel / 1048576:.3f} MiB; rootfs: {root / 1048576:.3f} MiB.', 'Fits original 6+60 MiB partitions.' if fits else 'ROOTFS EXCEEDS ORIGINAL 60 MiB PARTITION: expand GPT before flashing.', 'Factory image: for compatible U-Boot firmware upload. Sysupgrade: for later compatible system upgrades.', 'LAN: upstream default 192.168.1.1. Set a password and configure Wi-Fi after first boot.', 'OpenClash, PassWall2 and HomeProxy are installed as selected; autostart is disabled. Enable one transparent proxy at a time.', 'No router password, proxy subscription or personal credentials are included.', 'Static verification does not constitute a router boot, Wi-Fi or proxy stability test.']
(output / 'RESULT.txt').write_text('\n'.join(lines) + '\n')
(output / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n' for p in sorted(output.glob('*.bin'))))
print('\n'.join(lines))
