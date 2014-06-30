"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from ui_label_settings import Ui_LabelSetting
from functools import partial

class label_dialog(QtGui.QDialog):
    def __init__(self, labelSet):
        QtGui.QDialog.__init__(self)
        self.ui = Ui_LabelSetting()
        self.ui.setupUi(self, labelSet)
        self.center()
        self.ui.colorButton.clicked.connect(partial(self.showColor, self.ui.colorButton))
        self.ui.fontButton.clicked.connect(self.showFont)
        
        self.font = labelSet[1]
        self.ui.label_2.setFont(labelSet[1])
        self.ui.doubleSpinBox.setValue(labelSet[2])
        self.ui.doubleSpinBox_2.setValue(labelSet[3])

                
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def showFont(self):
        font, ok = QtGui.QFontDialog.getFont()
        if ok:
            self.font = font
            self.ui.label_2.setFont(font)
        
    def showColor(self, frame):
        # Open the PyQt dialog box
        col = QtGui.QColorDialog.getColor()
        if col.isValid():
            # color the button
            frame.setStyleSheet("QWidget { background-color: %s }" % col.name())
            # color the font
            self.ui.label_2.setStyleSheet('QLabel {color: %s }' % col.name())

