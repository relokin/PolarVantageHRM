#!/usr/bin/env python3
#
# Copyright (c) 2021 Nikos Nikoleris
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# This tool captures Bluetooth Low-Energy Advertisements from Polar
# Vantage watches. It can detect Polar Vantage watches using the
# Complete Local Name advertisement unless the user provides the MAC
# address of the watch. It listens for Manufacturer specific
# advertisements which encode the heart rate.

import logging
import argparse
import time

from bluepy import btle

logging.basicConfig(format="%(asctime)s  %(message)s")
log = logging.getLogger("PolarVantageHR")
log.setLevel(logging.INFO)

class ScanDelegate(btle.DefaultDelegate):
    def __init__(self, mac=None):
        super(ScanDelegate, self).__init__()
        self.mac = mac

    def handleDiscovery(self, dev, _newDevice, _newData):
        if self.mac is not None and dev.addr != self.mac:
            return

        for (adtype, desc, value) in dev.getScanData():
            log.debug('Received {}({}): {}'.format(desc, adtype, value))
            if self.mac is None:
                # Find a Polar Vantage watch broadcasting
                if adtype == btle.ScanEntry.COMPLETE_LOCAL_NAME and \
                   value.startswith('Polar Vantage'):
                    self.mac = dev.addr
            elif adtype == btle.ScanEntry.MANUFACTURER:
                # Advertisements from Polar Vantage M (firmware
                # ver. 5.1.8) are of the form:
                #
                # 6b00720872acf50200000000XX00YY
                #
                # Where YY is the heart rate in hex. XX also encodes
                # something as it constantly changes but I haven't
                # been able to figure it out yet. Judging from other
                # HRMs from Polar it could be an indication of the
                # expended energy or the interval between two
                # measurements.
                assert(value.startswith('6b00720872acf50200000000'))
                bpm = int(value[-2:], 16)
                log.info('HR: {} bpm'.format(bpm))


def main():
    parser = argparse.ArgumentParser(
        description="BLE HR Monitor for Polar Vantage watches")
    parser.add_argument(
        "-m", metavar='MAC', type=str,
        help="MAC address of BLE device (default: auto-discovery)")
    args = parser.parse_args()
 
    scanner = btle.Scanner().withDelegate(ScanDelegate(args.m.lower()))
    while True:
        devices = []
        try:
            devices = scanner.scan()
            time.sleep(1)
        except btle.BTLEManagementError as e:
            logging.error(e)
        except btle.BTLEDisconnectError as e:
            logging.error(e)


if __name__ == "__main__":
    main()
