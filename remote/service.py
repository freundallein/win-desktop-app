# -*- coding: utf-8 -*-
import time

from PyQt5.QtCore import pyqtSignal, QThread

from utils import Logger, Configurator
from remote.requester import HttpRequester


class RemoteService(QThread):
    TAG = 'REMOTE SERVICE'
    data_received = pyqtSignal(dict)
    status_changed = pyqtSignal(str)

    def __init__(self, parent, config):
        super(RemoteService, self).__init__(parent)
        self.requester = HttpRequester(config)
        self.logger = Logger()

    def log(self, message):
        self.logger.TAG = self.TAG
        self.logger.log(message)

    def send_status_OK(self):
        self.status_changed.emit('OK')

    def send_status_STANDBY(self):
        self.status_changed.emit('STANDBY')

    def get_text_status(self, flag):
        return 'ON' if flag else 'OFF'

    def check_server_status(self, inner):
        machine_status = self.get_text_status(inner)
        return self.requester.server_exchange(machine_status)

    def check_inner_status(self):
        return True

    def send_data(self, data):
        self.log('send data from main thread: %s' % data)

    def get_data(self, data):
        datatype = data.get('data')
        if datatype == 'types':
            types = self.requester.get_types()
            self.log('Types from server: %s' % types)
            self.data_received.emit(types)
        elif datatype == 'form':
            card_type = data.get('card_type')
            form = self.requester.get_form(card_type)
            self.log('Form from server: %s' % form)
            self.data_received.emit(form)

    def run(self):
        while True:
            inner_status = self.check_inner_status()
            server_status = self.check_server_status(inner_status)

            self.log("Server status: " + self.get_text_status(server_status))
            self.log("Inner status: " + self.get_text_status(inner_status))
            if server_status and inner_status:
                self.send_status_OK()
            else:
                self.send_status_STANDBY()
            time.sleep(3)
