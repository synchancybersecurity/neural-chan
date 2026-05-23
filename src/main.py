import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from neural_window import NeuralWindow
from brain_thread import BrainThread

if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = NeuralWindow()
    brain = BrainThread(window)
    brain.start()
    window.set_brain(brain)
    window.show()
    sys.exit(app.exec())
