import json
import os
import sys
import calendar
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import re

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import *
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDate, Qt
from PyQt5 import uic


import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtWidgets

# import plotly.express as px

import folium
from folium import plugins

from pandasModel import PandasModel
from MyUtill import MyUtill
from ExceptionHook import ExceptionHook

ex = ExceptionHook()

matplotlib.use('qt5agg')
plt.rc('font', family='gulim')

formClass = uic.loadUiType('./resources/1.ui')[0]
class MyCalendar(QDialog, QWidget, formClass):
    def __init__(self, parent=None, data=None):
        print('__main__[MyCalendar] __init__***')
        super(MyCalendar, self).__init__(parent)
        self.mu = MyUtill()
        self.path = './resources/scheduleDataSaved.csv'
        self.fileName = 'scheduleDataSaved.csv'
        self.schedule = pd.DataFrame()
        self.todayDf = pd.DataFrame()
        self.dateColName = '연월일'
        self.dongColName = '동'
        self.settingsDf = pd.DataFrame()
        self.settingsPath = './resources/settings.csv'
        self.selectedDate = ''
        self.setupUi(self)
        self.initDF(data)
        self.initSettingsDf()
        self.visits_dong()
        self.initUI()

    def setSettingsDf(self, df):
        self.settingsDf = df

    def initSettingsDf(self):
        df = pd.read_csv(self.settingsPath, encoding='cp949', engine='python')
        self.setSettingsDf(df)
        print(self.settingsDf)
        return df

    def initDF(self, data):
        if data is None:
            try:
                df = pd.read_csv(self.path, encoding='cp949', engine='python')
            except:
                df = pd.read_csv(self.path, encoding='utf-8-sig', engine='python')

            df = self.setString(df, self.dateColName)
            df = df.fillna('')
            self.setSchedule(df)

        else:
            self.setSchedule(data)

        self.initToday()

    def setSelectedDate(self, date):
        print('__main__[MyCalendar] setSelectedDate***')
        self.selectedDate = date

    def getSelectecDate(self):
        print('__main__[MyCalendar] getSelectecDate***')
        return self.selectedDate

    def setTodayDf(self, df):
        print('__main__[MyCalendar] setTodayDf***')
        self.todayDf = df
        print(self.todayDf)

    def getTodayDf(self):
        print('__main__[MyCalendar] getTodayDf***')
        return self.todayDf

    def setSchedule(self, df):
        print('__main__[MyCalendar] setSchedule***')
        self.schedule = df

    def getSchedule(self):
        print('__main__[MyCalendar] getSchedule***')
        return self.schedule

    def setDateColName(self, name):
        print('__main__[MyCalendar] setDateColName***')
        self.dateColName = name

    def getDateColName(self):
        print('__main__[MyCalendar] getDateColName***')
        return self.dateColName

    def setString(self, df, col):
        print('__main__[MyCalendar] setString***')
        if df.empty:
            print('Empty Data Frame!')

        else:
            for idx in range(len(df)):
                df.loc[idx, col] = str(df.loc[idx, col])
        return df

    def initUI(self):
        print('__main__[MyCalendar] initUI***')
        self.getScheduleBtn.clicked.connect(self.openfile)
        self.calendarWidget.clicked.connect(self.setToday)
        self.monthlyBtn.clicked.connect(self.initCalendar)
        self.scheduleAnalysisBtn.clicked.connect(self.initScheduleAnalysis)
        self.settingsBtn.clicked.connect(self.openSettings)
        self.today.setAlignment(Qt.AlignTop)
        self.vLayout_btns.setAlignment(Qt.AlignTop)
        self.setWindowTitle('Y-Schedule')


    def openSettings(self):
        print('__main__[MyCalendar] openSettings***')
        s = AnalysisSettings(parent=self, data=self.schedule,
                             minDay=self.schedule[self.dateColName].min(),
                             maxDay=self.schedule[self.dateColName].max(),
                             settings=self.settingsDf)
        s.exec_()
        if s.settings is not None:
            self.setSettingsDf(s.settings)
            self.settingsDf = self.settingsDf.dropna()
            self.settingsDf.to_csv(self.settingsPath, encoding='cp949', index=False)
            self.visits_condi(condi=s.condi)

    def mainClose(self):
        print('__main__[MyCalendar] mainClose***')

    def openfile(self):
        print('__main__[MyCalendar] openfile***')
        path = ''
        pathFileName = QFileDialog.getOpenFileName(self, '스케줄 불러오기', './')

        try:
            if pathFileName != ('',''):
                path = pathFileName[0]

            else:
                print('else')

        except:
            print('except')

        if path != '':
            self.path, self.fileName = self.mu.getPath_FileName(path)

            try:
                df = pd.read_csv(path, encoding='cp949', engine='python')

            except:
                df = pd.read_csv(path, encoding='utf-8-sig', engine='python')

            self.setSchedule(df)
            print(self.schedule)
            self.setDateCol()
            self.setToday()
            return df

    def setDateCol(self):
        print('__main__[MyCalendar] setDateCol***')
        cols = self.schedule.columns.to_list()
        sc = SelectCol(self, cols)
        sc.exec_()
        target = sc.getTarget()
        if target != '':
            self.setDateColName(target)
            self.schedule[target] = self.mu.delStrip(self.schedule[target].to_list())

    def initToday(self):
        print('__main__[MyCalendar] initToday***')
        date = str(datetime.datetime.today().strftime('%Y%m%d'))
        self.setSelectedDate(date)
        self.setTodayDf(self.schedule[self.schedule[self.dateColName] == self.selectedDate])

        if self.todayDf.empty:
            addBtn = QPushButton('일정 추가하기', self)
            addBtn.clicked.connect(self.addSchedule)
            addBtn.setStyleSheet("font-size: 10pt;")
            addBtn.setMinimumHeight(25)
            addBtn.setMaximumHeight(30)
            self.today.addWidget(addBtn)

        else:
            todaySimple = self.todayDf[['시간', '동', '행사명']]
            for i in self.todayDf.index.to_list():
                txt = ' | '.join(todaySimple.loc[i].to_list())
                if len(txt) > 40:
                    txt = txt[:41] + '...'
                btn = QPushButton(txt, self)
                btn.clicked.connect(lambda checked, i=i: self.detailPopup(i))
                btn.setStyleSheet("font-size: 10pt;")
                btn.setMinimumHeight(23)
                btn.setMaximumHeight(30)
                self.today.addWidget(btn)

    def setToday(self):
        print('__main__[MyCalendar] setToday***')
        self.layoutClear(self.today)
        self.setSelectedDate(self.calendarWidget.selectedDate().toString('yyyyMMdd'))
        self.setTodayDf(self.schedule[self.schedule[self.dateColName] == self.selectedDate])

        if self.todayDf.empty:
            addBtn = QPushButton('일정 추가하기', self)
            addBtn.clicked.connect(self.addSchedule)
            addBtn.setStyleSheet("font-size: 10pt;")
            addBtn.setMinimumHeight(25)
            addBtn.setMaximumHeight(30)
            self.today.addWidget(addBtn)

        else:
            print('__main__[MyCalendar] setToday::::Set Schedule')
            todaySimple = self.todayDf.copy()[['시간', '동', '행사명']]

            for i in self.todayDf.index.to_list():
                print(i)
                print(todaySimple.loc[i].to_list())
                txt = ' | '.join(todaySimple.loc[i].to_list())
                if len(txt) > 50:
                    txt = txt[:51] + '...'
                btn = QPushButton(txt, self)
                btn.clicked.connect(lambda checked, i=i: self.detailPopup(i))
                btn.setStyleSheet("font-size: 10pt;")
                btn.setMinimumHeight(25)
                btn.setMaximumHeight(30)
                self.today.addWidget(btn)

    def detailPopup(self, idx):
        print('__main__[MyCalendar] detailPopup***')
        print(idx)
        li = self.schedule.iloc[idx][1:].to_list()
        sd = ScheduleDetail(self, data=li)
        sd.exec_()
        data = sd.getData()
        print(data)
        if data is not None:
            self.setData(data, idx)
        self.setToday()

    def addSchedule(self):
        print('__main__[MyCalendar] detailPopup***')
        date = self.calendarWidget.selectedDate().toString('yyyyMMdd')
        sd = ScheduleDetail(self, date=date)
        sd.exec_()
        data = sd.getData()
        if data is not None:
            self.addData(data)
        self.setToday()

    def addData(self, data):
        print('__main__[MyCalendar] addData***')
        idx = len(self.schedule)
        data.insert(0, idx)
        self.schedule.loc[idx] = data
        print(self.schedule.tail())

    def setData(self, data, idx):
        print('__main__[MyCalendar] setData***')
        for i, col in enumerate(self.schedule.columns.to_list()[1:]):
            self.schedule.loc[idx, col] = data[i]

    def layoutClear(self, layout):
        print('__main__[MyCalendar] layoutClear***')
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    def visits_dong(self):
        print('__main__[MyCalendar] visits_dong***')
        figure = plt.figure(figsize=(8,4))
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)
        figure.clear()
        ax = figure.add_subplot(111)
        sns.countplot(data=self.schedule, x='동', ax=ax)
        self.vBoxGraph.addWidget(toolbar)
        self.vBoxGraph.addWidget(canvas)
        canvas.draw()

    def visits_condi(self, condi):
        print('__main__[MyCalendar] visits_condi***')
        # self.clearLayout(self.vBoxGraph)
        figure = plt.figure(figsize=(8,4))
        canvas = FigureCanvas(figure)
        toolbar = NavigationToolbar(canvas, self)
        figure.clear()
        ax = figure.add_subplot(111)
        sns.countplot(data=self.schedule[self.schedule[self.dateColName] == condi], x=self.dongColName, ax=ax)
        self.vBoxGraph.addWidget(toolbar)
        self.vBoxGraph.addWidget(canvas)
        canvas.draw()

    def initCalendar(self):
        print('__main__[MyCalendar] initCalendar***')
        print(self.schedule.tail(5))
        cal = Calendar(parent=self, schedule=self.schedule)
        self.hide()
        cal.exec_()
        data = cal.getSchedule()
        if data is not None and data.empty is not True:
            print('outCalendar')
            self.setSchedule(data)
            self.setToday()

    def initScheduleAnalysis(self):
        print('__main__[MyCalendar] initScheduleAnalysis***')
        sa = ScheduleAnalysis(parent=self, data=self.schedule)
        self.hide()
        sa.exec_()
        data = sa.getData()
        print(data)
        if data is not None and data.empty is not True:
            print('outCalendar')
            self.setSchedule(data)
            self.setToday()

    def clearLayout(self, layout):
        print('[Calendar] clearLayout***')
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

