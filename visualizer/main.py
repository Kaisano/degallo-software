# visualize serial output
import sys
from PySide6.QtCharts import QBarSet, QBarSeries, QChart, QBarCategoryAxis, QValueAxis, QChartView
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout
from PySide6.QtCore import Slot, Signal, Qt, QThread, QThreadPool
from PySide6.QtGui import QPainter

from serial_device import serial_device_manager

import random as rand


class DataView(QWidget):
    newDataGenerated = Signal(list)

    def __init__(self, parent=None):
        super(DataView, self).__init__(parent)
        # super().__init__()

        self.setWindowTitle("PIU Pad DataView")
        self.set_0 = QBarSet("1")

        self.set_0.append([1, 2, 3, 4, 5])

        self.series = QBarSeries()
        self.series.append(self.set_0)

        self.chart = QChart()
        self.chart.addSeries(self.series)
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.categories = ["1", "2", "3", "4", "5"]
        self.axis_x = QBarCategoryAxis()
        self.axis_x.append(self.categories)
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setRange(0, 3.3)
        # self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        self.chart.legend().setVisible(False)
        self.chart.setBackgroundVisible(False)
        # self.chart.legend().setAlignment(Qt.AlignBottom)

        self._chart_view = QChartView(self.chart)
        self._chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.button = QPushButton("Change data")
        self.button.clicked.connect(self.generateNewData)
        self.newDataGenerated.connect(self.changeData)

        self.qvboxlayout = QVBoxLayout()
        self.qvboxlayout.addWidget(self._chart_view)
        self.qvboxlayout.addWidget(self.button)
        self.setLayout(self.qvboxlayout)

        # self.setCentralWidget(self._chart_view)

    @Slot()
    def generateNewData(self):
        data = [rand.uniform(0,3.3), rand.uniform(0,3.3), rand.uniform(0,3.3), rand.uniform(0,3.3), rand.uniform(0,3.3)]
        self.newDataGenerated.emit(data)

    @Slot(list)
    def changeData(self, data):
        for i, d in enumerate(data):
            self.set_0.replace(i, d)

if __name__ == "__main__":
    # dev_manager = serial_device_manager()
    app = QApplication(sys.argv)
    button = QPushButton("Change Data")
    DV = DataView()
    DV.resize(420, 300)
    DV.show()
    sys.exit(app.exec())
    
    # app.exec()
    # while True:

    #     device_manager.update_port()
    #     print(device_manager.shared_device_data)