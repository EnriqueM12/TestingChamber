from Client import Server
import pickle
import threading
import os
import time
from datetime import datetime
import cv2

class Experiment:
    def __init__(self, output_path):
        self.out_path = os.path.join(output_path, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        os.mkdir(self.out_path)
        self.buffer = []
        self.bufnum = 0
        self.buffer1 = []
        self.cap = cv2.VideoCapture(2)
        self.save = False
        self.empty = False
        self.begin = time.time()

        self.thr = threading.Thread(target=self.listen)
        self.thr.daemon = True
        self.thr.start()

    def get_size(self):
        return (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def start(self):
        self.empty = True
        self.save = True
        self.begin = time.time()
        self.server.start()

    def stop(self):
        self.save = False
        tq = threading.Thread(target=self.server.end)
        tq.daemon = True
        tq.start()
        self.buffer2 = self.buffer
        time.sleep(1)
        self.buffer1 = self.buffer2
        self.save_buffer()


    def read_cur(self):
        return None if len(self.buffer) < 1 else \
            self.buffer[len(self.buffer)-1]
        

    def listen(self):
        self.buffer = []
        while True:
            if self.empty:
                self.buffer = []
                self.empty = False

            tt = time.time() - self.begin
            ret, data = self.cap.read()
            data = [tt, data]
            self.buffer.append(data)

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

    def sync(self, ser: Server):
        self.server = ser
        self.begin = time.time()
        self.servtime = ser.get_time() 
