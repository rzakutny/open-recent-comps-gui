# OPEN RECENT FILES IN GUI
# Created by Radoslav Zakutny 
# 2022

from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import QWidget, QListWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PySide2.QtWidgets import QMessageBox, QListWidgetItem

import nuke
import os.path
import subprocess

class OpenRecentFile(QWidget):
    def __init__(self):
        super(OpenRecentFile, self).__init__()


        # BUTTONS
        self.open_button = QPushButton("Open")
        self.load_button = QPushButton("Load")
        self.reveal_in_finder = QPushButton("Reveal")
        #--------------------------

        # QListWidet
        self.recent_list = BuildRecentList()
        self.recent_list.setDragEnabled(True)

        # Layouts
        buttons_layout = QVBoxLayout()
        recent_list_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        #----------------------------

        # Signal
        self.open_button.clicked.connect(self.open_recent)
        self.reveal_in_finder.clicked.connect(self.explore_selected)
        self.recent_list.itemSelectionChanged.connect(self.set_drag_and_drop_data)
        self.load_button.clicked.connect(self.load_recent)

        # Widgets
        buttons_layout.addWidget(self.open_button)
        buttons_layout.addWidget(self.load_button)
        buttons_layout.addWidget(self.reveal_in_finder)

        recent_list_layout.addWidget(self.recent_list)


        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(recent_list_layout)

        self.setLayout(main_layout)
        self.resize(600,250)
        self.setMinimumSize(600,250)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)


    def open_recent(self):
        current_row = self.recent_list.currentRow()
        if current_row == -1:
            QMessageBox.information(self, "Warning", "No recent file selected ! ")
            return
        data = self.recent_list.item(current_row).data(32)

        try:
            nuke.scriptClose()
        except Exception as e:
            QMessageBox.information(self, "Warning", "Nuke scene save failed !\nError: {}".format(e))
            return
        try:
            nuke.scriptOpen(data)
        except Exception as e:
            QMessageBox.information(self, "Warning", "Opening script failed !:\n{}\nError:{}".format(data,e))
            return

        self.close()

    def load_recent(self):
        current_row = self.recent_list.currentRow()
        if current_row == -1:
            QMessageBox.information(self, "Warning", "No recent file selected ! ")
            return
        data = self.recent_list.item(current_row).data(32)

        try:
            nuke.scriptOpen(data)
        except Exception as e:
            QMessageBox.information(self, "Warning", "Load script failed !:\n{}\nError:{}".format(data,e))
            return     

    def set_drag_and_drop_data(self):
        current_row = self.recent_list.currentRow()
        data = self.recent_list.item(current_row).data(32)
        self.recent_list.mime_dict = {u'text/plain': str(data)}

    def explore_selected(self):
        current_row = self.recent_list.currentRow()

        if current_row == -1:
            QMessageBox.information(self, "Warning", "No recent file selected ! ")
            return

        data = self.recent_list.item(current_row).data(32)
        if data:
            data = os.path.dirname(data)
        if os.path.isdir(data):
            if nuke.env['WIN32']:
                os.startfile(data)
            elif nuke.env['LINUX']:
                subprocess.Popen(['xdg-open', data]) 
            elif nuke.env['MACOS']:
                subprocess.Popen(['open', data])

class BuildRecentList(QListWidget):
    def __init__(self):
        super(BuildRecentList, self).__init__()

        self.data = self.get_data()

        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setAlternatingRowColors(True)
            
        self.set_style_sheet()
        self.populate_recent_list()

        self.setAcceptDrops(True)

        self.mime_dict = {u'text/plain': 'clipboard'}

    def populate_recent_list(self):
        for i in range(len(self.data)):
            name = str(os.path.basename(self.data[i]))
            item = QListWidgetItem(name[:-3]) # get rid off ".nk" extension
            item.setData(32, self.data[i])
            item.setToolTip(self.data[i])
            self.addItem(item)

    def get_data(self):
        data = list()

        for i in range(1,7):
            try:
                data.append(nuke.recentFile(i))
            except Exception as e:
                print(e)
        return data

    def set_style_sheet(self):
        text = open("{}/style.txt".format(os.path.dirname(__file__))).read()
        self.setStyleSheet(text)

    def dragEnterEvent(self, event):
        event.accept()
    
    def dropEvent(self, event):
        mime_dict = {}
        for format in event.mimeData().formats():
            mime_dict[format] = event.mimeData().data(format)
        self.mime_dict = mime_dict
        print(event.mimeData().formats())
    
    def mouseMoveEvent(self, event):
        mimeData = QtCore.QMimeData()
        for format, value in self.mime_dict.iteritems():
            if format not in [u'text/uri-list']:
                mimeData.setData(format, value)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        dropAction = drag.start(QtCore.Qt.MoveAction)

def show_panel():
    show_panel.panel = OpenRecentFile()
    show_panel.panel.show()

