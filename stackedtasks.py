#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  TODO: Documentation
        
class StackedTasks():

    class Task(object):
        pass
    class Event(object):
        INIT = Event('init')
        def __init__(self, _id, **kwargs):
            self.id = _id
            self.__dict__.update(kwargs)
            
    def __init__(self):
        self.tasks = []
        
    def put_task(self, hdlr, **state):
        task = Task()
        task.__dict__.update(state)
        task.__dict__['hdlr'] = hdlr
        self.tasks.append(task)
        task.hdlr(task, Event.INIT)
        
    def drop_task(self):
        ret_task = self.tasks.pop()
        task = self.tasks[-1]
        task.hdlr(task, Event('ret', task=ret_task))
        
    def send_event(self, _id, **kwargs):
        task = self.tasks[-1]
        task.hdlr(task, Event(_id, **kwargs))
        
    def current_task(self):
        return self.tasks[-1]
        
def task_handler(*none_args, **defaults):

    def decor(func):
    
        def wrapper(*pos_args, **kwargs):
            task = pos_args[-2]
            event = pos_args[-1]
            if event.id == 'init':
                update1 = {x:None for x in none_args \
                            if not x in task.__dict__}
                update2 = {x:defaults[x] for x in defualts \
                            if not x in task.__dict__}
                task.__dict__.update(update1)
                task.__dict__.update(update2)
            return func(*pos_args, **kwargs)
            
        return wrapper
        
    return decor
