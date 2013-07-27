# coding: utf-8
import prototype
import time
import re

class Service(prototype.Service):
    mess_count = 0
    today = time.ctime().split(' ')[2]
    log = open('logfile.txt', 'a')
    log.write(time.ctime() + '\n')

    def work(self, sess, mess):
        nick = mess.getFrom().getResource()
        text = mess.getBody()
        self.mess_count += 1
        c_time = time.ctime().split(' ')
        if c_time[2] != self.today:
            self.log.write('{0}\n({1}) {2}: {3}\n'.format(' '.join(c_time), c_time[3], nick.encode('utf8'), text.encode('utf8')))
            self.today = time.ctime().split(' ')[2]
            self.mess_count = 0
        else:
            self.log.write('{0} {1}: {2}\n'.format(c_time[3], nick.encode('utf8'), text.encode('utf8')))
        self.log.flush()
        if re.search(u'^how many messages$', text) is not None:
            return nick + u': Today the messages posted: ' + str(self.mess_count)
        else:
            return None
