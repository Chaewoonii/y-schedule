'''import sys

import pandas as pd
from PyQt5.QtWidgets import QDialog, QWidget,QFileDialog, QTableWidget, QApplication,QVBoxLayout, QTableWidgetItem, QScrollArea
from PyQt5 import uic

class MyApp(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('./Data Refinement Program.ui',self)
        self.ui.show()

    def initUI(self):
        self.setWindowTitle('Data Refinement Program')
        self.move(300,300)
        self.resize(400,200)
        self.show()

    def confirm(self):
        self.ui.label_status.setText('confirm')
    def cancel(self):
        self.ui.label_status.setText('cancel')

    def openfile(self):
        fname = QFileDialog.getOpenFileNames(self, 'Open file', './')
        print(type(fname), fname)
        self.ui.label_filename.setText(fname[0])
        path = fname[0][0]
        if path:
            win = QWidget()
            table = QTableWidget()
            scroll = QScrollArea()
            layout = QVBoxLayout()
            scroll.setWidget(table)
            layout.addWidget(table)
            win.setLayout(layout)

            df = pd.read_csv(path, encoding='cp949', engine='python')
            table.setColumnCount(len(df.columns))
            table.setRowCount(len(df.index))
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    table.setItem(i,j,QTableWidgetItem(str(df.iloc[i,j])))

            win.show()
'''

import pandas as pd
from PyQt5.QtWidgets import QFileDialog, QTableView, QApplication
from PyQt5.QtCore import QAbstractTableModel, Qt, QModelIndex
import sys


class PandasModel(QAbstractTableModel):
    """A model to interface a Qt view with pandas dataframe """

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        print('[PandasModel] __init__')
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def rowCount(self, parent=QModelIndex()) -> int:
        """ Override method from QAbstractTableModel

        Return row count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe)

        return 0

    def columnCount(self, parent=QModelIndex()) -> int:
        """Override method from QAbstractTableModel

        Return column count of the pandas DataFrame
        """
        if parent == QModelIndex():
            return len(self._dataframe.columns)
        return 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return data cell from the pandas DataFrame
        """
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])

        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):
        """Override method from QAbstractTableModel

        Return dataframe index as vertical header data and columns as horizontal header data.
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._dataframe.columns[section])

            if orientation == Qt.Vertical:
                return str(self._dataframe.index[section])

        return None

    def openfile(self):
        fname = QFileDialog.getOpenFileNames(self, 'Open file', './')
        print(type(fname), fname)
        path = fname[0][0]
        return path


    def showTable(self, model):
        view = QTableView()
        view.resize(800, 500)
        view.horizontalHeader().setStretchLastSection(True)
        view.setAlternatingRowColors(True)
        view.setSelectionBehavior(QTableView.SelectRows)

        view.setModel(model)
        view.show()
        app.exec()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    df = pd.read_csv('./resources/doro.csv', encoding='cp949', engine='python')
    pm = PandasModel(df)
    pm.showTable(pm)

