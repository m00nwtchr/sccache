#!/usr/bin/env python

from __future__ import print_function

import glob
import io
import os
import subprocess
import sys
import tooltool

PLATFORM_MANIFESTS = {
    'Linux': ['linux32', 'linux64'],
    'Darwin': ['macosx64'],
    'MINGW32_NT-6.2': ['win32', 'win64'],
}

def indices(s, which):
    i = 0
    while True:
        i = s.find(which, i)
        if i == -1:
            return
        yield i
        i += 1

def rewrite_manifest_entry(manifest_file, manifest, index):
    old_data = open(manifest_file, 'rb').read()
    b = io.BytesIO()
    manifest.dump(b)
    new_data = b.getvalue().strip(' \n[]')
    start = list(indices(old_data, '{'))[index]
    end = old_data.index('}', start)
    with open(manifest_file, 'wb') as f:
        f.write(old_data[:start])
        f.write(new_data)
        f.write(old_data[end+1:])

def update_tooltool_manifests(build_dir, gecko_dir):
    system = os.path.basename(build_dir)
    new_manifest_file = os.path.join(build_dir, 'releng.manifest')
    manifest = tooltool.open_manifest(new_manifest_file)
    for platform in PLATFORM_MANIFESTS[system]:
        for platform_manifest_file in glob.glob(os.path.join(gecko_dir, 'browser/config/tooltool-manifests', platform, '*.manifest')):
            print(platform_manifest_file)
            platform_manifest = tooltool.open_manifest(platform_manifest_file)
            for i, f in enumerate(platform_manifest.file_records):
                if f.filename.startswith('sccache'):
                    platform_manifest.file_records[i] = manifest.file_records[0]
                    rewrite_manifest_entry(platform_manifest_file, manifest, i)
                    break
def main():
    if len(sys.argv) < 3:
        print("Usage: update-gecko-manifests.py <destination directory> <gecko clone>")
        sys.exit(1)
    dest_dir = sys.argv[1]
    gecko_dir = sys.argv[2]
    for d in os.listdir(dest_dir):
        update_tooltool_manifests(os.path.join(dest_dir, d), gecko_dir)

if __name__ == '__main__':
    main()

