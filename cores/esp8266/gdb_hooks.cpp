/*
 gdb_hooks.c - Default (no-op) hooks for GDB Stub library
 Copyright (c) 2018 Ivan Grokhotkov.  All right reserved.

 This library is free software; you can redistribute it and/or
 modify it under the terms of the GNU Lesser General Public
 License as published by the Free Software Foundation; either
 version 2.1 of the License, or (at your option) any later version.

 This library is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Lesser General Public License for more details.

 You should have received a copy of the GNU Lesser General Public
 License along with this library; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
*/

#include "ets_sys.h"
#include "gdb_hooks.h"


extern "C" {

void __attribute__((weak)) ICACHE_RAM_ATTR gdb_init(void) {}
void __attribute__((weak)) ICACHE_RAM_ATTR gdb_do_break(void) {}
bool __attribute__((weak)) ICACHE_RAM_ATTR gdb_present(void) {
    return false;
}
bool __attribute__((weak)) ICACHE_RAM_ATTR gdbstub_has_putc1_control(void) {
    return false;
}
void __attribute__((weak)) ICACHE_RAM_ATTR gdbstub_set_putc1_callback(void (*)(char)) {}
bool __attribute__((weak)) ICACHE_RAM_ATTR gdbstub_has_uart_isr_control(void) {
    return false;
}
void __attribute__((weak)) ICACHE_RAM_ATTR gdbstub_set_uart_isr_callback(void (*)(void*, uint8_t), void*) {}
void __attribute__((weak)) ICACHE_RAM_ATTR gdbstub_write_char(char) {}
void __attribute__((weak)) ICACHE_RAM_ATTR gdbstub_write(const char*, size_t) {}

};
