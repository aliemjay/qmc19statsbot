#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.oy
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
import logging, time

class ConversationHandler(Handler):
    """handles conversations seperately.
    params:
        conversation_cls: a subclass of Conversation
        **kwargs: passed as is to conversation_cls.__init__()"""

    def __init__(self, conversation_cls, **kwargs):
        super(Handler, self).__init__()
        self.conversation_cls = conversation_cls
        self.passed_kwargs = kwargs
        #dict of {int chat_id: obj conversation_cls}
        self.conversations = {}

    def check_update(self, update):
        """handle every update from "private" chats only"""
        return True if update.effective_chat.type == 'private' \
            else False

    def handle_update(self, update, dispatcher):

        if not update.effective_chat.id in self.conversations:
            #initiate new one
            self.conversations[update.effective_chat.id] = \
                self.conversation_cls(
                bot=dispatcher.bot,
                chat=update.effective_chat,
                **self.passed_kwargs)

        #handle update by type: command or message
        conv = self.conversations[update.effective_chat.id]
        if update.message.text.startswith("/"):
            conv.handle_command(update.message)
        else:
            conv.handle_message(update.message)

class Conversation:
    """base class for other conversations
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
                chat_id = self.chat.id, *args, timeout=2, **kwargs)
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

class MainConversation(Conversation):
    def on_load(self, **kwargs):
        pass
    
    def on_message(self, msg):
        logging.debug('cello: sleeping 5 secs')
        self.send_message(text=msg.text)
        
    def on_apolo(self, msg):
        logging.debug('cello: apolo recieved')
        self.send_message(text='apolo recieved')


def test(args):
    from apolosystem import ApoloSystem
    import telegram.ext as tg
    import logging
    logging.basicConfig(
        filename='/tmp/log', filemode='w',
        level=logging.DEBUG)

    token = args[1]

    updater = tg.Updater(token)
    apolo = ApoloSystem(updater.update_queue)
    main_handler = ConversationHandler(MainConversation,
        apolo_system=apolo)
    updater.dispatcher.add_handler(main_handler)
    apolo.start()
    updater.start_polling(timeout=120)
    updater.idle()
    

if __name__ == '__main__':
    import sys
    sys.exit(test(sys.argv))