class SelectCol(QDialog, QWidget):
    def __init__(self, parent, cols):
        print('[SelectCol] __init__----')
        super(SelectCol, self).__init__(parent)
        self.cols = cols
        self.target = ''
        self.cnt = len(cols)
        self.initUI()
        self.show()

    def initUI(self):
        print('[SelectCol] initUI----')
        self.gbox = QGridLayout()

        for i in range(self.cnt):
            globals()[f'rbtn{i}'] = QRadioButton(f'rbtn{i}', self)
            globals()[f'rbtn{i}'].setText(self.cols[i])
            self.gbox.addWidget(globals()[f'rbtn{i}'], i//2, i%2)


        self.SelectColCommit = QPushButton('확인', self)
        self.SelectColCommit.clicked.connect(self.selectColConfirm)
        self.SelectColCancel = QPushButton('취소', self)
        self.SelectColCancel.clicked.connect(self.selectColClose)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.SelectColCommit)
        self.hbox.addWidget(self.SelectColCancel)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(self.gbox)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)
        self.setWindowTitle('속성 선택')

    def selectColConfirm(self):
        print('[SelectCol] selectColConfirm----')
        for i in range(self.cnt):
            if globals()[f'rbtn{i}'].isChecked():
                self.setTarget(self.cols[i])
        self.close()

    def setTarget(self, target):
        print('[SelectCol] setTarget----')
        self.target = target

    def getTarget(self):
        print('[SelectCol] getTarget----')
        return self.target

    def selectColClose(self):
        print('[SelectCol] selectColClose----')
        self.close()


