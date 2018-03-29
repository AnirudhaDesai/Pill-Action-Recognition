#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 10:37:05 2018

@author: anirudha
"""

from flask import Flask

app = Flask(__name__)

@app.route('/users/<string:username>')
def hello_world(username=None):
    return ("Hello {}!".format(username))
