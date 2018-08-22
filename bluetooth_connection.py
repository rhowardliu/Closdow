import bluetooth


class BlueToothConnection:


    def __init__(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.window_bluetooth_dic = {'bedroom_one': '98:D3:31:F5:23:16', }
        self.window_port_dic = {'bedroom_one': 1}
        for key, values in self.window_bluetooth_dic.items():
            self.socket.connect(values, self.window_port_dic[key])

    def open(self):
        self.socket.send(b'o')

    def close(self):
        self.socket.send(b'c')

    def setchildlock(self):
        self.socket.send(b'l')

    def disable_child_lock(self):
        self.socket.send(b'u')

