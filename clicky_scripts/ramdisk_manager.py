import subprocess


# Attach disk of size ~10MB to /dev/disk?
# This size is number of 512-byte blocks, so "20480" is 2x1024*10
# hdiutil attach -nobrowse -nomount ram://20480
# Returns a /dev/disk? name
# Format this and mount the /dev/disk? name
# diskutil erasevolume HFS+ 'screenshot_ramdisk' /dev/disk?
# (takes a second)
# Now it's mounted.

def check_if_ramdisk_exists():
    pass

def create_ramdisk():
    pass

def remove_ramdisk():
    pass

def ramdisk_location():
    pass

