#
# SPDX-FileCopyrightText: The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

# Inherit from the proprietary version
include vendor/xiaomi/camera/BoardConfigVendor.mk

CAMERA_PATH := device/xiaomi/camera

# Properties
TARGET_SYSTEM_PROP += $(CAMERA_PATH)/system.prop

# Sepolicy
BOARD_VENDOR_SEPOLICY_DIRS += $(CAMERA_PATH)/sepolicy/vendor