# client.py
import socket
import numpy as np
import PySimpleGUI as ps
import cv2
import pickle
import struct
import threading
import time
from datetime import datetime
import shutil
import os

class Server:
    def __init__(self, output_path, ip='127.0.0.1', port=3000):
        self.out_path = os.path.join(output_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        os.mkdir(self.out_path)
        self.begin = time.time()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((ip, port))
        self.sync()
        self.thrd = threading.Thread(target=self.listen)

        self.buffer = []
        self.bufnum = 0
        self.etime = 0

        self.empty = False
        self.save = False
        self.thrd.daemon = True
        self.thrd.start()


    def send(self, vals):
        bytes = str(vals).encode()
        self.socket.sendall(bytes)

    def receive(self):
        data = self.socket.recv(1024)
        return data.decode()

    def start(self):
        self.etime = self.get_time()
        self.empty = True
        self.save = True

    def end(self):
        self.save = False
        self.buffer2 = self.buffer
        time.sleep(1)
        self.buffer1 = self.buffer2
        self.save_buffer

    def sync(self):
        a0 = time.time() - self.begin
        self.send(a0)
        f0 = float(self.receive())
        a1 = time.time() - self.begin
        self.send(a1 - a0)
        self.begin += self.begin + 0.5 * a0 + 0.5 * a1
        self.size = pickle.loads(self.socket.recv(1024))

    def get_size(self):
        return self.size

    def get_time(self):
        return time.time() - self.begin

    def read_cur(self):
        return None if len(self.buffer) < 1 else \
            self.buffer[len(self.buffer)-1]

    def listen(self):
        print('h')
        while True:
            if self.empty:
                self.empty = False
                self.buffer = []

            message_size = self.socket.recv(struct.calcsize("L"))
            if not message_size:
                break
            message_size = struct.unpack("L", message_size)[0]

            data =b""
            while len(data) < message_size:
                packet = self.socket.recv(4096)
                if not packet:
                    break
                data += packet
            
            self.buffer.append(pickle.loads(data))
            self.buffer[len(self.buffer)-1][0] -= self.etime
            if (len(self.buffer) > 500):
                if self.save:
                    self.buffer1 = self.buffer
                    self.buffer = []
                    thr = threading.Thread(target= self.save_buffer)
                    thr.daemon = True
                    thr.start()
                else:
                    self.buffer = []

    def save_buffer(self):
        file = open(os.path.join(self.out_path, f'out{self.bufnum}'), 'wb')
        self.bufnum += 1
        pickle.dump(self.buffer1, file)
            
    

if __name__ == '__main__':
    layout = [[ps.Graph(canvas_size=(640, 480), graph_bottom_left=(0,0), graph_top_right=(640,480), key='out')]]

    window = ps.Window("Window", layout)
    gr = window['out']
    server = Server('out')
    while True:
        window.read(timeout=20)

        cur = server.read_cur()
        if cur is not None:
            imencode = cv2.imencode('.png', cur[1])[1].tobytes()
            gr.erase()
            gr.draw_image(data=imencode, location=(0, 480))
