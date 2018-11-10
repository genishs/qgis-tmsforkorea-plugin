# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_openlayers_ovwidget.ui'
#
# Created: Mon Mar 24 18:00:50 2014
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKitWidgets

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(457, 467)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lytEnableMap = QtWidgets.QHBoxLayout()
        self.lytEnableMap.setObjectName(_fromUtf8("lytEnableMap"))
        self.checkBoxEnableMap = QtWidgets.QCheckBox(Form)
        self.checkBoxEnableMap.setChecked(False)
        self.checkBoxEnableMap.setObjectName(_fromUtf8("checkBoxEnableMap"))
        self.lytEnableMap.addWidget(self.checkBoxEnableMap)
        self.comboBoxTypeMap = QtWidgets.QComboBox(Form)
        self.comboBoxTypeMap.setObjectName(_fromUtf8("comboBoxTypeMap"))
        self.lytEnableMap.addWidget(self.comboBoxTypeMap)
        self.pbAddRaster = QtWidgets.QPushButton(Form)
        self.pbAddRaster.setText(_fromUtf8(""))
        self.pbAddRaster.setObjectName(_fromUtf8("pbAddRaster"))
        self.lytEnableMap.addWidget(self.pbAddRaster)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.lytEnableMap.addItem(spacerItem)
        self.verticalLayout_2.addLayout(self.lytEnableMap)
        self.lbStatusRead = QtWidgets.QLabel(Form)
        self.lbStatusRead.setText(_fromUtf8(""))
        self.lbStatusRead.setTextFormat(QtCore.Qt.PlainText)
        self.lbStatusRead.setObjectName(_fromUtf8("lbStatusRead"))
        self.verticalLayout_2.addWidget(self.lbStatusRead)
        self.webViewMap = QtWebKitWidgets.QWebView(Form)
        self.webViewMap.setObjectName(_fromUtf8("webViewMap"))
        self.verticalLayout_2.addWidget(self.webViewMap)
        self.lytHideCross = QtWidgets.QHBoxLayout()
        self.lytHideCross.setObjectName(_fromUtf8("lytHideCross"))
        self.checkBoxHideCross = QtWidgets.QCheckBox(Form)
        self.checkBoxHideCross.setObjectName(_fromUtf8("checkBoxHideCross"))
        self.lytHideCross.addWidget(self.checkBoxHideCross)
        self.pbRefresh = QtWidgets.QPushButton(Form)
        self.pbRefresh.setText(_fromUtf8(""))
        self.pbRefresh.setObjectName(_fromUtf8("pbRefresh"))
        self.lytHideCross.addWidget(self.pbRefresh)
        self.pbSaveImg = QtWidgets.QPushButton(Form)
        self.pbSaveImg.setText(_fromUtf8(""))
        self.pbSaveImg.setObjectName(_fromUtf8("pbSaveImg"))
        self.lytHideCross.addWidget(self.pbSaveImg)
        self.pbCopyKml = QtWidgets.QPushButton(Form)
        self.pbCopyKml.setText(_fromUtf8(""))
        self.pbCopyKml.setObjectName(_fromUtf8("pbCopyKml"))
        self.lytHideCross.addWidget(self.pbCopyKml)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.lytHideCross.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.lytHideCross)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form"))
        self.checkBoxEnableMap.setText(QtWidgets.QApplication.translate("Form", "Enable map"))
        self.pbAddRaster.setToolTip(QtWidgets.QApplication.translate("Form", "Add map"))
        self.checkBoxHideCross.setText(QtWidgets.QApplication.translate("Form", "Hide cross in map"))
        self.pbRefresh.setToolTip(QtWidgets.QApplication.translate("Form", "Refresh map"))
        self.pbSaveImg.setToolTip(QtWidgets.QApplication.translate("Form", "Save this image"))
        self.pbCopyKml.setToolTip(QtWidgets.QApplication.translate("Form", "Copy rectangle (KML) of map to clipboard"))

from PyQt5 import QtWebKit
