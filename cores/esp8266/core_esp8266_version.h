
/*
 core_esp8266_version.h - parse "git describe" at compile time
 Copyright (c) 2018 david gauchard. All rights reserved.
 This file is part of the esp8266 core for Arduino environment.

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

#ifndef __CORE_ESP8266_VERSION_H
#define __CORE_ESP8266_VERSION_H

#define HAS_ESP8266_VERSION_NUMERIC 1

#include <core_version.h>

#define __STRHELPER(x) #x
#define __STR(x) __STRHELPER(x)

#ifdef __cplusplus
extern "C++"
{

// Following constexpr functions are compiled and executed
// *after* pre-processing and *during* compilation
//
// Their result is treated like a numeric constant in final binary code.
// git tags must be in the form:
// - <major>.<minor>.<revision>       (2.4.2) (2.5.0)
// - <major>.<minor>.<revision>-rc<rc> (2.5.0-rc1) (2.5.0-rc2)
//
// "git describe" = ARDUINO_ESP8266_GIT_DESC will thus be in the form:
// - <tag> (2.4.2) (2.5.0)
// - <tag>-<numberOfCommits>-g<git-hash> (2.4.2-91-gcb05b86d) (2.5.0-rc3-1-gcb05b86d)
//
// Examples:
// case 2.4.2 (fresh version/tag)
//     esp8266CoreVersionSubRevision() is 0   Numeric is: 20402000
// case 2.4.2-91-gcb05b86d:
//     esp8266CoreVersionSubRevision() is -91 Numeric is: 20402091
// case 2.5.0-rc3-1-gcb05b86d:
//     esp8266CoreVersionSubRevision() is 3   Numeric is: 20499903
// case 2.5.0:
//     esp8266CoreVersionSubRevision() is 0   Numeric is: 20500000
//
// Using esp8266::coreVersionNumeric() in a portable way:
//
//   #if HAS_ESP8266_VERSION_NUMERIC
//       if (esp8266::coreVersionNumeric() >= 20500042)
//       {
//           // modern api can be used
//       }
//       else
//   #endif
//       {
//           // code using older api
//           // (will not be compiled in when newer api is usable)
//       }

namespace conststr {

constexpr
bool isDecimal (const char c)
{
    return c >= '0' && c <= '9';
}

template<unsigned N> constexpr
bool isMinus (const char (&arr) [N], unsigned i)
{
    return arr[i] == '-' && isDecimal(arr[i+1]);
}

// atoi: recursive C++11 constexpr (accumulates digits)
template<unsigned N> constexpr
int atoiAcc (const char (&arr) [N], unsigned i, int acc)
{
    return isDecimal(arr[i]) ? atoiAcc(arr, i+1, acc*10 + arr[i] - '0') : acc;
}

template<unsigned N> constexpr
int atoi (const char (&arr) [N], unsigned i)
{
    return arr[i] == '-' ? -atoiAcc(arr, i+1, 0) : atoiAcc(arr, i, 0);
}

// skipDigits: advance past a run of decimal digits
template<unsigned N> constexpr
unsigned skipDigits (const char (&arr) [N], unsigned i)
{
    return isDecimal(arr[i]) ? skipDigits(arr, i+1) : i;
}

// skipNonToken: advance past characters that are neither a digit nor a '-<digit>' pair
template<unsigned N> constexpr
unsigned skipNonToken (const char (&arr) [N], unsigned i)
{
    return (arr[i] && !isMinus(arr, i) && !isDecimal(arr[i]))
               ? skipNonToken(arr, i+1) : i;
}

// findNthToken: locate the start index of the f-th integer token
template<unsigned N> constexpr
unsigned findNthToken (const char (&arr) [N], unsigned i, unsigned f)
{
    return (f == 0 || !arr[i])
               ? i
               : findNthToken(arr,
                              skipNonToken(arr,
                                           skipDigits(arr,
                                                      isMinus(arr, i) ? i+1 : i)),
                              f-1);
}

template<unsigned N> constexpr
int parseNthInteger (const char (&arr) [N], unsigned f)
{
    return atoi(arr, findNthToken(arr, 0, f));
}

}; // namespace conststr

namespace esp8266 {

/*
 * version major
 */
constexpr
int coreVersionMajor ()
{
    return conststr::parseNthInteger(__STR(ARDUINO_ESP8266_GIT_DESC), 0);
}

/*
 * version minor
 */
constexpr
int coreVersionMinor ()
{
    return conststr::parseNthInteger(__STR(ARDUINO_ESP8266_GIT_DESC), 1);
}

/*
 * version revision
 */
constexpr
int coreVersionRevision ()
{
    return conststr::parseNthInteger(__STR(ARDUINO_ESP8266_GIT_DESC), 2);
}

/*
 * git commit number since last tag (negative)
 * or RC-number (positive)
 */
constexpr
int coreVersionSubRevision ()
{
    return conststr::parseNthInteger(__STR(ARDUINO_ESP8266_GIT_DESC), 3);
}

/*
 * unique revision indentifier (never decreases)
 */
constexpr
int coreVersionNumeric ()
{
    return   coreVersionMajor()    * 10000000
           + coreVersionMinor()    *   100000
           + coreVersionRevision() *     1000
           + (coreVersionSubRevision() < 0 ?
               -coreVersionSubRevision() :
               coreVersionSubRevision() ?
                 coreVersionSubRevision() - 100 :
                 0);
}

}; // namespace esp8266

} // extern "C++"
#endif // __cplusplus
#endif // __CORE_ESP8266_ESP8266_VERSION_H
