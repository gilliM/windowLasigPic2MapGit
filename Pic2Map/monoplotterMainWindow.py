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

"""
 The monoplotter consists in the final step of the plugin.
 Both pose estimation approaches launch this code. 
 The background principle is quite easy: The landscape picture
 is displayed in a QGLwidget. The DEM is draw inside, and the camera
 is set according to the pose estimation. Then the DEM is set as
 transparent. Now, if you click on the window, you think you
 click on the picture, but in fact, you click on the DEM.
"""

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from qgis.core import *
from qgis.gui import *
from QGL_monoplotter import QGLMonoplotter
from ui_monoplotter import Ui_Monoplotter
from drapping import drappingMain
from numpy import zeros, concatenate, dot, linalg, pi, arctan2, ones, array
from ui_buffering import Ui_progressBar
from labelSettingsDialog import label_dialog
from measure3D import mesure3DDialog
from ortho import viewOrtho_class
import os
import ogr
from osgeo import gdal, osr

class MonoplotterMainWindow(QtGui.QMainWindow):
    openOrtho = pyqtSignal()
    clearMapTool= pyqtSignal()
    def __init__(self, iface, pointBuffer, picture_name, ParamPose, dem_box, cLayer,pathToData, crs,demName,isFrameBufferSupported):
        QtGui.QMainWindow.__init__(self)
        self.iface = iface
        self.cLayer = cLayer
        self.dem_box = dem_box
        self.ParamPose = ParamPose
        self.picture_name = picture_name
        self.pointBuffer = pointBuffer
        self.pathToData = pathToData
        self.crs = crs
        self.demName = demName
        self.isFrameBufferSupported = isFrameBufferSupported
        self.useOrthoImage = isinstance(self.pointBuffer.m_normal,int)
        self.haveMask = False
        self.polygonActivated = False
        
        self.ui = Ui_Monoplotter()
        self.qgl_window = QGLMonoplotter(pointBuffer, picture_name,ParamPose)
        
        img = QImage(picture_name)
        resolution = QDesktopWidget().screenGeometry()
        size = [0,0]
        size[1] = resolution.height()/2
        self.ratio = img.width()/float( img.height())
        size[0] = int(self.ratio*size[1])
        self.ui.setupUi(self, self.useOrthoImage)
        
        self.setCentralWidget(self.qgl_window)
        self.setFixedSize(size[0]+200,size[1])

        self.ui.refreshButton.clicked.connect(self.refreshLayers)
        self.ui.saveButton.clicked.connect(self.saveImage)
        self.ui.spinBox.setValue(size[1])
        self.ui.spinBox.editingFinished.connect(self.resizeMonoplotter)
        self.ui.pushButton.clicked.connect(self.getOrtho)
        self.ui.buttonLabel.clicked.connect(self.openLabelSettings)
        self.ui.activatePolygon.clicked.connect(self.activatePolygonVisualization)
        
        if not self.useOrthoImage:
            self.ui.horizontalSlider.valueChanged.connect(self.changeTransparency)
        
        self.labelSetting = [QtGui.QColor(0, 0, 0),QFont(),0,0]
        self.ui.measure3D.toggled.connect(self.startMeasure3D)
        self.isMeasuring3D = False
        
    def activatePolygonVisualization(self):
        if self.polygonActivated == False:
            self.polygonActivated = True
            self.qgl_window.polygonActivated = True
            self.ui.activatePolygon.setText('Disable Polygons')
        elif self.polygonActivated == True:
            self.polygonActivated = False
            self.qgl_window.polygonActivated = False
            self.ui.activatePolygon.setText('Enable Polygons')
        
    def changeTransparency(self, val):
        self.qgl_window.transparency = val*50
        self.qgl_window.updateGL()
    
    def closeEvent(self, event):
        namePath = os.path.realpath(__file__)
        namePath = namePath.rsplit('\\', 3)
        path = namePath[0]+str("/plugins/Pic2Map/dustbin")
        folder = path.replace("\\","/")
        self.qgl_window = None
        self.layerPolygonClipped = None
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            file_path = file_path.replace("\\","/")
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception, e:
                print e
        
    def startMeasure3D(self, state):
        if state == False:
            self.dlgMeasure3D.close()
            self.dlgMeasure3D = None
            self.isMeasuring3D = False
            
        else:
            self.dlgMeasure3D = mesure3DDialog()
            self.dlgMeasure3D.show()
            self.clearMapTool.emit()
            self.dlgMeasure3D.closeSignal.connect(self.stopMeasure3D)
            self.isMeasuring3D = True
            
    def stopMeasure3D(self):
        self.ui.measure3D.setChecked(False)
        self.qgl_window.lineEditBuffer = []
        self.qgl_window.updateGL()
        
        
    def openLabelSettings(self):
        # Control the settings of label in the monoplotter.
        # Label are drawn according to the current state inside the canvas
        self.labelSettingWindow = label_dialog(self.labelSetting)
        self.labelSettingWindow.setWindowModality(Qt.ApplicationModal)
        self.labelSettingWindow.show()
        result = self.labelSettingWindow.exec_()
        if result == 1:
            self.labelSetting[0] = self.labelSettingWindow.ui.colorButton.palette().color(1)
            self.labelSetting[1] = self.labelSettingWindow.font
            self.labelSetting[2] = self.labelSettingWindow.ui.doubleSpinBox.value()
            self.labelSetting[3] = self.labelSettingWindow.ui.doubleSpinBox_2.value()
            self.qgl_window.labelSettings = self.labelSetting
            self.qgl_window.notUpdate = False
        self.qgl_window.updateGL()
    
    def getOrtho(self, forPolygon = False):
        zBuffer = self.qgl_window.getZBuffer()
        zBuffer = zBuffer.reshape((self.qgl_window.viewport[3],self.qgl_window.viewport[2]))
        zBuffer = zBuffer.T
        bar = progress_bar()
        bar.progressBar = bar.ui_progbar.progressBar
        bar.show()
        bar.progressBar.setValue(1)
        
        A = dot(self.qgl_window.modelview, self.qgl_window.projection)
        self.m = linalg.pinv(A).transpose()
        texture = [0]*self.qgl_window.l_est*self.qgl_window.l_nord
        i = 0
        r = 0
        win = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,3))
        fTempo0 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,1))
        fTempo1 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,1))
        fTempo2 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,1))
        fTempo3 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,1))
        fTempo4 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,1))
        fTempo5 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,1))
        fTempo6 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,1))
        fTempo7 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,1))
        matrix_ini = concatenate((self.qgl_window.numpy_verts,ones((self.qgl_window.l_est*self.qgl_window.l_nord,1))),1)
        fTempo0 = dot(matrix_ini , self.qgl_window.modelview[:,0])
        fTempo1 = dot(matrix_ini , self.qgl_window.modelview[:,1])   
        fTempo2 = dot(matrix_ini , self.qgl_window.modelview[:,2])   
        fTempo3 = dot(matrix_ini , self.qgl_window.modelview[:,3])
        f1 = zeros((self.qgl_window.l_est*self.qgl_window.l_nord,4))
        f1 = array(concatenate((fTempo0,fTempo1,fTempo2,fTempo3),0))
        f1 = f1.reshape((4,self.qgl_window.l_est*self.qgl_window.l_nord)).T
        fTempo4 = dot(f1, self.qgl_window.projection[:,0])              
        fTempo5 = dot(f1, self.qgl_window.projection[:,1])    
        fTempo6 = dot(f1, self.qgl_window.projection[:,2])
        fTempo7 = -1.0/fTempo2
        fTempo4 *= fTempo7
        fTempo5 *= fTempo7
        fTempo6 *= fTempo7
        win[:,0]= (fTempo4*0.5+0.5)*self.qgl_window.viewport[2];
        win[:,1]= (fTempo5*0.5+0.5)*self.qgl_window.viewport[3];
        win[:,2]= (1.0+fTempo6)*0.5;        
       
        viewport2 = self.qgl_window.viewport[2]-0.5
        viewport3 =  self.qgl_window.viewport[3]-0.5
        
        #For each vertex of the DEM
        for winx, winy, winz in win:
            # check if the projection falls inside the sensor plane (id est falls inside the viewport of the QGLwidget
            if winx > 0 and winy > 0 and winx < (viewport2) and winy < (viewport3) and winz > 0 and winz < 0.99999:
                z_buff = zBuffer[int(winx),int(winy)]
                # check if the reprojection falls near the initial coordinates
                # which is a way to test if the vertex is visible, not hidden
                if (winz-z_buff)/(1-winz) < 0.01:
                    # The projected coordinate is given to the vertex
                    # The picture gets drapped on the DEm
                    texture[i] = [winx/viewport2, winy/viewport3]
                else:
                    # Here appears a small trick. Only someone who know openGL can understand 
                    # the machinery behind the next line
                    # In brief, it's impossible to give a texture at some vertices and no textures to some others.
                    # So how to deal with invisible vertices (which are majority) ?
                    # Here we give outside the picture. So it will appear black. 
                    # Now if you know openGL, you know that the texture is stretched between each vertices.
                    # So by giving a coordinates of -100, the pixel will be at 99% black. The 1% which remains
                    # is cleared by the round off at the resampling. 
                    texture[i] = [-100,-100]
            else:
                #same as the previous "else"
                texture[i] = [-100,-100]
                
            #progress bar
            r0 = r 
            i += 1
            r = (i*99)/(self.qgl_window.l_nord*self.qgl_window.l_est)
            if r != r0:
                bar.progressBar.setValue(r)
                
        self.texture = texture
        # Create the drapping window
        if not forPolygon:
            self.openOrtho.emit()
            
        
    def resizeMonoplotter(self):
        new_size = self.ui.spinBox.value()
        self.setFixedSize(int(self.ratio*new_size)+200,new_size)
    
    def saveImage(self):
        imgSave = self.qgl_window.grabFrameBuffer()
        path = self.pathToData + "/image.png"
        imageSaveName = QtGui.QFileDialog.getSaveFileName(self,"save file dialog" ,path,"Images (*.png *.xpm *.jpg)");
        if imageSaveName:
            imgSave.save(imageSaveName)
        
    def get_box(self):
        # This function help to decrease the number of feature to test for displaying in the monoplotter.
        # We create a bounding box limited by the DEM and the line passing by the camera perpendicular to
        # the nearest cardinal point of the view direction
        box =  [self.dem_box.xMinimum(), self.dem_box.yMinimum(), self.dem_box.xMaximum(), self.dem_box.yMaximum()]
        a = box[0]
        b = box[1]
        c = box[2]
        d = box[3]
        pos = self.ParamPose[0]
        lookat = self.ParamPose[1]
        FOV = self.ParamPose[2]
        if FOV < 90:
            dx = pos[0]-lookat[0]
            dy = pos[2]-lookat[2]
            heading = arctan2(-dy,dx)
            if heading > 3*pi/2 or heading < -3*pi/2:
                x_min = a
                y_min = b
                x_max = -pos[0]
                y_max = d
            elif heading > pi/2:
                x_min = a
                y_min = pos[2]
                x_max = c
                y_max = d
            elif heading > -pi/2:
                x_min = -pos[0]
                y_min = b
                x_max = c
                y_max = d
            elif heading > -3*pi/2:
                x_min = a
                y_min = b
                x_max = c
                y_max = pos[2]
            else:
                pass
            feat = QgsFeature()
            feat.setGeometry(QgsGeometry.fromPolyline([QgsPoint(x_min,y_min),QgsPoint(x_max,y_max)]))
            new_box = feat.geometry().boundingBox()
            return new_box

        else:
            return self.dem_box
    
    def getSymbology(self):
        # The idea here is to read how features are symbolized in the canvas and then to reproduce
        # the same symbols in the monoplotter.
        # The symbology is not read for each feature, but for a whole layer. Then a array filled with indices
        # is used for given the right symbol to the right feature according to atttributes
        layers = QgsMapLayerRegistry.instance().mapLayers()
        layerType = []
        symbolParam = []
        symbolAttributes = []
        symbolGraduations = []
        symbolCategories = []
        symbolColor = []
        symbolSize = []
        labelParam = []
        
        self.layerPolygonClipped = []
        self.symbolParamPolygon = []
        self.colorPolygons= []
        self.gradPolygon = []
        self.catPolygon = []
        self.attPolygon = []
        polygoneLayerCount = 0
        self.polygonClipedLayers = []
        
        for name, layer in layers.iteritems():
            try:
                # Check if Labels are enabled on the current layer
                WidthSize = []
                Color = []
    
                att = 0
                RenderType = None
                #Layer type is 0 for vector layers
                if layer.type() ==0 and self.iface.legendInterface().isLayerVisible(layer):
                    palyr = QgsPalLayerSettings() 
                    palyr.readFromLayer(layer) 
                    if layer.geometryType() == 2:
                        pass
                    elif not palyr.enabled:
                        labelParam.append(-1)

                    else:
                        fields =  layer.pendingFields()
                        id = -1
                        for field in fields:
                             id+=1
                             if str(field.name()) == palyr.fieldName:
                                 att = id
                        labelParam.append(att)
                        
                    test_oneSymbolLayer = -1
                    renderer = layer.rendererV2()
                    new_graduation = []
                    new_categorie = []
                    new_color = []
                    new_size = []
                    attribute = None
                    #Point: 0
                    if layer.geometryType() == 0:
                        layerType.append(0)
                        if renderer.type() == "singleSymbol":
                            symbolParam.append(0)
                            for i in xrange(renderer.symbol().symbolLayerCount()):
                                lyr = renderer.symbol().symbolLayer(i)
                                WidthSize = lyr.size()
                                Color = lyr.color().getRgb()
                                test_oneSymbolLayer += 1
                                new_color.append(Color)
                                new_size.append(WidthSize)
                                
                        elif renderer.type() == "graduatedSymbol":
                            symbolParam.append(1)
                            attribute = renderer.classAttribute()
                            test_oneSymbolLayer += 1
                            for ran in renderer.ranges():
                                  new_graduation.append([ran.lowerValue(),ran.upperValue()])
                                  test_oneSymbolLayer -= 1
                                  for i in xrange(ran.symbol().symbolLayerCount()):
      
                                      lyr = ran.symbol().symbolLayer(i)
                                      test_oneSymbolLayer += 1
                                      WidthSize = lyr.size()
                                      Color = lyr.color().getRgb()
                                      new_color.append(Color)
                                      new_size.append(WidthSize)
                            att = self.getAttrId(layer,attribute)

                        elif renderer.type() == "categorizedSymbol":
                            symbolParam.append(2)
                            attribute = renderer.classAttribute()
                            test_oneSymbolLayer += 1
                            for cat in renderer.categories():
                                new_categorie.append(cat.value())
                                test_oneSymbolLayer -= 1
                                for i in xrange(cat.symbol().symbolLayerCount()):
                                      lyr = cat.symbol().symbolLayer(i)
                                      WidthSize = lyr.size()
                                      Color = lyr.color().getRgb()
                                      new_color.append(Color)
                                      new_size.append(WidthSize)
                                      test_oneSymbolLayer += 1
                            att = self.getAttrId(layer,attribute)
                                     
                    #Line: 1
                    elif layer.geometryType() == 1:
                        layerType.append(1)   
                        if renderer.type() == "singleSymbol":
                            for i in xrange(renderer.symbol().symbolLayerCount()):
                                symbolParam.append(0)
                                lyr = renderer.symbol().symbolLayer(i)
                                WidthSize = lyr.width()
                                Color = lyr.color().getRgb()
                                test_oneSymbolLayer += 1
                                new_color.append(Color)
                                new_size.append(WidthSize)
                        elif renderer.type() == "graduatedSymbol":
                            symbolParam.append(1)
                            attribute = renderer.classAttribute()
                            test_oneSymbolLayer += 1
                            for ran in renderer.ranges():
                                  new_graduation.append([ran.lowerValue(),ran.upperValue()])
                                  test_oneSymbolLayer -= 1
                                  for i in xrange(ran.symbol().symbolLayerCount()):
                                      lyr = ran.symbol().symbolLayer(i)
                                      WidthSize = lyr.width()
                                      Color = lyr.color().getRgb()
                                      test_oneSymbolLayer += 1
                                      new_color.append(Color)
                                      new_size.append(WidthSize)
                            att = self.getAttrId(layer,attribute)
                                     
                                      
                        elif renderer.type() == "categorizedSymbol":
                            symbolParam.append(2)
                            attribute = renderer.classAttribute()
                            test_oneSymbolLayer += 1
                            for cat in renderer.categories():
                                new_categorie.append(cat.value())
                                test_oneSymbolLayer -= 1
                                for i in xrange(cat.symbol().symbolLayerCount()):
                                      lyr = cat.symbol().symbolLayer(i)
                                      WidthSize = lyr.width()
                                      Color = lyr.color().getRgb()
                                      test_oneSymbolLayer += 1
                                      new_color.append(Color)
                                      new_size.append(WidthSize)    
                            att = self.getAttrId(layer,attribute)
                    #Polygon
                    elif layer.geometryType() == 2:
                        # Get only the viewshed, the first time polygons are activated
                        if self.polygonActivated:
                            colorPolygon = []
                            catPolygon = []
                            gradPolygon = []
                            attribute = 0
                            namePath = os.path.realpath(__file__)
                            namePath = namePath.rsplit('\\', 3)
                            path = namePath[0]+str("/plugins/Pic2Map/dustbin/")
                            path = path.replace("\\","/")
                            
                            if not self.haveMask:
                                self.createMaskClip(path)
                                self.haveMask = True
                            self.getPolygons(layer, path)
                            
                            if renderer.type() == "singleSymbol":
                                 for i in xrange(renderer.symbol().symbolLayerCount()):
                                    lyr = renderer.symbol().symbolLayer(i)
                                    self.symbolParamPolygon.append(0)
                                    Color = lyr.color().getRgb()
                                    colorPolygon.append(Color)
                                    test_oneSymbolLayer += 1
                            elif renderer.type() == "graduatedSymbol":
                                self.symbolParamPolygon.append(1)
                                attribute = renderer.classAttribute()
                                test_oneSymbolLayer += 1
                                for ran in renderer.ranges():
                                      gradPolygon.append([ran.lowerValue(),ran.upperValue()])
                                      test_oneSymbolLayer -= 1
                                      for i in xrange(ran.symbol().symbolLayerCount()):
                                          lyr = ran.symbol().symbolLayer(i)
                                          Color = lyr.color().getRgb()
                                          test_oneSymbolLayer += 1
                                          colorPolygon.append(Color)
                            elif renderer.type() == "categorizedSymbol":
                                self.symbolParamPolygon.append(2)
                                attribute = renderer.classAttribute()
                                test_oneSymbolLayer += 1
                                for cat in renderer.categories():
                                    catPolygon.append(cat.value())
                                    test_oneSymbolLayer -= 1
                                    for i in xrange(cat.symbol().symbolLayerCount()):
                                          lyr = cat.symbol().symbolLayer(i)
                                          Color = lyr.color().getRgb()
                                          test_oneSymbolLayer += 1
                                          colorPolygon.append(Color)
                            self.colorPolygons.append(colorPolygon)
                            self.attPolygon.append(attribute)
                            self.catPolygon.append(catPolygon)
                            self.gradPolygon.append(gradPolygon)
                                
                        else:
                            test_oneSymbolLayer = 0
                    
                    if test_oneSymbolLayer:
                        test_oneSymbolLayer += 1
                        raise UserWarning, "Multiband layer selected"

                    if layer.geometryType() != 2:
                        symbolGraduations.append(new_graduation)
                        symbolCategories.append(new_categorie)
                        symbolColor.append(new_color)
                        symbolSize.append(new_size)
                        symbolAttributes.append(att)
            except UserWarning, e:
                QMessageBox.warning(self, "Symbology - Error", "Failed update icons, Unsupported Symbology: %s " %e)
        self.qgl_window.defSymbology(layerType,symbolParam,symbolGraduations,symbolCategories,symbolColor,symbolSize)
        self.layerType = layerType
        self.symbolParam = symbolParam
        self.symbolAttributes = symbolAttributes
        self.symbolGraduations = symbolGraduations
        self.symbolCategories = symbolCategories
        self.symbolColor = symbolColor
        self.symbolSize = symbolSize
        self.labelParam = labelParam
        
    def getAttrId(self, layer, attribute):
        fields =  layer.pendingFields()
        id = -1
        for field in fields:
             id+=1
             if str(field.name()) == str(attribute):
                 att = id
        return att
        
    def createMaskClip(self, path):
        name = path + 'raster12.tiff'
        self.getOrtho(True)
        meterPerPixel = 10
        totPixN = (self.qgl_window.l_nord/meterPerPixel)*self.qgl_window.resolution
        totPixE = (self.qgl_window.l_est/meterPerPixel)*self.qgl_window.resolution
        ParamViewport = [0,0,1,1]
        orthoSavedParam = [totPixN, totPixE, ParamViewport]
        """
        a = self.viewOrtho.getMaxBufferSize()
        try:
            if not self.isFrameBufferSupported:
                QMessageBox.warning(self, "OpenGL Version","The current openGL Version does not support frame buffer.\n Raster with less pixel than screen can be saved only.")
                if self.resolution.height() < totPixN or self.resolution.width() < totPixE:
                    raise ValueError
            if totPixE > a or totPixN > a:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Value Error","Failed to save raster.\nConsider increasing the resolution.")"""
        self.orthoSaveInstance = viewOrtho_class(self.pointBuffer,
                                          self.picture_name,
                                          self.qgl_window.modelview,
                                          self.qgl_window.projection,
                                          self.qgl_window.viewport,
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
        self.orthoSaveInstance.saveOrtho(name)
        self.orthoSaveInstance.close()
        
        try:
            sourceRaster = gdal.Open(name)
            band = sourceRaster.GetRasterBand(4)
            bandArray = band.ReadAsArray()
            outShapefile = path + "polygonized"
            driver = ogr.GetDriverByName("ESRI Shapefile")
        
            if os.path.exists(outShapefile+".shp"):
                driver.DeleteDataSource(outShapefile+".shp")
            outShapefile = path + "polygonized"
            outDatasource = driver.CreateDataSource(outShapefile + ".shp")
            
            outLayer = outDatasource.CreateLayer("polygonized", None)
            newField = ogr.FieldDefn('MYFLD', ogr.OFTInteger)
    
            outLayer.CreateField(newField)
            gdal.Polygonize(band, None, outLayer, 0, [], callback=None )
            
            layer = outDatasource.GetLayer()
            indice = 0
            for feature in layer:
                indice +=1
                if feature.GetField("MYFLD") == 0:
                    layer.DeleteFeature(feature.GetFID())
        
        finally:
            outLayer = None
            outShapefile = None
            sourceRaster = None
            if 'outDatasource' in locals():
                outDatasource.Destroy()
        
    def getPolygons(self, layer, path):
        try:
            count = 0
            done = False
            while count < 4 and not done:
                try:
                    driver = ogr.GetDriverByName("ESRI Shapefile")
                    myfilepath= os.path.dirname( unicode(layer.dataProvider().dataSourceUri() ) )
                    layerName2 = myfilepath + "/" +str(layer.name())+ ".shp"
                    layerName2 = layerName2.replace("\\","/")
            
                    layerName1 = path + "polygonized" + ".shp"
            
                    Datasource1 = driver.Open(layerName1)
                    layer1 = Datasource1.GetLayer()
                    
                    Datasource2 = driver.Open(layerName2) 
                    layer2 = Datasource2.GetLayer()
                    
                    outShapefile2 = path +"intersectioned"
            
                    if os.path.exists(outShapefile2+".shp"):
                        driver.DeleteDataSource(outShapefile2+".shp")
                        
                    outShapefile2 = path +"intersectioned"    
                    outDatasource2 = driver.CreateDataSource(outShapefile2+ ".shp")
                    outLayer2 = outDatasource2.CreateLayer("intersectioned", None)
                    layer2.Intersection(layer1,outLayer2)
                
                    outputshp = path +"polygons" + layer.name()
                    if os.path.exists(outputshp+".shp"): 
                        driver.DeleteDataSource(outputshp+".shp") 
                    outputshp = path +"polygons"  + layer.name()   
                    out_ds = driver.CreateDataSource(outputshp+".shp") 
                    out_lyr = out_ds.CreateLayer('polygons', geom_type=ogr.wkbPolygon)
                    layerDef = outLayer2.GetLayerDefn()
                    for i in range(layerDef.GetFieldCount()):
                        fieldDef = outLayer2.GetLayerDefn().GetFieldDefn(i)
                        name = fieldDef.GetName()
                        type = fieldDef.GetType()
                        out_lyr.CreateField(ogr.FieldDefn(name, type))
                    self.multipoly2poly(outLayer2, out_lyr) 
                    
                    out_lyr = None
                    out_ds.Destroy()
                    out_ds = None
                    t = outputshp+".shp"
                    qgsClip = QgsVectorLayer(t,"layer_name", "ogr")
        
                    qgsClip.setCrs(self.crs)
                    iter2 = qgsClip.getFeatures()
                    polygons = []
                    for feature2 in iter2:
                        new_polygon = []
                        geom = feature2.geometry()
                        B = geom.asPolygon()
                        for vertex in B[0]:
                            ident = self.cLayer.dataProvider().identify(vertex,QgsRaster.IdentifyFormatValue).results()
                            value = ident.get(1)
                            new_polygon.append([-vertex[0],value,vertex[1]])
                        polygons.append(new_polygon)
                        
                    self.qgl_window.polygonLayers.append(polygons)
                    self.layerPolygonClipped.append(qgsClip)    
                    done = True
                except AttributeError:
                    if 'outDatasource' in locals():
                        out_ds.Destroy()
                    out_ds = None
                    count += 1
        finally:
            qgsClip = None
            t = None
            layer1 = None
            layer2 = None
            outLayer2 = None
            if hasattr(outDatasource2,'Destroy'):
                outDatasource2.Destroy()
            
                
    def multipoly2poly(self, in_lyr, out_lyr): 
        for in_feat in in_lyr: 
            geom = in_feat.GetGeometryRef() 
            field_value = []
            for i in range(in_lyr.GetLayerDefn().GetFieldCount()):
                field_value.append(in_feat.GetField(i))
            if geom.GetGeometryName() == 'MULTIPOLYGON':
                for i in range(geom.GetGeometryCount()): 
                        geom_part = geom.GetGeometryRef(i) 
                        self.addPolygon(geom_part.ExportToWkb(), out_lyr, field_value) 
                       
            else: 
                self.addPolygon(geom.ExportToWkb(), out_lyr, field_value)
                
    def addPolygon(self, simplePolygon, out_lyr, field_value): 
        featureDefn = out_lyr.GetLayerDefn() 
        polygon = ogr.CreateGeometryFromWkb(simplePolygon) 
        out_feat = ogr.Feature(featureDefn) 
        out_feat.SetGeometry(polygon)
        for i in range(featureDefn.GetFieldCount()):
            fieldDef = featureDefn.GetFieldDefn(i)
            name = fieldDef.GetName()
            out_feat.SetField(name, field_value[i])
        out_lyr.CreateFeature(out_feat) 
        
    def refreshLayers(self, boolSymbology = False):
        self.qgl_window.notUpdate = True
        zBuffer = self.qgl_window.getZBuffer()
        
        zBuffer = zBuffer.reshape((self.qgl_window.viewport[3],self.qgl_window.viewport[2]))
        zBuffer = zBuffer.T
        self.qgl_window.clearLayers()
        if not boolSymbology:
            self.getSymbology()
        layers = QgsMapLayerRegistry.instance().mapLayers()
        
        dataProvider =  self.cLayer.dataProvider()
        request = QgsFeatureRequest()
        box = self.get_box()
        request.setFilterRect(box)
        counter = -1
        counterPolygon = -1
        for name, layer in layers.iteritems():
            pointArrayXYZ = []
            LineArrayXYZ = []
            AttributeToSizeColorArray = []
            labels = []
            if layer.type() == 0 and self.iface.legendInterface().isLayerVisible(layer):
                if layer.geometryType() != 2: 
                    counter += 1
                    attributeTest =  self.symbolParam[counter]
                    graduation = self.symbolGraduations[counter]
                    categorie = self.symbolCategories[counter]
                    AttributeID = self.symbolAttributes[counter]
                    labelTest = self.labelParam[counter]
                        
                    if layer.geometryType() == 0: #Point
                        iter1 = layer.getFeatures(request)
                        if labelTest != -1:
                            for feature in iter1:
                                labels.append(feature.attributes()[labelTest])
                                
                        iter2 = layer.getFeatures(request)
                        for feature in iter2:
                            geom = feature.geometry()
                            p = geom.asPoint()
                            x = -p.x()
                            y = p.y()
                            ident = dataProvider.identify(p,QgsRaster.IdentifyFormatValue).results()
                            value = ident.get(1)
                            pointArrayXYZ.append([x,value,y])
                            if attributeTest== 1:
                                #Graduated symbology
                                attributeValue = feature.attributes()[AttributeID]
                                Index = self.getIndexSizeColorGraduation(attributeValue,graduation)
                                AttributeToSizeColorArray.append(Index)
                            if attributeTest== 2:
                                #Categorized symbology
                                attributeValue = feature.attributes()[AttributeID]
                                Index = self.getIndexSizeColorCategorie(attributeValue,categorie)
                                AttributeToSizeColorArray.append(Index)
                        self.qgl_window.pointRefresh(pointArrayXYZ,AttributeToSizeColorArray,zBuffer, attributeTest, labels)
                        
                    elif layer.geometryType() == 1: #Line
                        iter1 = layer.getFeatures(request) 
                        if labelTest != -1:
                            for feature in iter1:
                                labels.append(feature.attributes()[labelTest])
                        iter2 = layer.getFeatures(request)
                        for feature in iter2:
                            geom = feature.geometry()
                            l = geom.asPolyline()
                            new_line = []
                            for point in l:
                                x = -point.x()
                                y = point.y()
                                ident = dataProvider.identify(point,QgsRaster.IdentifyFormatValue).results()
                                value = ident.get(1)
                                new_line.append([x,value,y])
                            if len(new_line)>1:
                                LineArrayXYZ.append(new_line)
                                if attributeTest == 1:
                                    #Graduated Symbology
                                    attributeValue = feature.attributes()[AttributeID]
                                    Index = self.getIndexSizeColorGraduation(attributeValue,graduation)
                                    AttributeToSizeColorArray.append(Index)
    
                                if attributeTest == 2:
                                    #Categorized symbology
                                    attributeValue = feature.attributes()[AttributeID]
                                    Index = self.getIndexSizeColorCategorie(attributeValue,categorie)
                                    AttributeToSizeColorArray.append(Index)
                                    
                        self.qgl_window.line2Refresh(LineArrayXYZ, AttributeToSizeColorArray, zBuffer, attributeTest, labels)
                        
                elif layer.geometryType() == 2: #Polygon
                    if self.polygonActivated:
                        counterPolygon += 1
                        layerCliped = self.layerPolygonClipped[counterPolygon]
                        iter = layerCliped.getFeatures()
                        colorPolygon = self.colorPolygons[counterPolygon]
                        
                        attributeTest = self.symbolParamPolygon[counterPolygon]
                        color = []
                        if attributeTest == 0:
                            #simple symbology
                            for feature in iter:
                                color.append(colorPolygon[0])
                        elif attributeTest == 1:
                            #Graduated symbology
                            AttributeID =self.getAttrId(layerCliped,self.attPolygon[counterPolygon])
                            graduation = self.gradPolygon[counterPolygon]
                            for feature in iter:
                                attributeValue = feature.attributes()[AttributeID]
                                Index = self.getIndexSizeColorGraduation(attributeValue,graduation)
                                color.append(colorPolygon[Index])
                        elif attributeTest == 2:
                            #Graduated symbology
                            categories = self.catPolygon[counterPolygon]
                            AttributeID =self.getAttrId(layerCliped,self.attPolygon[counterPolygon])
                            for feature in iter:
                                attributeValue = feature.attributes()[AttributeID]
                                Index = self.getIndexSizeColorCategorie(attributeValue,categories)
                                color.append(colorPolygon[Index])
                        self.qgl_window.colorPolygon.append(color)
                    
        self.qgl_window.notUpdate = False
        self.qgl_window.updateGL()
        
    def getIndexSizeColorCategorie(self,value, categorie):
        indice = -1
        for cat in categorie:
            indice +=1
            if value == cat:
                return indice
        return -1
                        
    def getIndexSizeColorGraduation(self,value, graduation):
        indice = -1
        for min, max in graduation:
            indice +=1
            if value >= min and value <= max:
                return indice
        return -1
                    
        
class progress_bar(QtGui.QWidget):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.ui_progbar = Ui_progressBar()
        self.ui_progbar.setupUi(self)
        
        
                    