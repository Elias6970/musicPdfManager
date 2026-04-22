from PyQt6 import QtCore, QtWidgets
from frontend.pyqt.app.score_classifier.score_classifier_view import ScoreClassifierView

class ScoreClassifierController(QtCore.QObject):
    def __init__(self, view: ScoreClassifierView):
        super().__init__()
        self.view = view

        