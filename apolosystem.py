#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread, Lock
from datetime import datetime
from telegram import Message, Update
import socket, time, logging

class ApoloSystem(Thread):
    def __init__(self, update_queue):
        super().__init__()
        
        self.__lock = Lock()
        self.set_stop = False
        
        self.update_queue = update_queue
        self.conversations=[]
        
        self.notifiable_convs = []
        self.notifiable_convs_lock = Lock()

    def register_conversation(self, conv):
        if not conv in self.conversations:
            self.conversations.append(conv)

    def notify_on_network(self, conv):
        """register a conv for notification when network recovered"""
        with self.notifiable_convs_lock:
            if not conv in self.notifiable_convs:
                self.notifiable_convs.append(conv)
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
        self.set_stop = True
        self.__lock.acquire()
        self.__lock.release()

    def run(self):
        """check regularly for network status;
        if up, notify every registered chat"""
        self.__lock.acquire()
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk
        while not self.set_stop:

            try:
                sk = socket.create_connection(
                    ('149.154.167.220', 80), timeout=2)
                sk.close()
                if len(self.notifiable_convs) == 0:
                    continue
                with self.notifiable_convs_lock:
                    for conv in self.notifiable_convs:
                        self.notify(conv)
                    self.notifiable_convs = []
                    logging.debug('cello: Apolo: notification dispatched')
            except Exception:
                logging.warning('cello: Apolo: network disconnected')
            
            time.sleep(5)

        self.__lock.release()
