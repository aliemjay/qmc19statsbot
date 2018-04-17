#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  conversationmodel.py
#  
#  Copyright 2018 Ali MJ An-Nasrawy <alimj@alimj-pc>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  


from datetime import datetime
from telegram.ext import Handler
from threading import Lock
import logging, time

class ConversationHandler(Handler):
    """handles conversations seperately.
    params:
        conversation_cls: a subclass of Conversation
        responsive: if true, updates to a conv with an already running handler
            are queued for execution and thus may render the pool useless since
            they will block waiting for conv lock. Otherwise, they are ignored
        **kwargs: passed as is to conversation_cls.__init__()"""

    def __init__(self, conversation_cls, responsive=False, **kwargs):
        super(Handler, self).__init__()
        self.conversation_cls = conversation_cls
        self.responsive = responsive
        self.passed_kwargs = kwargs
        #dict of {int chat_id: obj conversation_cls}
        self.conversations = {}

    def check_update(self, update):
        """handle every update from "private" chats only"""
        return True if update.effective_chat.type == 'private' \
            else False

    def handle_update(self, update, dispatcher):
        """handle update by the dispatcher thread, it should be a lightweight
        handler and further processing is relayed to the thread pool.
        WARNING: unexpected behaviour: """
        if not update.effective_chat.id in self.conversations:
            #initiate new one
            self.conversations[update.effective_chat.id] = \
                self.conversation_cls(
                bot=dispatcher.bot,
                chat=update.effective_chat,
                **self.passed_kwargs)
            self.conversations[update.effective_chat.id]._hlock = \
                Lock()

        #handle update by type: command or message
        conv = self.conversations[update.effective_chat.id]
        lock = conv._hlock
        
        if self.responsive or not lock.locked():
            dispatcher.run_async(self._pooled_handler, conv=conv, lock=lock,
                msg=update.message)
        #otherwise, ignore
            
            
    def _pooled_handler(self, conv, lock, msg):
        #print(conv, lock)
        with lock:
            if msg.text.startswith("/"):
                conv.handle_command(msg)
            else:
                conv.handle_message(msg)
        

class Conversation:
    """base class for other conversations.
    any of the defined methods should not be overrided.
    Atrributes:
        chat; bot; apolo_system;
        ignore_until_notified: ignore messages until notified;
            set to true when expecting notification from apolo_system:
            when message older than 1 minute recieved and when
            TimeoutError on sending a message
        ignore_old: ignore messages older than last_message_id
        last_message_id: id(sequence) of the last sent message
    """

    def __init__(self, bot, chat,
        apolo_system = None, **kwargs):
        """pass kwargs to on_load"""
        self.chat = chat
        self.bot = bot
        self.apolo_system = apolo_system
        self.apolo_system.register_conversation(self)

        self.ignore_until_notified = False
        self.ignore_old = True
        self.last_message_id = 0

        self.on_load(**kwargs)
        
    def send_message(self, *args, **kwargs):
        try:
            msg = self.bot.send_message(
                chat_id = self.chat.id, *args, timeout=3, **kwargs)
            self.last_message_id = msg.message_id
            return msg
        except:
            self.apolo_system.notify_on_network(self)
            self.ignore_until_notified = True


    def handle_message(self, msg):
        logging.warning('cello: Conversation: new message handled {}'.\
            format(str(msg)))
        logging.warning('cello: Conversation: initial state dump: {}'.\
            format(str(self.__dict__)))
            
        if self.ignore_until_notified:
            pass
        elif self.ignore_old and msg.message_id < self.last_message_id:
            pass
        elif (msg.date - datetime.now()).total_seconds() < -15:
            self.apolo_system.notify_on_network(self)
            self.ignore_until_notified = True
        else:
            self.on_message(msg)
            
        logging.warning('cello: Conversation: final state dump: {}'.\
            format(str(self.__dict__)))

    def handle_command(self, msg):
        if msg.text == '/apolo':
            self.on_apolo(msg)
            self.ignore_until_notified = False
        else:
            self.on_command(msg)

    def on_load(self, **kwargs):
        pass

    def on_command(self, msg):
        pass

    def on_apolo(self, msg):
        pass

    def on_message(self, msg):
        pass