form_detail = uic.loadUiType('./resources/schedule_detail.ui')[0]
class ScheduleDetail(QDialog, QWidget, form_detail):
    def __init__(self, parent, data=None, date=None, labels=None):
        print('[ScheduleDetail] __init__****')
        super(ScheduleDetail, self).__init__(parent)
        self.year = datetime.datetime.today().year
        self.month = datetime.datetime.today().month
        self.day = datetime.datetime.today().day
        self.date = date
        self.time = datetime.datetime.now()
        self.dong = ''
        self.event = ''
        self.location = ''
        self.attend = ''
        self.manager = ''
        self.phone = ''
        self.group = ''
        self.labels=labels
        self.data = data
        self.labels = []

        self.setupUi(self)
        self.initUI()
        self.show()

    def initUI(self):
        print('[ScheduleDetail] initUI****')
        self.setData(self.data)
        self.setInfo()
        self.setDate(self.date)
        self.setTime(self.time)
        self.initLables()
        self.setComboBox(self.comboBox_group, self.labels)
        self.detailModifyBtn.clicked.connect(self.detailModifyConfirm)
        self.detailCancelBtn.clicked.connect(self.scheduleDetailClose)

    def initLables(self):
        print('[ScheduleDetail] initLabels****')
        if self.labels is None:
            df = pd.read_csv('./resources/settings.csv', encoding='cp949', engine='python')
            labels = df['단체'].to_list()
            self.setLabels(labels)
            print(self.labels)
            return labels

    def setLabels(self, li):
        print('[ScheduleDetail] setLabels****')
        self.labels = li

    def getLabels(self):
        print('[ScheduleDetail] getLabels****')
        return self.labels

    def setComboBox(self, cBox, li):
        print('[ScheduleDetail] setComboBox****')
        for item in li:
            print(item)
            self.comboBox_group.addItem(item)
        return cBox


    def setData(self, data):
        print('[ScheduleDetail] setData****')
        print(data)
        # self.date = QDate.fromString(str(data[0]),'yyyymmdd')
        if data == None:
            print('Empty Data')
            self.data = None

        else:
            self.year = data[0]
            self.month = data[1]
            self.day = data[2]
            self.date = data[3]
            self.time = str(data[4])
            self.dong = str(data[5])
            self.event = str(data[6])
            self.location = str(data[7])
            self.attend = self.getIntFromString(data[8])
            self.manager = str(data[9])
            self.phone = str(data[10])
            self.group = str(data[11])
            self.data = [self.year, self.month, self.day, self.date,
                         self.time, self.dong, self.event, self.location,
                         self.attend, self.manager, self.phone, self.group]

    def getIntFromString(self, txt):
        num = 0
        if type(txt) == str:
            num = int(re.findall('\d{1,3}', txt)[0])
            return num
        else:
            return num

    def setInfo(self):
        print('[ScheduleDetail] setInfo****')
        if self.data is not None:
            self.comboBox_dong.setCurrentText(self.dong)
            self.spinBox.setValue(self.attend)
            self.event_detail.setText(self.event)
            self.loc_detail.setText(self.location)
            self.manager_detail.setText(self.manager)
            self.phone_detail.setText(self.phone)
            self.comboBox_group.setCurrentText(self.group)

    def setDate(self, date):
        print('[ScheduleDetail] setDate****')
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd")
        self.dateTimeEdit.setMinimumDate(QDate(1900, 1, 1))
        self.dateTimeEdit.setMaximumDate(QDate(2100, 12, 31))

        if date is None:
            self.dateTimeEdit.setDate(QDate(self.year, self.month, self.day))

        else:
            date = datetime.datetime.strptime(date, '%Y%m%d')
            self.dateTimeEdit.setDate(QDate(date.year, date.month, date.day))

    def setTime(self, time):
        print('[ScheduleDetail] setTime****')
        self.timeEdit.setDisplayFormat('hh:mm')
        if type(time) == str:
            time = datetime.datetime.strptime(time, '%H:%M')
        self.timeEdit.setTime(QTime(time.hour, time.minute, 00))

    def getData(self):
        print('[ScheduleDetail] getData****')
        return self.data

    def detailModifyConfirm(self):
        print('[ScheduleDetail] detailModifyConfirm****')
        print(self.timeEdit.time().toString('hh:mm'))
        print(self.comboBox_dong.currentText())
        print(self.spinBox.value())
        data = [self.dateTimeEdit.date().year(),
                self.dateTimeEdit.date().month(),
                self.dateTimeEdit.date().day(),
                self.dateTimeEdit.date().toString('yyyyMMdd'),
                self.timeEdit.time().toString('hh:mm'),
                self.comboBox_dong.currentText(),
                self.event_detail.text(),
                self.loc_detail.text(),
                self.spinBox.value(),
                self.manager_detail.text(),
                self.phone_detail.text(),
                self.comboBox_group.currentText()]
        print(data)
        self.setData(data)
        self.close()

    def scheduleDetailClose(self):
        print('[ScheduleDetail] scheduleDetailClose****')
        self.setData(None)
        self.close()

