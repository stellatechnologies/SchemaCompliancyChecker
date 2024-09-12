import logging


class SchemaValidatorLogger:
    def __init__(self):
        self.info = []
        self.warnings = []
        self.errors = []
        self.logger = logging.getLogger(__name__)
        
    def add_message(self, message, message_type):
        if message_type == 'info':
            self.info.append(message)
        elif message_type == 'warning':
            self.warnings.append(message)
        elif message_type == 'error':
            self.errors.append(message)
        else:
            raise ValueError('Invalid message type. Must be info, warning, or error')