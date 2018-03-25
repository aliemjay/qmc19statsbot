#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dbhelper.py
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
import sqlite3
import threading

class DegDB:
    def __init__(self, db):
        self.db = db
        self.per_thread_conns = {}
        
    def get_conn(self):
        """returns the sqlite3 connection associated with the
        calling thread. This best works with thread-pools not with
        transiently created and detroyed threads"""
        try:
            conn = self.per_thread_conns[threading.current_thread()]
        except KeyError:
            conn = sqlite3.connect(self.db)
            self.per_thread_conns[threading.current_thread()] = conn
        return conn
    
    def upate_student(student_id, info)

def main(args):
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
