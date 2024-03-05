from PySide6.QtCore import Signal, QThread
import numpy as np
import cv2
from dotenv import load_dotenv
import os

load_dotenv()


class VideoThread(QThread):
    """
    A class to represent a video capturing thread.

    Attributes
    ----------
    change_pixmap_signal : Signal
        The signal that emits numpy array of image data.
    _run_flag : bool
        The flag to control the running of thread.

    Methods
    -------
    run():
        The main function of the thread to capture video from a source.
    stop():
        Stops the running thread.
    """

    change_pixmap_signal: Signal = Signal(np.ndarray)

    def __init__(self) -> None:
        """
        Constructs all the necessary attributes for the VideoThread object.
        """
        super().__init__()
        self._run_flag: bool = True

    def run(self) -> None:
        """
        The main function of the thread which captures video from a source.
        The source is specified in the environment variable 'RTSP'
        """
        # capture from web cam
        rtsp: str = os.getenv("RTSP")
        cap = cv2.VideoCapture(rtsp)
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)
        # shut down capture system
        cap.release()

    def stop(self) -> None:
        """
        Sets run flag to False and waits for the thread to finish.
        """
        self._run_flag = False
        self.wait()
