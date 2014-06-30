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
from qgis.core import *
from qgis.gui import *
from ui_drapping import Ui_drapping
from ortho import viewOrtho_class

class drappingMain(QtGui.QMainWindow):
    # This Mainwindow is used to set the bounding box and the cell size of the raster extracted
    # from the drapped picture on the DEM.
    def __init__(self, pointBuffer, picture_name,
                                          modelview,
                                          projection,
                                          viewport,
                                          texture,
                                          crs,
                                          demName,
                                          isFrameBufferSupported,
                                          parent = None):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_drapping()
        self.ui.setupUi(self)
        self.pointBuffer = pointBuffer
        self.modelview = modelview
        self.projection = projection
        self.viewport = viewport
        self.texture = texture
        self.picture_name = picture_name
        self.crs = crs
        self.demName = demName
        self.isFrameBufferSupported = isFrameBufferSupported
        self.viewOrtho = viewOrtho_class(pointBuffer, picture_name,
                                          modelview,
                                          projection,
                                          viewport,
                                          texture)
        
        self.viewOrtho.makeCurrent()
        self.setCentralWidget(self.viewOrtho)
        self.resolution = QDesktopWidget().screenGeometry()
        size = [0,0]
        size[1] = self.resolution.height()/2
        l_nord =  pointBuffer.l_nord
        self.l_nord = l_nord
        l_est =  pointBuffer.l_est
        self.l_est = l_est
        ratio =  l_nord /float(l_est)
        size[0] = size[1]/ratio
        self.resize(size[0]+200,size[1])
        
        self.viewOrtho.getBound.connect(self.displayBound)
        self.ui.saveButton.clicked.connect(self.saveOrtho)
    
    def displayBound(self, box):
        self.ui.label_3.setText(str(-round(box[0][0],0)))
        self.ui.label_4.setText(str(round(box[1][1],0)))
        self.ui.label_5.setText(str(round(box[0][1],0)))
        self.ui.label_6.setText(str(-round(box[1][0],0)))
    
    def saveOrtho(self):
        reply = QtGui.QMessageBox.question(self, 'Message',
        "Continue with the current purple bounding box ?", QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QMessageBox.Yes:
            meterPerPixel = self.ui.spinBox.value()
            totPixN = (self.l_nord/meterPerPixel)*self.viewOrtho.resolution
            totPixE = (self.l_est/meterPerPixel)*self.viewOrtho.resolution
            self.viewOrtho.getViewPortZoom()
            orthoSavedParam = [totPixN, totPixE, self.viewOrtho.ParamViewport]
            a = self.viewOrtho.getMaxBufferSize()
            
            try:
                if not self.isFrameBufferSupported:
                    QMessageBox.warning(self, "OpenGL Version","The current openGL Version does not support frame buffer.\n Raster with less pixel than screen can be saved only.")
                    if self.resolution.height() < totPixN or self.resolution.width() < totPixE:
                        raise ValueError
                if totPixE > a or totPixN > a:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Value Error","Failed to save raster.\nConsider increasing the resolution.")
            else:
                self.orthoSaveInstance = viewOrtho_class(self.pointBuffer,
                                                  self.picture_name,
                                                  self.modelview,
                                                  self.projection,
                                                  self.viewport,
                                                  self.texture,
                                                  orthoSavedParam,
                                                  self.crs,
                                                  meterPerPixel,
                                                  self.demName,
                                                  self.isFrameBufferSupported)
                
                if not self.isFrameBufferSupported:
                    totPixN = int(orthoSavedParam[0])
                    totPixE = int(orthoSavedParam[1])
                    self.orthoSaveInstance.show()
                    self.orthoSaveInstance.resize(totPixE,totPixN)
                    self.orthoSaveInstance.resizeGL(totPixE,totPixN)
                    self.orthoSaveInstance.updateGL()
                self.orthoSaveInstance.saveOrtho()
                self.orthoSaveInstance.close()   
                self.close()         
       