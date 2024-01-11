Platformio Tasmota Arduino core for ESP8266 [![GitHub Releases](https://img.shields.io/github/downloads/tasmota/Arduino/total?label=downloads)](https://github.com/tasmota/Arduino/releases/latest)
==========================================

### This fork can only be used with PlatformIO

[PlatformIO](https://platformio.org?utm_source=arduino-esp8266) is an open source ecosystem for IoT
development with a cross-platform build system, a library manager, and full support
for Espressif (ESP8266) development. It works on the following popular host operating systems: macOS, Windows,
Linux 32/64, and Linux ARM (like Raspberry Pi, BeagleBone, CubieBoard).

- [What is PlatformIO?](https://docs.platformio.org/en/latest/what-is-platformio.html?utm_source=arduino-esp8266)
- [PlatformIO IDE](https://platformio.org/platformio-ide?utm_source=arduino-esp8266)
- [PlatformIO Core](https://docs.platformio.org/en/latest/core.html?utm_source=arduino-esp8266) (command line tool)

### License and credits ###

ESP8266 core includes an xtensa gcc toolchain, which is also under GPL.

[Espressif's NONOS SDK](https://github.com/espressif/ESP8266_NONOS_SDK) included in this build is under Espressif MIT License.

ESP8266 core files are licensed under LGPL.

[umm_malloc](https://github.com/rhempel/umm_malloc) memory management library written by Ralph Hempel is used in this project. It is distributed under the MIT license.

[BearSSL](https://bearssl.org) library written by Thomas Pornin, built from https://github.com/earlephilhower/bearssl-esp8266, is used in this project.  It is distributed under the [MIT License](https://bearssl.org/#legal-details).

[LittleFS](https://github.com/ARMmbed/littlefs) library written by ARM Limited and released under the [BSD 3-clause license](https://github.com/ARMmbed/littlefs/blob/master/LICENSE.md).

[uzlib](https://github.com/pfalcon/uzlib) library written and (c) 2014-2018 Paul Sokolovsky, licensed under the ZLib license (https://www.zlib.net/zlib_license.html). uzlib is based on: tinf library by Joergen Ibsen (Deflate decompression); Deflate Static Huffman tree routines by Simon Tatham; LZ77 compressor by Paul Sokolovsky; with library integrated and maintained by Paul Sokolovsky.
