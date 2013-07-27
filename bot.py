# coding: utf-8
import xmpp
import modules
import services
import imp
import thread
import os
import re
import time
import sys

class BotConfig:
    def __init__(self, config_file='config.py'):
        config_module_name = config_file[:-3]
        if imp.find_module(config_module_name):
            import config
            if len(config.config.keys()):
                self.out_to_console = False
                for key in config.config.keys():
                    exec('self.'+ key + ' =  config.config[\'' + key + '\']')
            else:
                print 'incorrect configuration format'
                exit(1)
        else:
            print 'file {0} is not found'.format(config_file)
            exit(1)

class BotModulesAndServices:
    def __init__(self):
        m = self.refresh('modules/')
        s = self.refresh('services/')
        for item in m:
            exec('from modules import {0}'.format(item))
        for item in s:
            exec('from services import {0}'.format(item))
        self.modules = [module for module in dir(modules) if not module.startswith('_')]
        self.services = [service for service in dir(services) if not service.startswith('_') and not service.startswith('prototype')]

    @staticmethod
    def refresh(path_to_init):
        init_file = open(path_to_init + '__init__.py', 'w')
        init_string = '__all__ = '
        init_list = repr(list(set([el.split('.')[0] for el in os.listdir(path_to_init) if not el.startswith('_')])))
        init_file.write(init_string + init_list)
        init_file.close()
        return eval(init_list)

class Bot:
    def __init__(self, config, room):
        self.cfg = config
        modiles_and_services = BotModulesAndServices()
        self.modules = modiles_and_services.modules
        self.services = modiles_and_services.services
        self.room = room
        if self.room.count('@') == 0:
            print 'incorrect room name'
            exit(1)
        self.serv_list = []
        for service in self.services:
            exec('self.serv_list.append(services.' + service + '.Service())')
        self.jid = xmpp.protocol.JID('@'.join([cfg.node, cfg.domain]))
        try:
            self.client = xmpp.Client(cfg.domain, debug=[])
            self.connection = self.client.connect()
        except:
            print 'connection problems'
            exit(1)
        self.client.RegisterHandler('message', self.message_handler)
        self.client.RegisterHandler('presence', self.presence_handler)
        self.auth = self.client.auth(cfg.node, cfg.password)
        self.client.sendInitPresence()
        pres = xmpp.Presence(to='/'.join([self.room, cfg.resource]))
        pres.setTag('x',namespace=xmpp.NS_MUC).setTagData('password', '')
        pres.getTag('x').addChild('history',{'maxchars':'0', 'maxstanzas':'0'})
        self.client.send(pres)
        thread.start_new_thread(self.listen, ())

    def listen(self):
        while 1:
            try:
                self.client.Process(1)
            except:
                time.sleep(1)

    def message_handler(self, sess, mess):
        if self.cfg.out_to_console:
            nick=mess.getFrom().getResource()
            text=mess.getBody()
            print '\r', nick, u': ', text, '\n'
        for module in self.modules:
            exec('answer = modules.' + module + '.work(sess, mess)')
            if answer is not None:
                self.send_message(answer)
                break
        for serv in self.serv_list:
            answer = serv.work(sess, mess)
            if answer is not None:
                self.send_message(answer)

    def presence_handler(self, sess, pres):
        pass

    def reload(self):
        BotModulesAndServices.refresh('modules/')
        BotModulesAndServices.refresh('services/')
        for module in self.modules:
            exec('reload(modules.' + module + ')')
        print 'modules have been reloaded'

    def send_message(self, text):
        reply = xmpp.Message(self.room, unicode(text))
        reply.setType('groupchat')
        self.client.send(reply)

    def work(self, ):
        while 1:
            command = raw_input('enter command: ')
            if command.lower() == 'reload':
                self.reload()
            if command.lower() == 'exit':
                exit(0)
            if 'send ' in command:
                res = re.match(u'^send (?P<text>.*)', command.decode('utf8'))
                text = res.group('text')
                self.send_message(text)
            if command.lower() == 'out 1':
                print 'output started'
                self.cfg.out_to_console = True
            if command.lower() == 'out 0':
                print 'output stopped'
                self.cfg.out_to_console = False

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1].count('@') != 0:
        room = sys.argv[1]
        cfg = BotConfig()
        bot = Bot(cfg, room)
        bot.work()
        pass
    elif len(sys.argv) == 3:
        if '--silent' in sys.argv[1] and '@' in sys.argv[2]:
            room = sys.argv[2]
            cfg = BotConfig()
            bot = Bot(cfg, room)
            while True:
                pass
        else:
            print 'Error'
            exit(0)
    else:
        print 'Use: bot.py --silent room@conference.jabber.org \n     where \'--silent\' disables the bot control'
        exit(0)