calendarUi = uic.loadUiType('./resources/monthlyCalendar.ui')[0]
class Calendar(QDialog, QWidget, calendarUi):
    def __init__(self,
                 parent=None,
                 year=datetime.date.today().year,
                 month=datetime.date.today().month,
                 day=datetime.date.today().day,
                 schedule = pd.DataFrame(),
                 dayCol = '연월일',
                 dongCol = '동'):
        print('[Calendar] __init__****')
        super(Calendar, self).__init__(parent)
        self.cal = calendar.Calendar()
        self.cal.setfirstweekday(calendar.SUNDAY)
        self.year = year
        self.month = month
        self.day = day
        self.ymd = datetime.datetime.today().strftime('%Y%m%d')
        self.dayCol = dayCol
        self.dongCol = dongCol
        self.weekDays = ['일','월','화','수','목','금','토']
        self.schedule = schedule
        self.setupUi(self)
        self.monthlySchedule = self.getMonthlySchedule(year=self.year, month=self.month)
        self.initUI()

    def setMonthlySchedule(self, df):
        self.monthlySchedule = df

    def getMonthlySchedule(self, year=datetime.date.today().year, month=datetime.date.today().month):
        print('[Calendar] getMonthlySchedule****')
        ydf = self.schedule[self.schedule['year'] == year]
        mdf = ydf[ydf['month'] == month]
        print(mdf.tail(5))
        return mdf

    def setSchedule(self, df):
        self.schedule = df

    def getSchedule(self):
        return self.schedule

    def setYear(self, year):
        self.year = year

    def getYear(self):
        return self.year

    def setMonth(self, month):
        self.month = month

    def getMonth(self):
        return self.month

    def setDay(self, day):
        self.day = day

    def getDay(self):
        return self.day

    def setWeekDays(self, weekDays):
        self.weekDays = weekDays

    def getWeekDays(self):
        return self.weekDays

    def setDayCol(self, colName):
        self.dayCol = colName

    def getColumns(self):
        return self.dayCol

    def initUI(self):
        print('[Calendar] initUI***')
        print(self.schedule.tail(5))
        self.setCalLayout()
        self.setRightVBox(self.ymd)
        self.yearMonthLabel.setText(f'{self.year}년 {self.month}월')
        self.todayLabel.setText(f'{self.year}.{self.month}.{self.day}')
        self.prevMonth.clicked.connect(lambda : self.setNewCalendar(-1))
        self.nextMonth.clicked.connect(lambda: self.setNewCalendar(1))
        self.weeklyBtn.clicked.connect(self.openWeeklySchedule)
        self.todayBtn.clicked.connect(self.setToday)
        self.homeBtn.clicked.connect(self.goHome)

    def goHome(self):
        print('[Calendar] goHome******')
        home = MyCalendar(self, data=self.schedule)
        self.hide()
        home.show()
        home.exec_()

    def openWeeklySchedule(self):
        print('[Calendar] openWeeklySchedule***')
        self.hide()
        ws = WeekelySchedule(parent=self, data=self.schedule)
        ws.exec_()

    def setCalLayout(self):
        print('[Calendar] setCalLayout****')
        self.clearLayout(self.calendarLayout)
        calendar = self.cal.monthdatescalendar(self.year, self.month)
        calendarDf = pd.DataFrame(calendar, columns=self.weekDays)
        for i in range(len(calendarDf)):
            for idx, day in enumerate(self.weekDays):
                m = calendarDf.loc[i, day].month
                layout = QVBoxLayout()
                if m == self.month:
                    d = str(calendarDf.loc[i, day].day)
                    if len(d) < 2:
                        d = f'0{d}'
                    layout = self.setSchedule(d, layout)
                    if layout.count() < 5:
                        print(layout.count())
                        flag = True
                        while flag:
                            layout.addStretch(1)
                            if layout.count() > 4:
                                flag = False
                self.calendarLayout.addLayout(layout, i, idx)

    def setSchedule(self, d, layout):
        print('[Calendar] setSchedule****')
        dayBtn = self.createBtn(d, styleSheet='color: #575e6b; background-color: white; font-size: 13pt;', max=25)
        ymd = self.getYMD(self.year, self.month, d)
        dayBtn.clicked.connect(lambda checked: self.setRightVBox(ymd))
        layout.addWidget(dayBtn)
        for i in self.monthlySchedule.index:
            if ymd == self.monthlySchedule.loc[i, self.dayCol]:
                if layout.count() > 3:
                    cnt = len(self.monthlySchedule[self.monthlySchedule[self.dayCol] == ymd]) - 3
                    moreBtn = self.createBtn(name=f'{cnt} more +', styleSheet="color: #f56358; background-color: white; font-size: 9pt;")
                    moreBtn.clicked.connect(lambda checked : self.seeAll(ymd, layout))
                    layout.addWidget(moreBtn)
                    return layout

                else:
                    scheduleBtn = self.createBtn(str(self.monthlySchedule.loc[i, self.dongCol]))
                    scheduleBtn.clicked.connect(lambda checked, i=i: self.details(i))
                    layout.addWidget(scheduleBtn)

        return layout

    def createBtn(self, name='btn', styleSheet='font-size: 10pt; border-radius:50px;', min=20, max=23):
        btn = QPushButton(name, self)
        btn.setMaximumHeight(max)
        btn.setMinimumHeight(min)
        btn.setStyleSheet(styleSheet)
        return btn

    def seeAll(self, ymd, layout):
        print('[Calendar] seeAll****')
        if layout.count() > 1:
            self.clearLayout(layout)
        data = self.monthlySchedule[self.monthlySchedule[self.dayCol] == ymd]
        dayBtn = self.createBtn(ymd[6:],
                                styleSheet='color: #575e6b; background-color: white; border: none; font-size: 13pt;',
                                max=25)
        dayBtn.clicked.connect(lambda checked: self.setRightVBox(ymd))
        layout.addWidget(dayBtn)
        for i in data.index:
            scheduleBtn = self.createBtn(name=f'{data.loc[i, self.dongCol]}')
            scheduleBtn.clicked.connect(lambda checked, i=i: self.details(i))
            layout.addWidget(scheduleBtn)

        closeBtn = self.createBtn(name='close', styleSheet="color: #f56358; background-color: white; font-size: 9pt;")
        closeBtn.clicked.connect(lambda checked: self.closeLayout(ymd, layout))
        layout.addWidget(closeBtn)

    def closeLayout(self, ymd, layout):
        print('[Calendar] closeLayout****')
        if layout.count() > 1:
            self.clearLayout(layout)
        data = self.monthlySchedule[self.monthlySchedule[self.dayCol] == ymd]
        dayBtn = self.createBtn(ymd[6:],
                                styleSheet='color: #575e6b; background-color: white; border: none; font-size: 13pt;',
                                max=25)
        dayBtn.clicked.connect(lambda checked: self.setRightVBox(ymd))
        layout.addWidget(dayBtn)
        for i in range(3):
            scheduleBtn = self.createBtn(name=str(data.loc[data.index[i], self.dongCol]))
            scheduleBtn.clicked.connect(lambda checked: self.details(i))
            layout.addWidget(scheduleBtn)

        moreBtn = self.createBtn(name=f'{len(data)-3} more +', styleSheet="color: #f56358; background-color: white; font-size: 9pt;")
        moreBtn.clicked.connect(lambda checked: self.seeAll(ymd, layout))
        layout.addWidget(moreBtn)

    def setRightVBox(self, ymd):
        print('[Calendar] setRightVBox****')
        print(ymd)
        self.clearLayout(self.vLayout)
        self.todayLabel.setText(f'{ymd[:4]}.{ymd[4:6]}.{ymd[6:]}')
        todaySchedule = self.monthlySchedule[self.monthlySchedule[self.dayCol] == ymd]
        print(todaySchedule)
        for i in todaySchedule.index:
            scheduleLabel = QLabel(f"- {todaySchedule.loc[i, '행사명']}")
            scheduleLabel.setStyleSheet('font-size: 9pt;')
            self.vLayout.addWidget(scheduleLabel)

        addBtn = self.createBtn(name='+', styleSheet='border: 1px dotted #575e6b; font-size: 12px;', max=40)
        addBtn.clicked.connect(lambda : self.addSchedule(ymd))
        self.vLayout.addWidget(addBtn)

    def getYMD(self, year, month, day):
        print('[Calendar] getYMD****')
        month = self.getZero(month)
        day = self.getZero(day)
        ymd = f'{year}{month}{day}'
        return ymd

    def addSchedule(self, ymd):
        print('[Calendar] addSchedule****')
        sd = ScheduleDetail(parent=self, date=ymd)
        sd.exec_()
        data = sd.getData()
        if data is not None:
            print(data)
            data.insert(0, len(self.schedule))
            self.schedule.loc[len(self.schedule)] = data
            self.monthlySchedule.loc[len(self.monthlySchedule)] = data
            print(self.schedule.tail(3))
            print(self.monthlySchedule.tail(3))
        self.setRightVBox(ymd)
        self.setCalLayout()

    def delSchedule(self, idx):
        print('[Calendar] delSchedule****')
        self.schedule = self.schedule.drop(index=idx)
        self.monthlySchedule = self.monthlySchedule.drop(index=idx)
        self.setCalLayout()
        self.setToday()

    def modifySchedule(self, idx):
        print('[Calendar] modifyForm****')
        ymd = datetime.datetime.today().strftime('%Y%m%d')
        data = self.monthlySchedule.iloc[idx].to_list()[1:]
        sd = ScheduleDetail(parent=self, data=data, date=ymd)
        sd.exec_()
        data = sd.getData()
        print(data)
        print(idx)
        if data is not None:
            self.modifyData(data, idx)
        self.setCalLayout()
        self.details(idx)

    def modifyData(self, data, idx):
        print('[Calendar] modifyData****')
        data.insert(0, idx)
        print(data)
        for i, col in enumerate(self.monthlySchedule.columns.to_list()):
            print(f'{col}:{data[i]}')
            self.monthlySchedule.loc[idx, col] = data[i]

    def details(self, i):
        print('[Calendar] details****')
        self.clearLayout(self.vLayout)
        ymd = self.monthlySchedule.loc[i, self.dayCol]
        self.todayLabel.setText(f'{ymd[:4]}.{ymd[4:6]}.{ymd[6:]}')
        grid = QGridLayout()
        grid.addWidget(QLabel('시간'), 0, 0)
        grid.addWidget(QLabel('동'), 0, 1)
        grid.addWidget(QLabel(f'{self.monthlySchedule.loc[i, "시간"]}'), 1, 0)
        grid.addWidget(QLabel(f'{self.monthlySchedule.loc[i, "동"]}'), 1, 1)
        self.vLayout.addLayout(grid)

        self.vLayout.addWidget(QLabel('행사명'))
        txt = self.txtCutDown(self.monthlySchedule.loc[i, "행사명"], 15)
        self.vLayout.addWidget(QLabel(f'{txt}'))

        self.vLayout.addWidget(QLabel('장소'))
        self.vLayout.addWidget(QLabel(f'{self.monthlySchedule.loc[i, "장소"]}'))

        grid2 = QGridLayout()
        grid2.addWidget(QLabel('단체'), 0, 0)
        grid2.addWidget(QLabel(f'{self.monthlySchedule.loc[i, "단체"]}'), 1, 0)
        grid2.addWidget(QLabel('참석인원'), 0, 1)
        grid2.addWidget(QLabel(f'{self.monthlySchedule.loc[i, "참석인원"]}'), 1, 1)
        self.vLayout.addLayout(grid2)

        grid3 = QGridLayout()
        grid3.addWidget(QLabel('담당자'), 0, 0)
        grid3.addWidget(QLabel(f'{self.monthlySchedule.loc[i, "담당자"]}'),1, 0)
        grid3.addWidget(QLabel('연락처'), 0, 1)
        grid3.addWidget(QLabel(f'{self.monthlySchedule.loc[i, "연락처"]}'), 1, 1)
        self.vLayout.addLayout(grid3)

        modifyBtn = self.createBtn(name='수정', max=35)
        modifyBtn.clicked.connect(lambda : self.modifySchedule(i))
        deleteBtn = self.createBtn(name='삭제', max=35)
        deleteBtn.clicked.connect(lambda : self.delSchedule(i))
        hbox = QHBoxLayout()
        hbox.addWidget(modifyBtn)
        hbox.addWidget(deleteBtn)
        self.vLayout.addLayout(hbox)

    def txtCutDown(self, txt, length=20):
        print("[Calendar] txtCutDown****")
        if len(txt) > length:
            txt = txt[:length] + '...'
        return txt

    def setToday(self):
        print('[Calendar] setToday****')
        self.clearLayout(self.vLayout)
        ymd = datetime.datetime.today().strftime('%Y%m%d')
        self.setRightVBox(ymd)

    def calendarDf(self):
        print('[Calendar] calendarDf****')
        calendar = self.cal.monthdatescalendar(self.year, self.month)
        calendarDf = pd.DataFrame(calendar, columns=self.weekDays)
        for i in range(len(calendarDf)):
            for idx, day in enumerate(self.weekDays):
                m = calendarDf.loc[i, day].month
                print(m)
                print(self.month)
                if m == self.month:
                    calendarDf.loc[i, day] = calendarDf.loc[i, day].day
                else:
                    calendarDf.loc[i, day] = ''

        model = PandasModel(calendarDf)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setAlternatingRowColors(True)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setModel(model)
        self.tableView.show()

    def clearLayout(self, layout):
        print('[Calendar] clearLayout***')
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    def layoutClear(self, layout):
        print('[Calendar] layoutClear***')
        for i in reversed(range(layout.count())):
            if layout.takeAt(i) is not None:
                layout.removeItem(layout.itemAt(i))

    def setNewCalendar(self, num):
        print('[Calendar] setNewCalendar***')
        self.setYearMonth(num)
        self.yearMonthLabel.setText(f'{self.year}년 {self.month}월')
        self.todayLabel.setText(f'{self.year}.{self.getZero(self.month)}.01')
        self.monthlySchedule = self.getMonthlySchedule(self.year, self.month)
        self.setCalLayout()
        ymd = self.getYMD(self.year, self.month, 1)
        self.setRightVBox(ymd)

    def getZero(self, num):
        print('[Calendar] getZero***')
        if len(str(num)) < 2:
            num = f'0{num}'
        return num

    def setYearMonth(self, num):
        print('[Calendar] setYearMonth***')
        self.setMonth(self.month+num)
        if self.month > 12:
            self.setMonth(1)
            self.setYear(self.year + 1)
        elif self.month < 1:
            self.setMonth(12)
            self.setYear(self.year - 1)


