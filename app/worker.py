from qtpy.QtCore import QObject, Signal


class Worker(QObject):
    finished = Signal()  # Signal when the task is finished
    result = Signal(object)  # Signal to return the result
    error = Signal(str)  # Signal for errors

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
            self.result.emit(result)  # Send the result to the main thread
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()  # Notify that the task is finished
