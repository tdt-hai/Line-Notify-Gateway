#!/bin/env python3
"""
Line Notify Gateway Application
License: MIT
"""

import logging
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify

import manage_logs

LOG_PATH = 'logs/line-notify-gateway.log'
LINE_NOTIFY_URL = 'https://notify-api.line.me/api/notify'
app = Flask(__name__)

def findResolved(value):
    for i in value:
        if i['status'] == 'resolved':
            return True
    return False
def firing_alert(request):
    header = {'Authorization':request.headers['AUTHORIZATION']}
    this = []
    for alert in request.json['alerts']:
        this.append(alert)
    if request.json['status'] == 'firing':
        if findResolved(this) == True:
            for i in this:
                if i['status'] == 'resolved':
                    msg = "   RESOLVED \n" + i['annotations']['title']
                    msg = {'message': msg}
                    response = requests.post(LINE_NOTIFY_URL, headers=header, data=msg)
        else:
            for i in this:
                if i['status'] == 'firing':
                        msg = "   FIRING \n" + i['annotations']['description']
                        msg = {'message': msg}
                        response = requests.post(LINE_NOTIFY_URL, headers=header, data=msg)
    else:
        if findResolved(this) == False:
            for i in this:
                if i['status'] == 'firing':
                        msg = "   FIRING \n" + i['annotations']['description']
                        msg = {'message': msg}
                        response = requests.post(LINE_NOTIFY_URL, headers=header, data=msg)
        else:
            for i in this:
                if i['status'] == 'resolved':
                    msg = "   RESOLVED \n" + i['annotations']['title']
                    msg = {'message': msg}
                    response = requests.post(LINE_NOTIFY_URL, headers=header, data=msg)
@app.route('/')
def index():
    """
    Show summary information on web browser.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG)
    return render_template('index.html', name='index')


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Firing message to Line notify API when it's triggered.
    """
    logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG)
    logging.debug(str(request))
    if request.method == 'GET':
        return jsonify({'status':'success'}), 200
    if request.method == 'POST':
        try:
            firing_alert(request)
            return jsonify({'status':'success'}), 200
        except:
            return jsonify({'status':'bad request'}), 400


@app.route('/logs')
def logs():
    """
    Display logs on web browser.
    """
    file = open(LOG_PATH, 'r+')
    content = file.read()
    return render_template('logs.html', text=content, name='logs')


@app.route('/metrics')
def metrics():
    """
    Expose metrics for monitoring tools.
    """


if __name__ == "__main__":
    manage_logs.init_log(LOG_PATH)
    app.run(host='0.0.0.0')