weeklyScheduleUI = uic.loadUiType('./resources/weeklySchedule.ui')[0]
class WeekelySchedule(QDialog, QWidget, weeklyScheduleUI):
    def __init__(self, parent=None, data=pd.DataFrame):
        super(WeekelySchedule, self).__init__(parent)
        print(data)
        self.schedule = data
        self.setupUi(self)
        self.cal = calendar.Calendar()
        self.cal.setfirstweekday(calendar.SUNDAY)
        self.year = datetime.date.today().year
        self.month = datetime.date.today().month
        self.ymdColName = '연월일'
        self.eventColName = '행사명'
        self.weekDays = ['일', '월', '화', '수', '목', '금', '토']
        self.initUI()
        self.show()

    def initUI(self):
        self.initSchedule(datetime.date.day)
        self.homeBtn.clicked.connect(self.goHome)
        self.monthlyBtn.clicked.connect(self.openCalendar)

    def goHome(self):
        print('[Calendar] goHome******')
        home = MyCalendar(self, data=self.schedule)
        self.hide()
        home.show()
        home.exec_()

    def getThisWeek(self, day):
        cal = self.cal.monthdatescalendar(self.year, self.month)
        calDf = pd.DataFrame(cal, columns=self.weekDays)
        for i in range(len(calDf)):
            for d in self.weekDays:
                if calDf.loc[i, d].day == day:
                    print(calDf.loc[i][0].strftime('%Y%m%d'))
                    return calDf.loc[i]

    def initSchedule(self, day):
        thisWeek = self.getThisWeek(day)
        for i in range(len(self.data)):
            for idx, day in enumerate(thisWeek):
                if day == self.data.loc[i, self.ymdColName]:
                    btn = QPushButton(self.data.loc[i, self.eventColName], self)




    def openCalendar(self):
        print('__main__[MyCalendar] initCalendar***')
        cal = Calendar(parent=self, schedule=self.schedule)
        self.hide()
        cal.exec_()
        data = cal.getSchedule()
        if data is not None and data.empty is not True:
            print('outCalendar')
            self.setSchedule(data)
            self.setToday()

