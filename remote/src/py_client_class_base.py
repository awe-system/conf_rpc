    def __init__(self):
        self.ip_port = ('', port)
        self.s = socket.socket()

    def snd_rcv(self, snd_data):
        try:
            self.s.send(snd_data.get_buf())
            len_bytes = self.s.recv(size_of_ulong())
            data_len = to_ulong(len_bytes)
            if (data_len > max_rcv_len): raise
            data_buf = self.s.recv(data_len)
            while (len(data_buf) != data_len):
                this_buf = self.s.recv(data_len - len(data_buf))
                data_buf += this_buf

            recv_data = lt_data_t()
            recv_data.from_len_buf(data_len, data_buf)
            return recv_data
        except:
            raise

    def connect(self, _ip):
        self.ip_port = (_ip, port)
        self.s.connect(self.ip_port)

    def disconnect(self):
        self.s.close()

