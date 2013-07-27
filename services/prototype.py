# coding: utf-8
import thread
import time

class Service:
    def __init__(self):
        thread.start_new_thread(self.Process, ())

    def Process(self):
        while True:
            time.sleep(100)

    def work(self, sess, mess):
        pass