saUi = uic.loadUiType('./resources/scheduleAnalysis.ui')[0]
class ScheduleAnalysis(QDialog, QWidget, saUi):
    def __init__(self, parent=None, data=pd.DataFrame,
                 dongColName = '동',
                 colName = '단체'):
        print('[ScheduleAnalysis] __init__******')
        super(ScheduleAnalysis, self).__init__(parent)
        self.data = data
        self.col1 = colName
        self.labels1 = []
        self.color = ['#beadff','#c6b9fa','#e0daf7','#91a8fa','#b1c1fc','#dce3fc','#8ae3b1','#b1e6c8','#d9fae8','#f5989c','#fcbdc0','#fce8e9','#7fb0aa']
        self.dongColName = dongColName
        self.minDay = ''
        self.maxDay = ''
        self.geojson = json.load(open('./resources/yuseongGeoJsonFile.geojson', encoding='utf-8'))
        self.dong_cd = {'진잠동': '3020052000',
                        '온천1동': '3020053000',
                        '원신흥동': '3020061000',
                        '온천2동': '3020054000',
                        '노은1동': '3020054600',
                        '노은2동': '3020054700',
                        '노은3동': '3020054800',
                        '신성동': '3020055000',
                        '전민동': '3020057000',
                        '구즉동': '3020058000',
                        '관평동': '3020060000',
                        '학하동': '3020052600',
                        '상대동': '3020052700'}
        self.ydmColName = '연월일'

        self.setupUi(self)
        self.initUi()
        self.show()

    def initUi(self):
        print('[ScheduleAnalysis] initUi******')
        self.setMinMaxDay(self.data)
        self.setLabels1(list(self.data[self.col1].unique()))
        self.setPie(self.data, self.col1, self.labels1)
        # print(QUrl.fromLocalFile('./resources/ysMap.html'))
        # self.webEngineView.load(QUrl.fromLocalFile('C:/chaeun/scheduleProgram/resources/ysMap.html'))
        self.setMap(self.data, self.dongColName)
        self.homeBtn.clicked.connect(self.goHome)
        self.settingsBtn.clicked.connect(self.openSettings)

    def getData(self):
        return self.data

    def setMinMaxDay(self, data):
        print('[ScheduleAnalysis] setMinMaxDay******')
        if data.empty is not True:
            print('[ScheduleAnalysis] setMinMaxDay:::set')
            min = str(data[self.ydmColName].min())
            max = str(data[self.ydmColName].max())
            self.setMinDay(min)
            self.setMaxDay(max)
        else:
            print('[ScheduleAnalysis] setMinMaxDay:::data.empty!::::setting_fail')
            min = self.minDay
            max = self.maxDay
        return min, max

    def setPie(self, df, colName, labels):
        print('[ScheduleAnalysis] setPie******')
        cnt = self.getCnt(df, colName, labels)
        self.drowPie(cnt, labels)

    def getCnt(self, df, colName, labels):
        print('[ScheduleAnalysis] getCnt******')
        cnt = np.zeros(len(labels), dtype=int)
        for d in df[colName]:
            for idx, item in enumerate(labels):
                if item in d:
                    cnt[idx] += 1
        print(cnt)
        return cnt

    def drowPie(self, x, labels):
        print('[ScheduleAnalysis] drowPie******')
        fig = Figure(figsize=(5,5))
        plt.rc('font', family='gulim')
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        fig.clear()
        ax = fig.add_subplot(111)
        ax.pie(x=x, labels=labels,
               startangle=90,
               # autopct=lambda p: '{:.2f}%'.format(p),
               wedgeprops=dict(width=0.5),
               colors=self.color)
        self.vGraphLayout2.addWidget(toolbar)
        self.vGraphLayout2.addWidget(canvas)
        canvas.draw()

    def getCntDf(self, df, colName):
        print('[ScheduleAnalysis] visitCnt******')
        labels = self.data[colName].unique()
        cnt = self.getCnt(df, colName, labels)
        df = pd.DataFrame({colName: labels, 'cnt': cnt})
        for idx, d in enumerate(df[colName]):
            for k in self.dong_cd.keys():
                if d == k:
                    df.loc[idx, 'adm_cd2'] = self.dong_cd[k]
        return df

    def setMap(self, df, colName):
        print('[ScheduleAnalysis] setMap******')
        data = self.getCntDf(df, colName)
        self.setGeojson(self.setTxtBox(self.geojson, data))
        self.drowMap2(data)

    def drowMap(self, df):
        print('[ScheduleAnalysis] drowMap******')
        fig = px.choropleth(df, geojson=self.geojson,
                            locations='adm_cd2',
                            color='cnt',
                            color_continuous_scale='Blues',
                            featureidkey='properties.adm_cd2')
        fig.update_geos(fitbounds='locations', visible=False)
        fig.update_layout(title_text='행정동별 방문횟수', title_font_size=20)
        fig.write_html('./resources/ysDongFig.html')
        self.webEngineView.load(QUrl.fromLocalFile(os.getcwd()+'\\resources\\ysDongFig.html'))

    def drowMap2(self, df):
        print('[ScheduleAnalysis] drowMap2******')
        map = folium.Map(location=[36.3623035, 127.3560786], titles='yuseongMap', zoom_start=11)
        print(0)
        choropleth = folium.Choropleth(
            geo_data=self.geojson,
            name='yuseong',
            data=df,
            columns=('adm_cd2', 'cnt'),
            fill_color='BuPu',
            fill_opacity=0.7,
            line_opacity=0.5,
            legend_name='visit',
            key_on='feature.properties.adm_cd2'
        ).add_to(map)
        plugins.Fullscreen(position='topright',
                           title='Cilck to Expand',
                           title_cancel='Click to Exit',
                           force_separate_button=True).add_to(map)
        plugins.MousePosition().add_to(map)

        choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['tooltip1'], labels=False))
        # title_html = '<h3 align="center" style="font-size:20px"><b>동별 방문 횟수</b></h3>'
        # map.get_root().html.add_child(folium.Element(title_html))
        folium.LayerControl().add_to(map)

        map.save('./resources/ysMap.html')
        self.webEngineView.load(QUrl.fromLocalFile(os.getcwd()+'\\resources\\ysMap.html'))

    def setTxtBox(self, geojson, df):
        print('[ScheduleAnalysis] setTxtBox******')
        for idx, dic in enumerate(geojson['features']):
            id = dic['properties']['adm_cd2']
            dong_nm = df[df['adm_cd2']==id].iloc[0]['동']
            cnt = df[df['adm_cd2']==id].iloc[0]['cnt']
            txt = f'<b><h4>{dong_nm}&nbsp;{cnt}회 방문</h4></b>'

            geojson['features'][idx]['properties']['tooltip1'] = txt

        return geojson

    def setGeojson(self, geojoson):
        print('[ScheduleAnalysis] setGeojson******')
        self.geojson = geojoson

    def getGeojson(self):
        print('[ScheduleAnalysis] getGeojson******')
        return self.geojson

    def goHome(self):
        print('[ScheduleAnalysis] goHome******')
        home = MyCalendar(self, data=self.data)
        self.hide()
        home.show()
        home.exec_()

    def setData(self, df):
        print('[ScheduleAnalysis] setData******')
        self.data = df

    def getData(self):
        print('[ScheduleAnalysis] getData******')
        return self.data

    def setLabels1(self, li):
        print('[ScheduleAnalysis] setLabels1******')
        self.labels1 = li

    def getLabels1(self):
        print('[ScheduleAnalysis] getLabels1******')
        return self.labels1

    def setMinDay(self, min):
        print('[ScheduleAnalysis] setMinDay******')
        self.minDay = min

    def getMinDay(self):
        return self.minDay

    def setMaxDay(self, max):
        print('[ScheduleAnalysis] setMinDay******')
        self.maxDay = max

    def getMaxDay(self):
        return self.maxDay

    def openSettings(self):
        print('[ScheduleAnalysis] openSettings******')
        s = AnalysisSettings(parent=self, data=self.data,
                             minDay=self.minDay, maxDay=self.maxDay,
                             labels=self.labels1)
        s.exec_()
        data = s.getData()
        if data.empty is not True and data is not None:
            print(s.labels)
            self.setLabels1(s.labels)
            print(self.labels1)
            self.setMinMaxDay(data)
            self.refreshUi(data)

        else:
            print('Settings Fail!!!')

    def refreshUi(self, data):
        print('[ScheduleAnalysis] refreshUi******')
        print(data)
        self.clearLayout(self.vGraphLayout2)
        self.setPie(data, self.col1, self.labels1)
        self.setMap(data, self.dongColName)

    def clearLayout(self, layout):
        print('[Calendar] clearLayout***')
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

