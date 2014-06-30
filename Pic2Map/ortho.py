"""
/***************************************************************************
 *                                                                         *
 *   This program is free software you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *****
 This class is used in two cases.
 First, it is used for the drapping MainWindow, for choosing the pink bounding box
 Secondly, it is usef for saving the raster.
 
 In the first case, the variable orthoSavedParam is not pass as argument, so equal to 0.
 In the second case, it is pass as argument and never equal to 0. Therefore,
 this variable is used as a test for changing the behavior of this file.
 
 The bounding box chosen for saving the raster is here called the "pink box"
 in reference to its color.
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtOpenGL import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from numpy import  zeros, array, float32, uint32, shape, uint8, uint16, max
from OpenGL.GL.framebufferobjects import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.arrays import ArrayDatatype as ADT
from osgeo import gdal, osr
from PIL import Image


class viewOrtho_class(QGLWidget):
    getBound =  pyqtSignal(list)# Emit the bounding box for saving the drapped picture
    def __init__(self, pointBuffer, picture_name, modelview, projection, viewport,
                  textCoord, orthoSavedParam = 0, crs = None, meterPerPixel = None, demName = None, isFrameBufferSupported = False):
        super(viewOrtho_class, self).__init__()
        self.orthoSavedParam = orthoSavedParam
        
        self.texture = textCoord
        self.numpy_verts = pointBuffer.numpy_verts
        self.m_indices =  pointBuffer.m_indices
        self.l_nord =  pointBuffer.l_nord
        print self.l_nord
        self.l_est =  pointBuffer.l_est
        print self.l_est
        self.res =  pointBuffer.res
        self.picture_name = picture_name
        self.dem_box = pointBuffer.dem_box
        self.offsetEst = (self.dem_box[2]-self.dem_box[0])/2 
        self.offsetNorth = (self.dem_box[3]-self.dem_box[1])/2
        self.modelview = modelview
        self.projection = projection
        self.viewport = viewport
        self.crs = crs
        self.meterPerPixel = meterPerPixel
        self.demName = demName
        self.isFrameBufferSupported = isFrameBufferSupported
        
        self.countVertices = len(self.numpy_verts)
        print self.countVertices
        print self.l_nord
        index = (self.countVertices)/2
        print self.numpy_verts[index][0]
        print self.numpy_verts[index][2]
        print index
        #Initialize the pink bounding box
        indexLD = (self.countVertices+self.l_nord*3)/4
        indexRU = (self.countVertices*3+self.l_nord)/4
        self.boxLeftUp = [self.numpy_verts[indexLD][0],self.numpy_verts[indexLD][2]]
        self.boxRightDown = [self.numpy_verts[indexRU][0],self.numpy_verts[indexRU][2]]
        
        if orthoSavedParam:
             self.totPixN = int(self.orthoSavedParam[0])
             self.totPixE = int(self.orthoSavedParam[1])
             ParamViewport =  self.orthoSavedParam[2]
             self.orthoViewPort = [int(ParamViewport[0]*self.totPixE),
                                   int(ParamViewport[1]*self.totPixN),
                                   int(ParamViewport[2]*self.totPixE),
                                   int(ParamViewport[3]*self.totPixN)]

    def mousePressEvent(self,event):
         # used fox editing the pink box
         if(event.buttons() & Qt.LeftButton):
                x = event.x()
                y = float(self.viewport_new[3]) -event.y()
                z = glReadPixels( x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
                print x,y,z
                result = gluUnProject( x, y, z, self.modelview_new, self.projection_new, self.viewport_new)
                self.boxLeftUp = [result[0],result[2]]
                self.boxRightDown = [result[0],result[2]]
        
    def mouseMoveEvent(self,event):
        if(event.buttons() & Qt.LeftButton):
            x =  event.x()
            y = float(self.viewport_new[3]) -event.y()
            z = glReadPixels( x, y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
            result = gluUnProject( x, y, z, self.modelview_new, self.projection_new, self.viewport_new)
            # Dragging the bounding box can only be done from up-left to right down corner
            if result[0]<self.boxLeftUp[0] and result[2]<self.boxLeftUp[1] :
                self.boxRightDown = [result[0],result[2]]
                self.last_pos = event.pos()
                self.updateGL()
                self.getBound.emit([self.boxLeftUp,self.boxRightDown])

    def paintGL(self):
         glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
         glEnable(GL_TEXTURE_2D)

         glMatrixMode(GL_MODELVIEW)
         glLoadIdentity()
         if (self.l_est) % 2 == 0:
            index = (self.countVertices+self.l_nord)/2
         else: 
             index = (self.countVertices)/2
         gluLookAt(self.numpy_verts[index][0],self.maximum+5000, self.numpy_verts[index][2],
                self.numpy_verts[index][0],self.maximum,self.numpy_verts[index][2],
                 0.0, 0.0, 1.0)
         
         glMatrixMode(GL_PROJECTION)
         glLoadIdentity()
         glOrtho(-self.offsetEst,self.offsetEst,-self.offsetNorth,self.offsetNorth,-1000,10000)
         
         #Draw the DEM with the projected picture as texture
         glEnableClientState( GL_VERTEX_ARRAY )
         glEnableClientState(GL_TEXTURE_COORD_ARRAY)
         glBindTexture(GL_TEXTURE_2D, self.textures2)
         
         glBindBufferARB( GL_ELEMENT_ARRAY_BUFFER_ARB, self.m_indicebuffer)
         glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.m_nVBOVertices )
         glVertexPointer(3,GL_FLOAT,0,None)
         glBindBufferARB( GL_ARRAY_BUFFER_ARB, 0 )
         
         glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.m_texbuffer )
         glTexCoordPointer(2, GL_FLOAT, 0, None)
         glBindBufferARB( GL_ARRAY_BUFFER_ARB, 0 )
         if self.orthoSavedParam:
             if self.isFrameBufferSupported:
                 glBindFramebuffer(GL_DRAW_FRAMEBUFFER, self.fbo)
         
         glDrawElements(GL_TRIANGLE_STRIP,self.count,GL_UNSIGNED_INT,None)
         
         glDisableClientState( GL_VERTEX_ARRAY )
         glBindBufferARB( GL_ELEMENT_ARRAY_BUFFER_ARB, 0 )
         
         self.modelview_new = glGetDoublev( GL_MODELVIEW_MATRIX)
         self.projection_new = glGetDoublev( GL_PROJECTION_MATRIX )
         self.viewport_new = glGetIntegerv( GL_VIEWPORT )
         

         if not self.orthoSavedParam:
             # Draw the pink box
             glDisable(GL_TEXTURE_2D)
             #The square is pink and half transparent
             glColor4f(1,0.5,1,0.5)
             # The square inside...
             glBegin(GL_QUADS)
             glVertex3f(self.boxLeftUp[0],self.maximum+3000,self.boxLeftUp[1])
             glVertex3f(self.boxRightDown[0],self.maximum+3000,self.boxLeftUp[1])
             glVertex3f(self.boxRightDown[0],self.maximum+3000,self.boxRightDown[1])
             glVertex3f(self.boxLeftUp[0],self.maximum+3000,self.boxRightDown[1])
             glEnd()
             glDepthMask(GL_TRUE)
             
             # and the border...
             # Border are black and not transparent
             glColor4f(0.0,0.0,0.0,1.0)
             glLineWidth(10)
             glBegin(GL_LINE_STRIP)
             glVertex3f(self.boxLeftUp[0],self.maximum+3000,self.boxLeftUp[1])
             glVertex3f(self.boxRightDown[0],self.maximum+3000,self.boxLeftUp[1])
             glVertex3f(self.boxRightDown[0],self.maximum+3000,self.boxRightDown[1])
             glVertex3f(self.boxLeftUp[0],self.maximum+3000,self.boxRightDown[1])
             glVertex3f(self.boxLeftUp[0],self.maximum+3000,self.boxLeftUp[1])
             glEnd()
             glColor3f(1.0, 1.0, 1.0)
             glEnable (GL_BLEND)
             glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  
             
    def getViewPortZoom(self):
        winx, winy, winz = gluProject(self.boxLeftUp[0],0,  self.boxLeftUp[1], self.modelview_new, self.projection_new, self.viewport_new)
        winx2, winy2, winz2 = gluProject(self.boxRightDown[0],0,  self.boxRightDown[1], self.modelview_new, self.projection_new, self.viewport_new)
        self.ParamViewport = [winx/self.viewport_new[2], winy2/self.viewport_new[3], winx2/self.viewport_new[2], winy/self.viewport_new[3]]
        
    def saveOrtho(self, name = None):
            self.updateGL()
            glViewport(0,0,self.totPixE,self.totPixN)
            self.updateGL()
            if self.isFrameBufferSupported:
                glReadBuffer(GL_COLOR_ATTACHMENT0)
            data = glReadPixels(self.orthoViewPort[0],
                self.orthoViewPort[1],
                self.orthoViewPort[2]-self.orthoViewPort[0],
                self.orthoViewPort[3]-self.orthoViewPort[1],
                 GL_RGB, GL_UNSIGNED_BYTE)
            
            imgSave = Image.fromstring("RGB", (self.orthoViewPort[2]-self.orthoViewPort[0],self.orthoViewPort[3]-self.orthoViewPort[1]), data)
            if name == None:
                imageSaveName = QFileDialog.getSaveFileName(self,"save file dialog" ,"/raster.tiff","Images (*.tiff *.png)")
                if imageSaveName:
                    format = imageSaveName.split('.')[1]
                    try:
                        if format == 'tiff':
                            #In case the user save the raster as tiff, it get georeferenced (so geotiff)
                            raster = array(imgSave.transpose(Image.FLIP_TOP_BOTTOM))
                            LeftUpInt = gluUnProject( int(self.orthoViewPort[0]), int(self.orthoViewPort[3]), 0.5, self.modelview_new, self.projection_new, self.viewport_new)
                            vectReference = [-LeftUpInt[0], self.meterPerPixel , 0, LeftUpInt[2],0,  -self.meterPerPixel]
                            self.WriteGeotiff(raster, imageSaveName, gdal.GDT_Byte, self.crs, vectReference)
                        elif format == 'png':
                            #In cas the user save the raster as png, it is not georeferenced
                            imgSave = imgSave.transpose(Image.FLIP_TOP_BOTTOM)
                            imgSave.save(imageSaveName)
                        else:
                            raise IOError, format
                    except IOError, e:
                        QMessageBox.warning(self, "Save - Error",
                            "Failed to save: %s - unsupported format" % e)
            else:
                imageSaveName = name
                raster = array(imgSave.transpose(Image.FLIP_TOP_BOTTOM))
                LeftUpInt = gluUnProject( int(self.orthoViewPort[0]), int(self.orthoViewPort[3]), 0.5, self.modelview_new, self.projection_new, self.viewport_new)
                vectReference = [-LeftUpInt[0], self.meterPerPixel , 0, LeftUpInt[2],0,  -self.meterPerPixel]
                self.WriteGeotiff(raster, imageSaveName, gdal.GDT_Byte, self.crs, vectReference)               
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            

    def WriteGeotiff(self, raster, filepath, dtype, crs, vectReference):
            nrows, ncols, nbands = shape(raster)
            format = "GTiff"
            driver = gdal.GetDriverByName( format )
            dst_ds = driver.Create(filepath, ncols, nrows, nbands+1, dtype, ['COMPRESS=LZW'])
            
            srs = osr.SpatialReference()
            ds=gdal.Open(self.demName)
            proj = ds.GetProjection()
            
            dst_ds.SetProjection(proj)
            dst_ds.SetGeoTransform(vectReference)
            
            R = array(raster[:,:,0],dtype=uint8)
            G = array(raster[:,:,1],dtype=uint8)
            B = array(raster[:,:,2],dtype=uint8)
            alpha = zeros((nrows,ncols))
            alpha[R > 0] = 255
            alpha[G > 0] = 255
            alpha[B > 0] = 255
            R = array(raster[:,:,0],dtype=uint16)
            G = array(raster[:,:,1],dtype=uint16)
            B = array(raster[:,:,2],dtype=uint16)

            dst_ds.GetRasterBand(1).WriteArray(R) # Red
            dst_ds.GetRasterBand(2).WriteArray(G) # Green
            dst_ds.GetRasterBand(3).WriteArray(B) # Blue
            dst_ds.GetRasterBand(4).WriteArray(alpha) # Alpha
            dst_ds = None
        
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def initializeGL(self):
        if self.orthoSavedParam:
            if self.isFrameBufferSupported:
                self.fbo = glGenFramebuffers(1)
                self.render_buf = glGenRenderbuffers(1)
        
                glBindRenderbuffer(GL_RENDERBUFFER, self.render_buf)
                glRenderbufferStorage(GL_RENDERBUFFER, GL_RGB, self.totPixE, self.totPixN)
                glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
                glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, self.render_buf)
        
        self.getBound.emit([self.boxLeftUp,self.boxRightDown])
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0,0.0,0.0,0.0)
        glEnable(GL_TEXTURE_2D)
        self.textures2 = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.textures2)
        
        img = QImage(self.picture_name)

        img = QGLWidget.convertToGLFormat(img)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, img.width(), img.height(),
                0, GL_RGBA, GL_UNSIGNED_BYTE, img.bits().asstring(img.numBytes()))
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        color =  [0.0, 0.0,0.0,0.0]

        glBindTexture(GL_TEXTURE_2D, 0)
        self.maximum = max(self.numpy_verts[:,1])
        self.numpy_texture = array(self.texture, dtype=float32)
        self.m_indices= array(self.m_indices,dtype=uint32)

        temp2 = glGenBuffersARB(3)
        self.m_nVBOVertices = int(temp2[0])           
        self.m_indicebuffer = int(temp2[1])
        self.m_texbuffer = int(temp2[2]) 
        glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.m_nVBOVertices )
        glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.numpy_verts, GL_STATIC_DRAW_ARB )

        glBindBufferARB( GL_ARRAY_BUFFER_ARB, 0 )
        glBindBufferARB( GL_ELEMENT_ARRAY_BUFFER_ARB, self.m_indicebuffer)
        glBufferDataARB( GL_ELEMENT_ARRAY_BUFFER_ARB, self.m_indices, GL_STATIC_DRAW_ARB )
        glBindBufferARB( GL_ELEMENT_ARRAY_BUFFER_ARB, 0) 
        glBindBufferARB( GL_ARRAY_BUFFER_ARB, self.m_texbuffer)
        glBufferDataARB( GL_ARRAY_BUFFER_ARB, self.numpy_texture, GL_STATIC_DRAW_ARB )
        glBindBufferARB( GL_ARRAY_BUFFER_ARB, 0 )
        self.count = len(self.m_indices)
        
    def getMaxBufferSize(self):
        return glGetIntegerv(GL_MAX_RENDERBUFFER_SIZE)
            
