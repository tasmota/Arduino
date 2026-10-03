# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Arduino

Arduino Wiring-based Framework allows writing cross-platform software to
control devices attached to a wide range of Arduino boards to create all
kinds of creative coding, interactive objects, spaces or physical experiences.

https://arduino.cc/en/Reference/HomePage
"""

# Extends: https://github.com/platformio/platform-espressif8266/blob/develop/builder/main.py

import os
from os.path import isfile, isdir, join

from SCons import Util
from SCons.Script import Builder, DefaultEnvironment


def scons_patched_match_splitext(path, suffixes=None):
    """
    Patch SCons Builder, append $OBJSUFFIX to the end of each target
    """
    tokens = Util.splitext(path)
    if suffixes and tokens[1] and tokens[1] in suffixes:
        return (path, tokens[1])
    return tokens


Builder.match_splitext = scons_patched_match_splitext


env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
gzip_fw = board.get("build.gzip_fw", False)
gzip_switch = []

FRAMEWORK_DIR = platform.get_package_dir("framework-arduinoespressif8266")
assert isdir(FRAMEWORK_DIR)

TOOLCHAIN_DIR = platform.get_package_dir("toolchain-xtensa-esp8266")
assert isdir(TOOLCHAIN_DIR)

# GCC 16+ xtensa-esp-elf is a unified multi-target toolchain. The dynconfig
# plugin selects the ESP8266 configuration: little-endian byte order, correct
# multilib C++ headers, and target-specific ABI. Without it the compiler
# defaults to big-endian, which makes the linker refuse to merge object files
# with the little-endian pre-built SDK libraries.
dynconfig = join(TOOLCHAIN_DIR, "lib", "xtensa_esp8266.so")
DYNCONFIG_FLAGS = ["-mdynconfig=%s" % dynconfig] if isfile(dynconfig) else []

# Dynamically resolve the GCC version directory under the toolchain's C++
# include path so the build doesn't break when the toolchain is upgraded.
# The path looks like: <TOOLCHAIN_DIR>/xtensa-esp-elf/include/c++/<version>/
cxx_include_base = join(TOOLCHAIN_DIR, "xtensa-esp-elf", "include", "c++")
gcc_version = None
if os.path.isdir(cxx_include_base):
    candidates = sorted(
        d for d in os.listdir(cxx_include_base)
        if os.path.isdir(join(cxx_include_base, d))
    )
    if candidates:
        gcc_version = candidates[-1]  # pick the highest version present
GCC_VERSION = gcc_version

SDK_LIBC_PATH = join(FRAMEWORK_DIR, "tools", "sdk", "libc", "xtensa-lx106-elf", "lib")

if gzip_fw:
    gzip_switch = ["--gzip", "PIO"]

env.Append(
    ASFLAGS=[
        "-mlongcalls",
        "-mtext-section-literals",
        "-Wno-frame-address",
        "-fno-builtin-memcpy",
        "-fno-builtin-memset",
        "-fno-builtin-bzero",
    ],
    ASPPFLAGS=[
        "-Wno-frame-address",
        "-mlongcalls",
        "-fno-builtin-memcpy",
        "-fno-builtin-memset",
        "-fno-builtin-bzero",
        "-x", "assembler-with-cpp",
    ],

    # General options that are passed to the C compiler (C only; not C++)
    CFLAGS=[
        "-std=gnu17",
        "-Wpointer-arith",
        "-Wno-implicit-function-declaration",
        "-Wl,-EL",
        "-fno-inline-functions",
        "-nostdlib",
        "-Wno-frame-address",
        "-mlongcalls",
        "-fno-builtin-memcpy",
        "-fno-builtin-memset",
        "-fno-builtin-bzero",
        "-Wno-old-style-declaration",
        "-fzero-init-padding-bits=all",
        "-fno-malloc-dce",
        "-Wno-enum-int-mismatch",
    ],

    # General options that are passed to the C and C++ compilers
    CCFLAGS=[
        "-Os",  # optimize for size
        ] + DYNCONFIG_FLAGS + [
        "-mlongcalls",
        "-mtext-section-literals",
        "-falign-functions=4",
        "-U__STRICT_ANSI__",
        "-ffunction-sections",
        "-fdata-sections",
        "-fno-exceptions",
        "-Wall",
        "-Werror=return-type",
        "-free",
        "-fipa-pta",
        "-Wno-frame-address",
        "-fno-builtin-memcpy",
        "-fno-builtin-memset",
        "-fno-builtin-bzero",
        "-Wno-error=unused-function",
        "-Wno-error=unused-variable",
        "-Wno-error=unused-but-set-variable",
        "-Wno-error=deprecated-declarations",
        "-Wno-error=extra",
        "-Wno-unused-parameter",
        "-Wno-sign-compare",
        "-Wno-enum-conversion",
        "-gdwarf-4",
        "-ggdb",
        "-freorder-blocks",
        "-mno-target-align",
        "-Wno-address",
        "-Wno-use-after-free",
        "-Wno-xor-used-as-pow",
        "-Wno-calloc-transposed-args",
        "-fstrict-volatile-bitfields",
        "-fno-jump-tables",
        "-fno-tree-switch-conversion",
        "-MMD",
    ],

    # General options that are passed to the C++ compiler
    CXXFLAGS=[
        "-Wno-register",
        "-fno-rtti",
        "-fno-sized-deallocation",
        "-std=gnu++17",
        "-fno-exceptions",
        "-Wno-self-move",
        "-Wno-dangling-reference",
        # GCC 15+ xtensa-esp-elf toolchain: gthr-default.h is the POSIX threads
        # variant; the ESP8266 bare-metal sysroot's pthread.h provides no types
        # without _POSIX_THREADS. Pre-define the posix gthr guard and force-include
        # the no-op single-thread stub so the full C++ library header chain works.
        "-D_GLIBCXX_GCC_GTHR_POSIX_H",
        "-include", join(TOOLCHAIN_DIR, "xtensa-esp-elf", "include", "c++",
                         GCC_VERSION, "xtensa-esp-elf", "bits", "gthr-single.h"),
    ],

    LINKFLAGS=[
        "-Os",
        ] + DYNCONFIG_FLAGS + [
        "-nostdlib",
        "-Wno-frame-address",
        "-mlongcalls",
        "-fno-builtin-memcpy",
        "-fno-builtin-memset",
        "-fno-builtin-bzero",
        "-nostartfiles",
        "-fno-rtti",
        "-Wl,-no-warn-rwx-segments",
        "-Wl,--no-check-sections",
        "-Wl,-static",
        "-Wl,--gc-sections",
        "-Wl,-wrap,system_restart_local",
        "-Wl,-wrap,spi_flash_read",
        "-u", "app_entry",
        "-u", "_DebugExceptionVector",
        "-u", "_DoubleExceptionVector",
        "-u", "_KernelExceptionVector",
        "-u", "_NMIExceptionVector",
        "-u", "_UserExceptionVector",
    ],

    CPPDEFINES=[
        ("F_CPU", "$BOARD_F_CPU"),
        "__ets__",
        "ICACHE_FLASH",
        ("ARDUINO", 10805),
        ("ARDUINO_BOARD", '\\"PLATFORMIO_%s\\"' % env.BoardConfig().id.upper()),
        "FLASHMODE_${BOARD_FLASH_MODE.upper()}",
        "LWIP_OPEN_SRC"
    ],

    CPPPATH=[
        join(FRAMEWORK_DIR, "tools", "sdk", "include"),
        join(FRAMEWORK_DIR, "tools", "sdk", "libc",
             "xtensa-lx106-elf", "include"),
        join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"))
    ],

    LIBPATH=[SDK_LIBC_PATH] + [
        join("$BUILD_DIR", "ld"),  # eagle.app.v6.common.ld
        join(FRAMEWORK_DIR, "tools", "sdk", "lib"),
        join(FRAMEWORK_DIR, "tools", "sdk", "ld")
    ],

    LIBS=[
        "hal", "phy", "pp", "net80211", "wpa", "crypto", "main",
        "wps", "bearssl", "espnow", "smartconfig", "airkiss", "wpa2",
        "stdc++", "m", "c", "gcc"
    ],

    LIBSOURCE_DIRS=[
        join(FRAMEWORK_DIR, "libraries")
    ],

    BUILDERS=dict(
        ElfToBin=Builder(
            action=env.VerboseAction(" ".join([
                '"$PYTHONEXE"',
                '"%s"' % join(FRAMEWORK_DIR, "tools", "elf2bin.py"),
                "--eboot", '"%s"' % join(
                    FRAMEWORK_DIR, "bootloaders", "eboot", "eboot.elf"),
                "--app", "$SOURCE",
                "--flash_mode", "$BOARD_FLASH_MODE",
                "--flash_freq", "${__get_board_f_flash(__env__)}",
                "--flash_size", "${__get_flash_size(__env__)}",
                "--path", '"%s"' % join(TOOLCHAIN_DIR, "bin"),
                "--out", "$TARGET"
            ] + gzip_switch), "Building $TARGET"),
            suffix=".bin"
        )
    )
)

# copy CCFLAGS to ASFLAGS (-x assembler-with-cpp mode)
env.Append(ASFLAGS=env.get("CCFLAGS", [])[:])

flatten_cppdefines = env.Flatten(env['CPPDEFINES'])

#
# SDK
#
if "PIO_FRAMEWORK_ARDUINO_ESPRESSIF_SDK3" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("NONOSDK3V0", 1)],
        LIBPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lib", "NONOSDK3V0")]
    )
elif "PIO_FRAMEWORK_ARDUINO_ESPRESSIF_SDK221" in flatten_cppdefines:
    #(previous default)
    env.Append(
        CPPDEFINES=[("NONOSDK221", 1)],
        LIBPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lib", "NONOSDK221")]
    )
elif "PIO_FRAMEWORK_ARDUINO_ESPRESSIF_SDK22x_190313" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("NONOSDK22x_190313", 1)],
        LIBPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lib", "NONOSDK22x_190313")]
    )
elif "PIO_FRAMEWORK_ARDUINO_ESPRESSIF_SDK22x_191024" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("NONOSDK22x_191024", 1)],
        LIBPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lib", "NONOSDK22x_191024")]
    )
elif "PIO_FRAMEWORK_ARDUINO_ESPRESSIF_SDK22x_191105" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("NONOSDK22x_191105", 1)],
        LIBPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lib", "NONOSDK22x_191105")]
    )
elif "PIO_FRAMEWORK_ARDUINO_ESPRESSIF_SDK22x_191122" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("NONOSDK22x_191122", 1)],
        LIBPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lib", "NONOSDK22x_191122")]
    )
else: #(default) if "PIO_FRAMEWORK_ARDUINO_ESPRESSIF_SDK22x_190703" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("NONOSDK22x_190703", 1)],
        LIBPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lib", "NONOSDK22x_190703")]
    )

#
# lwIP
#
if "PIO_FRAMEWORK_ARDUINO_LWIP2_IPV6_LOW_MEMORY" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("TCP_MSS", 536), ("LWIP_FEATURES", 1), ("LWIP_IPV6", 1)],
        CPPPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lwip2", "include")],
        LIBS=["lwip6-536-feat"]
    )
elif "PIO_FRAMEWORK_ARDUINO_LWIP2_IPV6_HIGHER_BANDWIDTH" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("TCP_MSS", 1460), ("LWIP_FEATURES", 1), ("LWIP_IPV6", 1)],
        CPPPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lwip2", "include")],
        LIBS=["lwip6-1460-feat"]
    )
elif "PIO_FRAMEWORK_ARDUINO_LWIP2_HIGHER_BANDWIDTH" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("TCP_MSS", 1460), ("LWIP_FEATURES", 1), ("LWIP_IPV6", 0)],
        CPPPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lwip2", "include")],
        LIBS=["lwip2-1460-feat"]
    )
elif "PIO_FRAMEWORK_ARDUINO_LWIP2_LOW_MEMORY_LOW_FLASH" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("TCP_MSS", 536), ("LWIP_FEATURES", 0), ("LWIP_IPV6", 0)],
        CPPPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lwip2", "include")],
        LIBS=["lwip2-536"]
    )
elif "PIO_FRAMEWORK_ARDUINO_LWIP2_HIGHER_BANDWIDTH_LOW_FLASH" in flatten_cppdefines:
    env.Append(
        CPPDEFINES=[("TCP_MSS", 1460), ("LWIP_FEATURES", 0), ("LWIP_IPV6", 0)],
        CPPPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lwip2", "include")],
        LIBS=["lwip2-1460"]
    )
# PIO_FRAMEWORK_ARDUINO_LWIP2_LOW_MEMORY (default)
else:
    env.Append(
        CPPDEFINES=[("TCP_MSS", 536), ("LWIP_FEATURES", 1), ("LWIP_IPV6", 0)],
        CPPPATH=[join(FRAMEWORK_DIR, "tools", "sdk", "lwip2", "include")],
        LIBS=["lwip2-536-feat"]
    )

#
# Waveform
#
if "PIO_FRAMEWORK_ARDUINO_WAVEFORM_LOCKED_PHASE" in flatten_cppdefines:
    env.Append(CPPDEFINES=[("WAVEFORM_LOCKED_PHASE", 1)])
# PIO_FRAMEWORK_ARDUINO_WAVEFORM_LOCKED_PWM will be used by default

#
# VTables
#

current_vtables = None
fp_in_irom = ""
for d in flatten_cppdefines:
    if str(d).startswith("VTABLES_IN_"):
        current_vtables = d
    if str(d) == "FP_IN_IROM":
        fp_in_irom = "-DFP_IN_IROM"
if not current_vtables:
    current_vtables = "VTABLES_IN_FLASH"
    env.Append(CPPDEFINES=[current_vtables])
assert current_vtables

# Build the eagle.app.v6.common.ld linker file
app_ld = env.Command(
    join("$BUILD_DIR", "ld", "local.eagle.app.v6.common.ld"),
    join(FRAMEWORK_DIR, "tools", "sdk", "ld", "eagle.app.v6.common.ld.h"),
    env.VerboseAction(
        "$CC -CC -E -P -D%s %s $SOURCE -o $TARGET" % (current_vtables, fp_in_irom),
        "Generating LD script $TARGET"))
env.Depends("$BUILD_DIR/$PROGNAME$PROGSUFFIX", app_ld)

if not env.BoardConfig().get("build.ldscript", ""):
    env.Replace(LDSCRIPT_PATH=env.BoardConfig().get("build.arduino.ldscript", "")) 

#
# Dynamic core_version.h for staging builds
#

def platform_txt_version(default):
    with open(join(FRAMEWORK_DIR, "platform.txt"), "r") as platform_txt:
        for line in platform_txt:
            if not line:
                continue
            k, delim, v = line.partition("=")
            if not delim:
                continue
            if k == "version":
                return v.strip()

    return default

if isdir(join(FRAMEWORK_DIR, ".git")):
    cmd = '"$PYTHONEXE" "{script}" -b "$BUILD_DIR" -p "{framework_dir}" -v {version}'
    fmt = {
        "script": join(FRAMEWORK_DIR, "tools", "makecorever.py"),
        "framework_dir": FRAMEWORK_DIR,
        "version": platform_txt_version("unspecified")
    }

    env.Prepend(CPPPATH=[
        join("$BUILD_DIR", "core")
    ])
    core_version = env.Command(
        join("$BUILD_DIR", "core", "core_version.h"),
        join(FRAMEWORK_DIR, ".git"),
        env.VerboseAction(cmd.format(**fmt), "Generating $TARGET")
    )
    env.Depends("$BUILD_DIR/$PROGNAME$PROGSUFFIX", core_version)


#
# Target: Build Core Library
#

libs = []

if "build.variant" in env.BoardConfig():
    env.Append(
        CPPPATH=[
            join(FRAMEWORK_DIR, "variants",
                 env.BoardConfig().get("build.variant"))
        ]
    )
    libs.append(env.BuildLibrary(
        join("$BUILD_DIR", "FrameworkArduinoVariant"),
        join(FRAMEWORK_DIR, "variants", env.BoardConfig().get("build.variant"))
    ))

libs.append(env.BuildLibrary(
    join("$BUILD_DIR", "FrameworkArduino"),
    join(FRAMEWORK_DIR, "cores", env.BoardConfig().get("build.core"))
))

env.Prepend(LIBS=libs)
