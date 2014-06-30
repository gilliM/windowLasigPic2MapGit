# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Pose(object):
    def setupUi(self, PoseDialog):
        PoseDialog.setObjectName(_fromUtf8("PoseDialog"))
        PoseDialog.resize(648, 383)
        self.gridLayout = QtGui.QGridLayout(PoseDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(PoseDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 4, 1, 1)
        self.frame_2 = QtGui.QFrame(PoseDialog)
        self.frame_2.setMinimumSize(QtCore.QSize(0, 318))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        

        self.XPosFree = QtGui.QRadioButton(self.frame_2)
        self.XPosFree.setObjectName(_fromUtf8("XPosFree"))
        self.XPosFixed = QtGui.QRadioButton(self.frame_2)
        self.XPosFixed.setObjectName(_fromUtf8("XPosFixed"))
        self.XPosGroup = QtGui.QButtonGroup(PoseDialog)
        self.XPosGroup.setObjectName(_fromUtf8("XPosGroup"))
        self.XPosGroup.addButton(self.XPosFixed)
        self.XPosGroup.addButton(self.XPosFree)
        self.gridLayout_2.addWidget(self.XPosFree, 0, 1, 1, 1)
        self.gridLayout_2.addWidget(self.XPosFixed, 0, 2, 1, 1)
        self.YPosFree = QtGui.QRadioButton(self.frame_2)
        self.YPosFree.setObjectName(_fromUtf8("YPosFree"))
        self.YPosGroup = QtGui.QButtonGroup(PoseDialog)
        self.YPosGroup.setObjectName(_fromUtf8("YPosGroup"))
        self.YPosGroup.addButton(self.YPosFree)
        self.YPosFixed = QtGui.QRadioButton(self.frame_2)
        self.YPosFixed.setObjectName(_fromUtf8("YPosFixed"))
        self.YPosGroup.addButton(self.YPosFixed)
        self.gridLayout_2.addWidget(self.YPosFree, 1, 1, 1, 1)
        self.gridLayout_2.addWidget(self.YPosFixed, 1, 2, 1, 1)


        self.ZPosFree = QtGui.QRadioButton(self.frame_2)
        self.ZPosFree.setObjectName(_fromUtf8("ZPosFree"))
        self.ZPosFixed = QtGui.QRadioButton(self.frame_2)
        self.ZPosFixed.setObjectName(_fromUtf8("ZPosFixed"))
        self.ZPoseGroup = QtGui.QButtonGroup(PoseDialog)
        self.ZPoseGroup.setObjectName(_fromUtf8("ZPoseGroup"))
        self.ZPoseGroup.addButton(self.ZPosFixed)
        self.ZPoseGroup.addButton(self.ZPosFree)
        self.gridLayout_2.addWidget(self.ZPosFree, 2, 1, 1, 1)
        self.gridLayout_2.addWidget(self.ZPosFixed, 2, 2, 1, 1)
        
        self.tiltFree = QtGui.QRadioButton(self.frame_2)
        self.tiltFree.setObjectName(_fromUtf8("tiltFree"))
        self.tiltgroup = QtGui.QButtonGroup(PoseDialog)
        self.tiltgroup.setObjectName(_fromUtf8("tiltgroup"))
        self.tiltgroup.addButton(self.tiltFree)
        self.gridLayout_2.addWidget(self.tiltFree, 3, 1, 1, 1)
        self.tiltFixed = QtGui.QRadioButton(self.frame_2)
        self.tiltFixed.setObjectName(_fromUtf8("tiltFixed"))
        self.tiltgroup.addButton(self.tiltFixed)
        self.gridLayout_2.addWidget(self.tiltFixed, 3, 2, 1, 1)
        
        self.headingFree = QtGui.QRadioButton(self.frame_2)
        self.headingFree.setObjectName(_fromUtf8("headingFree"))
        self.headinggroup = QtGui.QButtonGroup(PoseDialog)
        self.headinggroup.setObjectName(_fromUtf8("headinggroup"))
        self.headinggroup.addButton(self.headingFree)
        self.gridLayout_2.addWidget(self.headingFree, 4, 1, 1, 1)
        self.headingFixed = QtGui.QRadioButton(self.frame_2)
        self.headingFixed.setObjectName(_fromUtf8("headingFixed"))
        self.headinggroup.addButton(self.headingFixed)
        self.gridLayout_2.addWidget(self.headingFixed, 4, 2, 1, 1)

        self.swingFree = QtGui.QRadioButton(self.frame_2)
        self.swingFree.setObjectName(_fromUtf8("swingFree"))
        self.gridLayout_2.addWidget(self.swingFree, 5, 1, 1, 1)
        self.swingFixed = QtGui.QRadioButton(self.frame_2)
        self.swingFixed.setObjectName(_fromUtf8("swingFixed"))
        self.swinggroup = QtGui.QButtonGroup(PoseDialog)
        self.swinggroup.setObjectName(_fromUtf8("swinggroup"))
        self.swinggroup.addButton(self.swingFree)
        self.swinggroup.addButton(self.swingFixed)
        self.gridLayout_2.addWidget(self.swingFixed, 5, 2, 1, 1)
        
        self.focalFree = QtGui.QRadioButton(self.frame_2)
        self.focalFree.setObjectName(_fromUtf8("focalFree"))
        self.focalFixed = QtGui.QRadioButton(self.frame_2)
        self.focalFixed.setObjectName(_fromUtf8("focalFixed"))
        self.focalgroup = QtGui.QButtonGroup(PoseDialog)
        self.focalgroup.setObjectName(_fromUtf8("focalgroup"))
        self.focalgroup.addButton(self.focalFixed)
        self.gridLayout_2.addWidget(self.focalFixed, 6, 2, 1, 1)
        self.focalgroup.addButton(self.focalFree)
        self.gridLayout_2.addWidget(self.focalFree, 6, 1, 1, 1)

        self.XPosLine = QtGui.QLineEdit(self.frame_2)
        self.XPosLine.setObjectName(_fromUtf8("XPosLine"))
        self.gridLayout_2.addWidget(self.XPosLine, 0, 4, 1, 1)
        self.YPosLine = QtGui.QLineEdit(self.frame_2)
        self.YPosLine.setObjectName(_fromUtf8("YPosLine"))
        self.gridLayout_2.addWidget(self.YPosLine, 1, 4, 1, 1)
        self.ZPosLine = QtGui.QLineEdit(self.frame_2)
        self.ZPosLine.setObjectName(_fromUtf8("ZPosLine"))
        self.gridLayout_2.addWidget(self.ZPosLine, 2, 4, 1, 1)
        self.tiltLine = QtGui.QLineEdit(self.frame_2)
        self.tiltLine.setObjectName(_fromUtf8("tiltLine"))
        self.gridLayout_2.addWidget(self.tiltLine, 3, 4, 1, 1)
        self.headingLine = QtGui.QLineEdit(self.frame_2)
        self.headingLine.setObjectName(_fromUtf8("headingLine"))
        self.gridLayout_2.addWidget(self.headingLine, 4, 4, 1, 1)
        self.swingLine = QtGui.QLineEdit(self.frame_2)
        self.swingLine.setObjectName(_fromUtf8("swingLine"))
        self.gridLayout_2.addWidget(self.swingLine, 5, 4, 1, 1)
        self.focalLine = QtGui.QLineEdit(self.frame_2)
        self.focalLine.setObjectName(_fromUtf8("focalLine"))
        self.gridLayout_2.addWidget(self.focalLine, 6, 4, 1, 1)

        self.label_2 = QtGui.QLabel(self.frame_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.frame_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 1)
        self.label_5 = QtGui.QLabel(self.frame_2)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_2.addWidget(self.label_5, 3, 0, 1, 1)
        self.label_6 = QtGui.QLabel(self.frame_2)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout_2.addWidget(self.label_6, 4, 0, 1, 1)
        self.label_7 = QtGui.QLabel(self.frame_2)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout_2.addWidget(self.label_7, 5, 0, 1, 1)
        self.label_8 = QtGui.QLabel(self.frame_2)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout_2.addWidget(self.label_8, 6, 0, 1, 1)
   
        self.gridLayout.addWidget(self.frame_2, 1, 1, 1, 4)
        self.commandLinkButton = QtGui.QCommandLinkButton(PoseDialog)
        self.commandLinkButton.setObjectName(_fromUtf8("commandLinkButton"))
        self.gridLayout.addWidget(self.commandLinkButton, 2, 2, 1, 1)
        self.XPosFree.setChecked(True)
        self.YPosFree.setChecked(True)
        self.ZPosFree.setChecked(True)
        self.tiltFree.setChecked(True)
        self.headingFree.setChecked(True)
        self.swingFree.setChecked(True)
        self.focalFree.setChecked(True)
        
        self.reportButton = QtGui.QPushButton (PoseDialog)
        self.reportButton.setObjectName(_fromUtf8("reportButton"))
        self.gridLayout.addWidget(self.reportButton, 2, 3, 1, 1)
        

        self.retranslateUi(PoseDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), PoseDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), PoseDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PoseDialog)
        
        self.XPosLine.setReadOnly(True)
        self.XPosFixed.toggled.connect(self.XPosFixedclicked)
        self.XPosFree.toggled.connect(self.XPosFreeclicked)
        
        self.YPosLine.setReadOnly(True)
        self.YPosFixed.toggled.connect(self.YPosFixedclicked)
        self.YPosFree.toggled.connect(self.YPosFreeclicked)
        
        self.ZPosLine.setReadOnly(True)
        self.ZPosFixed.toggled.connect(self.ZPosFixedclicked)
        self.ZPosFree.toggled.connect(self.ZPosFreeclicked)
        
        self.headingLine.setReadOnly(True)
        self.headingFixed.toggled.connect(self.headingFixedclicked)
        self.headingFree.toggled.connect(self.headingFreeclicked)
        
        self.tiltLine.setReadOnly(True)
        self.tiltFixed.toggled.connect(self.tiltFixedclicked)
        self.tiltFree.toggled.connect(self.tiltFreeclicked)
        
        self.swingLine.setReadOnly(True)
        self.swingFixed.toggled.connect(self.swingFixedclicked)
        self.swingFree.toggled.connect(self.swingFreeclicked)
        
        self.focalLine.setReadOnly(True)
        self.focalFixed.toggled.connect(self.focalFixedclicked)
        self.focalFree.toggled.connect(self.focalFreeclicked)


    def focalFixedclicked(self):
        if self.focalFixed.isChecked():
            self.focalLine.setReadOnly(False) 
    def focalFreeclicked(self):
        if self.focalFree.isChecked():
            self.focalLine.setText('')
            self.focalLine.setReadOnly(True)
    def swingFixedclicked(self):
        if self.swingFixed.isChecked():
            self.swingLine.setReadOnly(False) 
    def swingFreeclicked(self):
        if self.swingFree.isChecked():
            self.swingLine.setText('')
            self.swingLine.setReadOnly(True)
    def tiltFixedclicked(self):
        if self.tiltFixed.isChecked():
            self.tiltLine.setReadOnly(False) 
    def tiltFreeclicked(self):
        if self.tiltFree.isChecked():
            self.tiltLine.setText('')
            self.tiltLine.setReadOnly(True)
    def headingFixedclicked(self):
        if self.headingFixed.isChecked():
            self.headingLine.setReadOnly(False) 
    def headingFreeclicked(self):
        if self.headingFree.isChecked():
            self.headingLine.setText('')
            self.headingLine.setReadOnly(True)
    def ZPosFixedclicked(self):
        if self.ZPosFixed.isChecked():
            self.ZPosLine.setReadOnly(False) 
    def ZPosFreeclicked(self):
        if self.ZPosFree.isChecked():
            self.ZPosLine.setText('')
            self.ZPosLine.setReadOnly(True)
    def YPosFixedclicked(self):
        if self.YPosFixed.isChecked():
            self.YPosLine.setReadOnly(False) 
    def YPosFreeclicked(self):
        if self.YPosFree.isChecked():
            self.YPosLine.setText('')
            self.YPosLine.setReadOnly(True)
    def XPosFixedclicked(self):
        if self.XPosFixed.isChecked():
            self.XPosLine.setReadOnly(False)
    def XPosFreeclicked(self):
        if self.XPosFree.isChecked():
            self.XPosLine.setText('')
            self.XPosLine.setReadOnly(True)
            
    def retranslateUi(self, PoseDialog):
        PoseDialog.setWindowTitle(_translate("PoseDialog", "Pose estimation", None))
        
        self.XPosFree.setText(_translate("PoseDialog", "Free", None))
        self.XPosFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.YPosFree.setText(_translate("PoseDialog", "Free", None))
        self.YPosFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.ZPosFree.setText(_translate("PoseDialog", "Free", None))
        self.ZPosFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.tiltFree.setText(_translate("PoseDialog", "Free", None))
        self.tiltFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.headingFree.setText(_translate("PoseDialog", "Free", None))
        self.headingFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.swingFree.setText(_translate("PoseDialog", "Free", None))
        self.swingFixed.setText(_translate("PoseDialog", "Fixed", None))
        self.focalFree.setText(_translate("PoseDialog", "Free", None))
        self.focalFixed.setText(_translate("PoseDialog", "Fixed", None))

        self.label_2.setText(_translate("PoseDialog", "X Position [m]", None))
        self.label_3.setText(_translate("PoseDialog", "Y Position [m]", None))
        self.label_4.setText(_translate("PoseDialog", "Z Position [m]", None))
        self.label_5.setText(_translate("PoseDialog", "tilt [°]", None))
        self.label_6.setText(_translate("PoseDialog", "heading [°]", None))
        self.label_7.setText(_translate("PoseDialog", "swing [°]", None))
        self.label_8.setText(_translate("PoseDialog", "focal [pixel]", None))
        self.reportButton.setText(_translate("PoseDialog", "Report on GCPs", None))

        self.commandLinkButton.setText(_translate("PoseDialog", "Pose Estimation", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    PoseDialog = QtGui.QDialog()
    ui = Ui_PoseDialog()
    ui.setupUi(PoseDialog)
    PoseDialog.show()
    sys.exit(app.exec_())

