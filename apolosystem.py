#!/usr/bin/env python
# -*- coding: utf-8 -*-
#TODO: sync ApoloSystem.conversations

from threading import Thread, Lock, Event, Condition
from datetime import datetime
from telegram import Message, Update
import socket, time, logging

class ApoloSystem(Thread):
    def __init__(self, update_queue):
        super().__init__()
        
        self.__finished = Event()
        
        self.update_queue = update_queue
        self.conversations=[]
        
        self.notifiable_convs = []
        self.set_stop = False
        self.apolo_condition = Condition() 
        #protects notifiable_convs and set_stop

    def register_conversation(self, conv):
        if not conv in self.conversations:
            self.conversations.append(conv)

    def notify_on_network(self, conv):
        """register a conv for notification when network recovered"""
        with self.apolo_condition:
            if not conv in self.notifiable_convs:
                self.notifiable_convs.append(conv)
                self.apolo_condition.notify()
                logging.debug('cello: Apolo: conv registered')

    def notify(self, conv):
        """send /apolo to a chat"""
        msg = Message(
            message_id = 123123123,
            from_user = None,
            date = datetime.now(),
            chat = conv.chat,
            text = '/apolo' )
        update = Update(update_id = 0, 
            message = msg)
        self.update_queue.put(update)

    def stop(self):
        """stops the thread, blocks until run() completes a cycle"""
        with self.apolo_condition:
            self.set_stop = True
            self.apolo_condition.notify()
        self.__finished.wait()

    def run(self):
        """check regularly for network status;
        if up, notify every registered chat"""
        check_connection = False
        
        while True:
        
            with self.apolo_condition:
                if self.set_stop:
                    break
                elif len(self.notifiable_convs) > 0:
                    check_connection = True
                else:
                    self.apolo_condition.wait() #wait for case worth handling
                    check_connection = False
                    
            if check_connection:
                try:
                    sk = socket.create_connection(
                            ('149.154.167.220', 80), timeout=2)
                    sk.close()
                    with self.apolo_condition:
                        for conv in self.notifiable_convs:
                            self.notify(conv)
                        self.notifiable_convs = []
                    logging.debug('cello: Apolo: notification dispatched')
                    
                except Exception:
                    logging.warning('cello: Apolo: network disconnected')
                    time.sleep(5)

        self.__finished.set()
