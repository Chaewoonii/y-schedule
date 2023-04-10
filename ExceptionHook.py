import sys
import traceback
import logging
from PyQt5 import QtCore, QtWidgets

log = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(stream=sys.stdout)
log.addHandler(stream_handler)

class ExceptionHook(QtCore.QObject):
    _exception_caught = QtCore.pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(ExceptionHook, self).__init__(*args, **kwargs)

        sys.excepthook = self.exception_hook
        self._exception_caught.connect(self.show_exception_box)

    def exception_hook(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        else:
            exc_info = (exc_type, exc_value, exc_traceback)
            log_msg = '\n'.join([''.join(traceback.format_tb(exc_traceback)),
                                 f'{exc_type.__name__}: {exc_value}'])
            log.critical(f"Uncaught Exception:\n{log_msg}", exc_info=exc_info)

            self._exception_caught.emit(log_msg)

    def show_exception_box(self, log_msg):
        if QtWidgets.QApplication.instance() is not None:
            errorBox = QtWidgets.QMessageBox()
            errorBox.setText(f"Uncaught Error Occured:\n{log_msg}")
            errorBox.exec_()

        else:
            log.debug("No QApplication instance available")