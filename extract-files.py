#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

import os
import shutil

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/xiaomi/miuicamera-sapphire',
]


def lib_fixup_system_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'system' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    'vendor.xiaomi.hardware.campostproc@1.0': lib_fixup_system_suffix,
}

def patch_camera_icon(ctx, file, file_path, *args, tmp_dir=None, **kwargs):
    if not tmp_dir:
        return
    icon_base = os.path.join(ctx.module_dir, 'icon')
    if not os.path.isdir(icon_base):
        return
    for root, _, files in os.walk(icon_base):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), icon_base)
            target = os.path.join(tmp_dir, 'res', rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(os.path.join(root, f), target)


blob_fixups: blob_fixups_user_type = {
    'system/lib64/libcamera_algoup_jni.xiaomi.so': blob_fixup()
        .add_needed('libgui_shim_miuicamera.so')
        .sig_replace('08 AD 40 F9', '08 A9 40 F9'),
    'system/lib64/libcamera_mianode_jni.xiaomi.so': blob_fixup()
        .add_needed('libgui_shim_miuicamera.so'),
    'system/lib64/libmicampostproc_client.so': blob_fixup()
        .remove_needed('libhidltransport.so'),
    'system/priv-app/MiuiCamera/MiuiCamera.apk': blob_fixup()
        .apktool_unpack('patches')
        .patch_dir('patches')
        .call(patch_camera_icon)
        .apktool_pack()
        .stripzip(),
    'vendor/lib64/camera/components/com.jigan.node.realtimebokeh.so': blob_fixup()
        .sig_replace('B1 02 40 B9 0A 02 11 6B 23 09 00 54',
                     'B1 02 40 B9 0A 02 11 6B 1F 20 03 D5')
        .sig_replace('B6 06 40 B9 0C 00 16 6B A3 08 00 54',
                     'B6 06 40 B9 0C 00 16 6B 1F 20 03 D5')
        .sig_replace('3F C1 29 EB 61 08 00 54',
                     '3F C1 29 EB 1F 20 03 D5')
        .sig_replace('6B 01 01 6B E6 07 00 54',
                     '6B 01 01 6B 1F 20 03 D5')
        .sig_replace('DF 7D 60 F2 61 07 00 54',
                     'DF 7D 60 F2 1F 20 03 D5')
        .sig_replace('C0 03 5F D6 E5 0A 00 94 D4 0A 00 94',
                     'C0 03 5F D6 F9 FF FF 17 F8 FF FF 17'),
}  # fmt: skip

module = ExtractUtilsModule(
    'miuicamera-sapphire',
    'xiaomi',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    # Pre-processing hook to combine split MiuiCamera chunks from the dump source before extraction
    import sys
    src_path = sys.argv[1] if len(sys.argv) > 1 else None
    if src_path:
        split_dir = os.path.join(src_path, 'product', 'priv-app', 'MiuiCamera')
        target_apk = os.path.join(split_dir, 'MiuiCamera.apk')
        chunk_aa = os.path.join(split_dir, 'MiuiCamera.apk.aa')
        
        if os.path.exists(chunk_aa) and not os.path.exists(target_apk):
            print("Recombining split MiuiCamera chunks from dump directory...")
            with open(target_apk, 'wb') as outfile:
                for suffix in ['aa', 'ab', 'ac', 'ad']:
                    chunk_file = os.path.join(split_dir, f'MiuiCamera.apk.{suffix}')
                    if os.path.exists(chunk_file):
                        with open(chunk_file, 'rb') as infile:
                            shutil.copyfileobj(infile, outfile)
            print("Successfully recombined MiuiCamera.apk for extraction.")

    utils = ExtractUtils.device(module)
    utils.run()