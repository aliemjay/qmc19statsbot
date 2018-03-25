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
token = '580202719:AAGxLrrfxbxmVoL-6KGRL0QShvfKiyqrYKM'
from datetime import datetime

class ConversationHandler(Handler):
    def __init__(self):
        super(Handler, self).__init__(None)
        self.conversations = {}
        
    def load_conversation(self, bot, chat):
        #invalid add function
        self.conversations.add(chat.id, Conversation(bot, chat))
            
    def check_update(self, update):
        if update.effective_chat.id in self.conversations:
            return True
        if update.effective_chat.type == 'private':
            self.load_conversation(update.effective_chat)
            return True
        else:
            return False
    
    def handle_update(self, update, dispatcher):
        #check if conv initiated otherwise create new one
        if not update.effective_chat.id in self.conversations:
            self.load_conversation(dispatcher.bot, update.effective_chat)
        #handle update by type: command or message
        conv = self.conversations[update.effective_chat.id]
        if update.message.text.startswith("/"):
            conv.on_command(update.message)
        else:
            conv.on_message(update.message)
            
class Conversation:
    def abort_previous_updates(self, date=None):
        if date:
            self.filter_date = date
        else:
            self.filter_date = now
        
    def __init__(self, bot, chat)
        self.chat = chat
        self.bot = bot
        
    def reset(self):
    """handle /reset command sent by user or error handler.
    send apologies message and reset to zero state"""
        pass
        
    def login(self):
        self.zero_state = clone(self.state)
        
    def suspend(self):
        self.suspended = Ture
        
    def send_message(self, *args, **kwargs):
        try:
            msg = self.bot.send_message(
                chat_id = self.chat.id, *args, **kwargs)
            self.last_msg_date = msg.date
            return msg
        except:
            xxx.apolo_system.register_chat(self.chat)
            self.invalid = True
        
        
    def on_message(self, msg):
        if self.invalid:
            return
        elif self.ignore_old and msg.date < self.last_msg_date:
            return
        elif (msg.date - datetime.now()).total_seconds() < -120:
            xxx.apolo_system.register_chat(self.chat)
            self.invalid = True
        else:
            self.handle_state(
    
    def on_command(self, msg):
        pass
    
class ApoloSystem(Thread):
    def __init__(self, update_queue):
        super(Thread, self).__init__()
        self.__lock = Lock()
        self.update_queue = update_queue
        self.apolo_chats=[]
        self.apolo_chats_lock = Lock()
        
    def register_chat(self, chat):
        with self.apolo_chats_lock:
            if not chat in self.apolo_chats:
                self.apolo_chats.append(chat)
                
    def apologise(self, chat0):
        msg = Message(
            message_id = 123123123,
            from_user = None,
            date = datetime.now(),
            chat = chat0
            text = '/apolo' )
        update = Update(message = msg, chat = chat0)
        update_queue.put(update)
    
    def stop(self):
        self.set_stop = True
        self.__lock.acquire()
        self.__lock.release()
        
    def run(self):
        self.__lock.acquire()
        while not self.set_stop:
            if socket.connect(xxxx):
                with self.apolo_chats_lock:
                    for chat in sef.apolo_chats:
                        self.apologise(chat)
                    self.apolo_chats = []
            datetime.sleep(2)
            
        self.__lock.release()

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
