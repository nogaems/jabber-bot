# coding: utf-8
import re
def work(sess, mess):
    nick=mess.getFrom().getResource()
    text=mess.getBody()
    if re.search(u'^ping$', text.lower()):
        return nick + ': ' + u'pong'
    else:
        return None