settingsUI = uic.loadUiType('./resources/settings.ui')[0]
class AnalysisSettings(QDialog, QWidget, settingsUI):
    def __init__(self, parent=None, data=None, minDay=None, maxDay=None, settings=None):
        print('[AnalysisSettings] __init__****')
        super(AnalysisSettings, self).__init__(parent)
        self.data = data
        self.ydmColName = '연월일'
        self.eventColName = '행사명'
        self.groupColName = '단체'
        self.minDay = minDay
        self.maxDay = maxDay
        self.settings = settings
        self.condi = ''
        self.labels = []
        self.setupUi(self)
        self.initUi()
        self.show()

    def initUi(self):
        print('[AnalysisSettings] initUi****')
        self.initDate()
        print(self.settings)
        self.setLabels(self.settings[self.groupColName].to_list())
        self.setCondiItem(self.labels)
        self.delCondiBtn.clicked.connect(self.delCondiClicked)
        self.addCondiBtn.clicked.connect(self.addBtnClicked)
        self.okBtn.clicked.connect(self.okBtnClicked)
        self.cancelBtn.clicked.connect(self.cancelBtnClicked)

    def setPeriod(self):
        print('[AnalysisSettings] setPeriod****')
        minDay = self.dateTimeEdit1.date().toString('yyyyMMdd')
        maxDay = self.dateTimeEdit2.date().toString('yyyyMMdd')
        self.setMinDay(minDay)
        self.setMaxDay(maxDay)
        df = self.data[self.data[self.ydmColName] >= minDay]
        df = df[df[self.ydmColName] <= maxDay]
        return df

    def initDate(self):
        print('[AnalysisSettings] initDate****')
        if self.minDay is not None and self.maxDay is not None:
            self.setDate(self.minDay, self.maxDay)

        else:
            min, max = self.setDateFromData(self.data)
            self.setMinDay(min)
            self.setMaxDay(max)
            self.setDate(min, max)


    def getDateFromData(self, data):
        print('[AnalysisSettings] getDateFromData****')
        if data.empty or data is None:
            print('Empty Data')
            min = datetime.date.today().strftime('%Y%m01')
            month = datetime.date.today().month + 1
            max = f'{datetime.date.today().year}{month}01'

        else:
            print('[AnalysisSettings] getDateFromData::::set')
            min = str(data[self.ydmColName].min())
            max = str(data[self.ydmColName].max())
        print(min, max)

        return min, max

    def setDate(self, minDay, maxDay):
        print('[AnalysisSettings] setDate****')
        print(minDay, maxDay)
        self.dateTimeEdit1.setCalendarPopup(True)
        self.dateTimeEdit1.setDisplayFormat('yyyy-MM-dd')
        self.dateTimeEdit1.setDate(QDate(int(minDay[:4]), int(minDay[4:6]), int(minDay[6:])))
        self.dateTimeEdit1.setMinimumDate(QDate(1900, 1, 1))
        self.dateTimeEdit1.setMaximumDate(QDate(2100, 12, 31))
        print('*')
        self.dateTimeEdit2.setCalendarPopup(True)
        self.dateTimeEdit2.setDisplayFormat('yyyy-MM-dd')
        self.dateTimeEdit2.setDate(QDate(int(maxDay[:4]), int(maxDay[4:6]), int(maxDay[6:])))
        self.dateTimeEdit2.setMinimumDate(QDate(1900, 1, 1))
        self.dateTimeEdit2.setMaximumDate(QDate(2100, 12, 31))

    def setCondiItem(self, li):
        print('[AnalysisSettings] setCondiItem****')
        print(li)
        self.clearLayout(self.condiRbtnGBox)
        for i, item in enumerate(li):
            if item != 'nan' and item != None:
                globals()[f'rBtn{i}'] = QRadioButton(item, self)
                self.condiRbtnGBox.addWidget(globals()[f'rBtn{i}'], i//2, i%2)
        print('3')

    def addBtnClicked(self):
        print('[AnalysisSettings] addBtnClicked****')
        item = self.lineEdit.text()
        self.labels.append(item)
        print('*')
        self.settings.loc[len(self.settings), self.groupColName] = item
        print('*')
        self.setCondiItem(self.labels)

    def delCondiClicked(self):
        print('[AnalysisSettings] delCondiClicked****')
        for i, item in enumerate(self.labels):
            if globals()[f'rBtn{i}'].isChecked():
                self.labels[i] = None
        print(self.labels)
        self.settings[self.groupColName] = self.labels
        print(self.settings)
        self.setCondiItem(self.labels)

    def setLabels(self, li):
        print('[AnalysisSettings] setLabels****')
        print(li)
        self.labels = li

    def getLabels(self):
        print('[AnalysisSettings] getLabels****')
        return self.labels

    def okBtnClicked(self):
        print('[AnalysisSettings] okBtnClicked****')
        df = self.setPeriod()
        self.setData(df)
        for i, item in enumerate(self.labels):
            if globals()[f'rBtn{i}'].isChecked():
                self.condi = globals()[f'rBtn{i}'].text()
        self.close()

    def cancelBtnClicked(self):
        print('[AnalysisSettings] cancelBtnClicked****')
        self.close()

    def setMinDay(self, min):
        print('[AnalysisSettings] setMinDay****')
        self.minDay = min

    def getMinDay(self):
        print('[AnalysisSettings] getMinDay****')
        return self.minDay

    def setMaxDay(self, max):
        print('[AnalysisSettings] setMaxDay****')
        self.maxDay = max

    def getMaxDay(self):
        print('[AnalysisSettings] getMaxDay****')
        return self.maxDay

    def setData(self, df):
        print('[AnalysisSettings] setData***')
        self.data = df

    def getData(self):
        print('[AnalysisSettings] getData***')
        return self.data

    def clearLayout(self, layout):
        print('[AnalysisSettings] clearLayout***')
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())




if __name__ == '__main__':
    try:
        qapp = QtWidgets.QApplication.instance()
        if not qapp:
            qapp = QtWidgets.QApplication(sys.argv)

        app = MyCalendar()
        app.show()
        app.activateWindow()
        app.raise_()
        qapp.exec()
        df = app.getSchedule()
        df.to_csv('./resources/scheduleDataSaved.csv', encoding='cp949', index=False)

    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        ex.exception_hook(exc_type, exc_value, exc_traceback)
