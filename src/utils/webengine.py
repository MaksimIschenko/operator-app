from typing import List, Dict, Union

from PySide6.QtWebEngineCore import QWebEnginePage
from src.web.mapestimator import Estimator

from src.utils.datashower import DataShower

from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtCore import QTimer
import sys


class WebEnginePage(QWebEnginePage):
    _webPointsData: List[str] = []

    def javaScriptConsoleMessage(self,
                                 level: int,
                                 message: str,
                                 lineNumber: int,
                                 sourceID: str) -> None:

        self._webPointsData.append(message)
        return super().javaScriptConsoleMessage(level, message,
                                                lineNumber, sourceID)

    def __getitem__(self, i: int) -> Union[Dict[str, Union[str, int, float]], None]:
        try:
            item = self.__parse_raw_data(i)
        except IndexError as _:
            item = None
        return item

    def __len__(self) -> int:
        if len(self._webPointsData) - 1 < 0:
            return 0
        return len(self._webPointsData) - 1

    def __iter__(self):
        for i in range(len(self._webPointsData) - 1):
            item = self.__parse_raw_data(i)
            yield item

    def __parse_raw_data(self, key: int) -> Dict[str, Union[int, float]]:
        raw_str = self._webPointsData[key + 1].split(' ')[1:]
        coord = [float(el) for el in raw_str[0].split(',')]
        item = {'Point': key, 'Latitude': coord[1], 'Longitude': coord[0]}
        return item

    def removePoints(self):
        self._webPointsData = []


class WebEngineMap(DataShower):
    def __init__(self):
        super().__init__()

        self.__currentPos: Dict[str, Union[str, float]] = {'Point': 'Current Position', 'Latitude': 59.818080, 'Longitude': 30.328469}
        self.view = self.ui.webEngineView
        self.page: WebEnginePage = WebEnginePage()

        self.view.setPage(self.page)
        self.view.setHtml(open("src/web/index.html").read())

        self.timer: QTimer = QTimer()
        self.timer.timeout.connect(self.getPoints)
        self.timer.start(1000)

        self.view.show()

        self.ui.btn_delete_points.clicked.connect(self.deletePoints)

        self.ui.table_points.setColumnCount(4)
        self.ui.table_points.resizeColumnsToContents()
        self.ui.table_points.setColumnWidth(0, 200)
        self.ui.table_points.setColumnWidth(1, 200)
        self.ui.table_points.setColumnWidth(2, 100)
        self.ui.table_points.setColumnWidth(3, 100)

        column_name: List[str] = ['Lat', 'Long', 'Dist', 'AZ']
        self.ui.table_points.setHorizontalHeaderLabels(column_name)

        self.estimator: Estimator = Estimator()

    def getPoints(self):

        if len(self.page) == 0:
            self.ui.table_points.setRowCount(0)
            pass

        else:
            self.ui.table_points.setRowCount(len(self.page))
            for idx, point in enumerate(self.page):
                if idx == 0:
                    distance = self.estimator.haversine(start_point=self.__currentPos,
                                                        end_point=point)
                    azimut = self.estimator.initial_bearing(start_point=self.__currentPos,
                                                            end_point=point)
                else:
                    distance = self.estimator.haversine(start_point=self.page[idx - 1],
                                                        end_point=point)
                    azimut = self.estimator.initial_bearing(start_point=self.page[idx - 1],
                                                            end_point=point)

                self.__pasteValueInTable(idx, point['Latitude'], point['Longitude'], distance, azimut)

    def deletePoints(self):
        self.view.reload()
        self.page.removePoints()

    def __pasteValueInTable(self, idx: int, latitude: float, longitude: float, distance: float, azimut: float):
        values: List[float] = [latitude, longitude, distance, azimut]
        for i, value in enumerate(values):
            formatted_value: str = f'{value:.4f}' if i < 2 else f'{value:.2f}'
            self.ui.table_points.setItem(idx, i, QTableWidgetItem(formatted_value))


if __name__ == '__main__':
    app: QApplication = QApplication(sys.argv)
    window: WebEngineMap = WebEngineMap()
    window.show()
    app.exec()