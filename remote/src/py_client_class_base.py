    ip_port = ('', port)

    s = socket.socket()

    def snd_rcv(self, snd_data):
        try:
            self.s.send(snd_data.get_buf())
            len_bytes = bytes()
            len_bytes = self.s.recv(size_of_ulong())
            data_len = to_unlong(len_bytes)
            if(data_len > max_rcv_len ):raise
            data_buf = self.s.recv(data_len)
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

