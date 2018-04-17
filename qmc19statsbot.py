#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  qmc19statsbot.py
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

from conversationmodel import ConversationHandler, Conversation

class StackedHandler:
    pass

class MainConversation(Conversation):
    def on_load(self, **kwargs):
        self.call_stack=[]
        self.data_stack=[]
    
    def call_handler(self, hdlr, params_dict=None, **params_kwargs):
        params = params_dict if params_dict else params_kwargs
        self.data_stack.append(params)
        self.call_stack.append(hdlr)
        hdlr(state=params)
        
    def return_from_handler(self):
        self.call_stack.pop()
        retVal = self.data_stack.pop()
        self.call_stack[-1](state=self.data_stack[-1], ret_state=retVal)
        
    def hRegistration(self, state, ret_state=None):
        if not ret_state:
            self.call_handler(self.getMessage, tag='')
            
    def getMessage(self, state, msg=None, ret_data=None):
        if msg:
            state['msg'] = msg.text
            self.return_from_handler()
        
    def on_message(self, msg):
        logging.debug(': sleeping 5 secs')
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
            responsive=False, apolo_system=apolo)
    updater.dispatcher.add_handler(main_handler)
    apolo.start()
    updater.start_polling(timeout=120)
    updater.idle()
    

if __name__ == '__main__':
    import sys
    sys.exit(test(sys.argv))
