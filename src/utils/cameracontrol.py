from PySide6.QtCore import Slot, Qt
from PySide6 import QtWidgets, QtGui
from src.utils.webengine import WebEngineMap
from src.video.videothread import VideoThread
import numpy as np
import cv2
import sys


class CameraControl(WebEngineMap):

    def __init__(self):
        super(CameraControl, self).__init__()
        self.button_configuration()

    def button_configuration(self):
        """Configure buttons to connect with camera operations"""
        self.ui.btn_start_camera.clicked.connect(self._start_camera)
        self.ui.btn_stop_camera.clicked.connect(self._stop_camera)

    def _start_camera(self):
        """Start the RTSP stream"""
        self.vthread = VideoThread()
        self.vthread.start()
        self.vthread.change_pixmap_signal.connect(self.update_image)
        self._toggle_button_states()

    def _stop_camera(self):
        """Stop the RTSP stream"""
        self.vthread.stop()
        self.vthread = None
        self._toggle_button_states()

    def _toggle_button_states(self):
        """Toggle button states when starting/stopping the camera"""
        camera_running = self.vthread and self.vthread.isRunning()
        self.ui.btn_start_camera.setEnabled(not camera_running)
        self.ui.btn_stop_camera.setEnabled(camera_running)

    @Slot(np.ndarray)
    def update_image(self, cv_img):
        """Update lb_camera with the received opencv frame"""
        qt_img = self.convert_cv_qt(cv_img)
        self.ui.lb_camera.setPixmap(qt_img)

    @staticmethod
    def convert_cv_qt(cv_img):
        """Convert an OpenCV frame to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, Qt.KeepAspectRatio)
        return QtGui.QPixmap.fromImage(p)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = CameraControl()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()