import codecs
from collections import OrderedDict

import arrow
import serial


class Interface:
    serial = None
    modes = {
        5: "APP1.0A",
        7: "DCP1.5A"
    }

    def __init__(self, port):
        self.port = port

    def connect(self):
        if self.serial is None:
            self.serial = serial.Serial(port=self.port, baudrate=9600, timeout=3)

    def read(self):
        self.send("f0")
        data = self.serial.read(130)
        return self.parse(data)

    def send(self, value):
        self.serial.write(bytes.fromhex(value))

    def parse(self, data):
        if len(data) < 130:
            return None

        data = codecs.encode(data, "hex").decode("utf-8")

        result = OrderedDict()

        result["timestamp"] = arrow.now().timestamp
        result["voltage"] = int("0x" + data[4] + data[5] + data[6] + data[7], 0) / 100
        result["current"] = int("0x" + data[8] + data[9] + data[10] + data[11], 0) / 1000
        result["power"] = int("0x" + data[12] + data[13] + data[14] + data[15] + data[16] +
                              data[17] + data[18] + data[19], 0) / 1000
        result["temperature"] = int("0x" + data[20] + data[21] + data[22] + data[23], 0)
        result["data_plus"] = int("0x" + data[192] + data[193] + data[194] + data[195], 0) / 100
        result["data_minus"] = int("0x" + data[196] + data[197] + data[198] + data[199], 0) / 100
        result["mode_id"] = int("0x" + data[200] + data[201] + data[202] + data[203], 0)
        result["mode_name"] = None
        result["accumulated_current"] = int("0x" + data[204] + data[205] + data[206] + data[207] + data[208] +
                                            data[209] + data[210] + data[211], 0)
        result["accumulated_power"] = int("0x" + data[212] + data[213] + data[214] + data[215] + data[216] +
                                          data[217] + data[218] + data[219], 0)
        result["accumulated_time"] = int("0x" + data[224] + data[225] + data[226] + data[227] + data[228] +
                                         data[229] + data[230] + data[231], 0)
        result["resistance"] = int("0x" + data[244] + data[245] + data[246] + data[247] + data[248] +
                                   data[249] + data[250] + data[251], 0) / 10

        if result["mode_id"] in self.modes:
            result["mode_name"] = self.modes[result["mode_id"]]

        return result

    def close(self):
        if self.serial:
            self.serial.close()
