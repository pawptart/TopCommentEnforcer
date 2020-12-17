class ErrorHandler():
    def __init__(self, klass, logger):
        self.klass  = klass
        self.logger = logger

    def handle(self, exception):
        class_name = type(self.klass).__name__
        thread = self.klass.name

        self.logger.error("{} [{}]: {}".format(class_name, thread, exception))