#
# Copyright (c) 2024 Analog Devices Inc.
#
# This file is part of libm2k
# (see http://www.github.com/analogdevicesinc/libm2k).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2.1 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
Requirements: x1 ADALM2000

This example assumes the following connections:
    W1      ->    1+
    W2      ->    2+
    GND     ->    1-
    GND     ->    2-
    DIO_0   ->    TI

This demo application generates a rising ramp signal on both output channels, W1 and W2. 
The generated signal is then fed back into the analog input channels for further analysis or processing.
This rising edge is generated using the DIO_0  pin but could be generated from an external source.

Rearm functionality:
    - Rearm mode allows the buffer to be automatically rearmed after each trigger event.

    - In cyclic mode, each trigger event sends the buffer to the DACs for one complete cycle. 
    After the cycle completes, the system waits for the next trigger event to resend the buffer.
    If rearm is not configured, the initial trigger event starts a continuous cyclic waveform, 
    which runs until manually stopped or reset.
"""

import time
import libm2k
import numpy as np
import matplotlib.pyplot as plt

# NOTE: change to see the effect of rearm on cyclic buffers
WITH_REARM = False

DAC_SR = 75_000_000
INPUT_BUFFER_SIZE = 20_000
DELAY = 8192
TRIGGER_THRESHOLD = 1
N_SAMPLES = 1024
AMPLITUDE = 5


def main():
    try:
        context: libm2k.M2k = libm2k.m2kOpen("ip:192.168.2.1")
        if context is None:
            print("Connection Error: No ADALM2000 device available/connected to your PC.")
            exit(1)

        ain: libm2k.M2kAnalogIn = context.getAnalogIn()
        aout: libm2k.M2kAnalogOut = context.getAnalogOut()
        dig: libm2k.M2kDigital = context.getDigital()
        trig: libm2k.M2kHardwareTrigger = ain.getTrigger()

        # Prevent bad initial configuration
        context.reset()
        context.calibrateADC()
        context.calibrateDAC()
        context.setTimeout(10_000)  # [ms]

        ain.setSampleRate(100_000_000)
        ain.enableChannel(libm2k.ANALOG_IN_CHANNEL_1, True)
        ain.enableChannel(libm2k.ANALOG_IN_CHANNEL_2, True)

        aout.setSampleRate(0, DAC_SR)
        aout.setSampleRate(1, DAC_SR)
        aout.enableChannel(0, True)
        aout.enableChannel(1, True)
        aout.setCyclic(True)

        dig.setSampleRateOut(100_000_000)
        dig.setDirection(libm2k.DIO_CHANNEL_0, libm2k.DIO_OUTPUT)
        dig.setOutputMode(libm2k.DIO_CHANNEL_0, libm2k.DIO_PUSHPULL)
        dig.setValueRaw(libm2k.DIO_CHANNEL_0, libm2k.LOW)
        dig.enableChannel(libm2k.DIO_CHANNEL_0, True)

        # ain acquisition trigger
        trig.setAnalogSource(libm2k.ANALOG_IN_CHANNEL_1)
        trig.setAnalogCondition(libm2k.ANALOG_IN_CHANNEL_1, libm2k.RISING_EDGE_ANALOG)
        trig.setAnalogLevel(libm2k.ANALOG_IN_CHANNEL_1, TRIGGER_THRESHOLD)
        trig.setAnalogDelay(-DELAY)
        trig.setAnalogMode(libm2k.ANALOG_IN_CHANNEL_1, libm2k.ANALOG)
        trig.setAnalogMode(libm2k.ANALOG_IN_CHANNEL_1, libm2k.ANALOG)

        # aout triggering: starts when the TI pin is triggered
        trig.setAnalogOutTriggerSource(libm2k.TRIGGER_TI)
        trig.setAnalogOutTriggerCondition(libm2k.RISING_EDGE_OUT)
        trig.setAnalogOutTriggerStatus(libm2k.START)
        aout.setBufferRearmOnTrigger(WITH_REARM)

        print("Starting acquisition ...")
        ain.startAcquisition(INPUT_BUFFER_SIZE)

        print("Sending waveform to DAC ...")
        rising_ramp = AMPLITUDE * (np.linspace(-1, 1, N_SAMPLES))
        aout.push([rising_ramp, rising_ramp])

        for _ in range(4 if WITH_REARM else 1):
            print("Waiting for trigger ...")
            time.sleep(0.5)

            print("Sending trigger event ...")
            dig.setValueRaw(libm2k.DIO_CHANNEL_0, libm2k.HIGH)

            data = np.array(ain.getSamples(INPUT_BUFFER_SIZE))
            time_axis = np.linspace(0, len(data[0]) / ain.getSampleRate(), len(data[0])) * 1e6
            plt.plot(time_axis, data[0], label="W1")
            plt.plot(time_axis, data[1], label="W2")
            plt.xlabel("Time [us]")
            plt.ylabel("Voltage [V]")
            plt.legend(loc="upper right")
            plt.grid(True)
            plt.show()

            dig.setValueRaw(libm2k.DIO_CHANNEL_0, libm2k.LOW)
    except Exception as e:
        print("Timeout occurred ... No trigger event detected")
        print(e)

    libm2k.contextClose(context)


if __name__ == '__main__':
    main()
