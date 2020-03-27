from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsCoordinateReferenceSystem
import webbrowser

import os
import math

''' Notes: 
l = iface.mapCanvas().currentLayer()
p = l.dataProvider()
p.nativeResolutions()
p.dpi()
c = iface.mapCanvas()
c.mapUnitsPerPixel()
'''

maxZoomLevel = 30
r3857 = [40075016.685 / (2 ** i * 256) for i in reversed(range(maxZoomLevel))]
r4326 = [180.0 / (2 ** i * 256) for i in reversed(range(maxZoomLevel))]

class LockZoomToTiles:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.epsg3857 = QgsCoordinateReferenceSystem('EPSG:3857')
        self.epsg4326 = QgsCoordinateReferenceSystem('EPSG:4326')
        self.islocking = False

    def initGui(self):
        '''Initialize Lock Zoom to Tiles GUI.'''

        icon = QIcon()
        icon.addFile(os.path.dirname(__file__) + "/images/zoomUnlocked.png", state=QIcon.Off)
        icon.addFile(os.path.dirname(__file__) + "/images/zoomLocked.png", state=QIcon.On)
        self.action = QAction(icon, "Lock zoom scale", self.iface.mainWindow())
        self.action.setObjectName('lockZoom')
        self.action.triggered.connect(self.lockIt)
        self.action.setCheckable(True)
        self.iface.addPluginToMenu("Lock zoom to tile scale", self.action)
        self.iface.addToolBarIcon(self.action)

        icon = QIcon(os.path.dirname(__file__) + '/images/help.png')
        self.helpAction = QAction(icon, "Help", self.iface.mainWindow())
        self.helpAction.triggered.connect(self.help)
        self.iface.addPluginToMenu('Lock zoom to tile scale', self.helpAction)
        
        self.checkCrs()
        self.canvas.destinationCrsChanged.connect(self.checkCrs)
        self.canvas.layersChanged.connect(self.checkCrs)

    def unload(self):
        '''Unload from the QGIS interface'''
        self.iface.removePluginMenu('Lock zoom to tile scale', self.action)
        self.iface.removeToolBarIcon(self.action)
        self.iface.removePluginMenu("Lock zoom to tile scale", self.helpAction)
        self.canvas.destinationCrsChanged.disconnect(self.checkCrs)
        if self.islocking == True:
            try:
                self.canvas.scaleChanged.disconnect(self.lockIt)
            except Exception:
                pass
        
    def help(self):
        '''Display a help page'''
        url = QUrl.fromLocalFile(os.path.dirname(__file__) + "/index.html").toString()
        webbrowser.open(url, new=2)

    def lockIt(self):
        '''Set the focus of the copy coordinate tool'''
        if self.action.isChecked():
            self.zoomTo()
            if self.islocking == False:
                self.islocking = True
                self.canvas.scaleChanged.connect(self.zoomTo)
                self.action.setText("Unlock zoom scale")
                self.action.setIconText("Unlock zoom scale")
        else:
            if self.islocking == True:
                self.canvas.scaleChanged.disconnect(self.zoomTo)
                self.islocking = False
                self.action.setText("Lock zoom scale")
                self.action.setIconText("Lock zoom scale")

    def zoomTo(self):
        crs = self.canvas.mapSettings().destinationCrs()
        mupp = self.canvas.mapUnitsPerPixel()
        if crs == self.epsg3857:
            r = 0
            for i in range(0, len(r3857)):
                r = i
                if r3857[i] > mupp:
                    if i > 0 and (r3857[i]-mupp > mupp-r3857[i-1]):
                        r = i-1
                    break
            if not math.isclose(r3857[r], mupp, rel_tol=1e-5):
                self.canvas.zoomByFactor(r3857[r] / self.canvas.mapUnitsPerPixel())
        else:
            r = 0
            for i in range(0, len(r4326)):
                r = i
                if r4326[i] > mupp:
                    if i > 0 and (r4326[i]-mupp > mupp-r4326[i-1]):
                        r = i-1
                    break
            if not math.isclose(r4326[r], mupp, rel_tol=1e-5):
                self.canvas.zoomByFactor(r4326[r] / self.canvas.mapUnitsPerPixel())
        
    def checkCrs(self):
        crs = self.canvas.mapSettings().destinationCrs()
        numlayers = self.canvas.layerCount()
        if (crs == self.epsg3857 or crs == self.epsg4326) and numlayers > 0:
            self.action.setEnabled(True)
        else:
            self.action.setEnabled(False)
            self.action.setChecked(False)
        self.lockIt()

