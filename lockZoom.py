from qgis.PyQt.QtCore import Qt, QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsCoordinateReferenceSystem

import os
import math

# Notes: l = iface.mapCanvas().currentLayer()
# p = l.dataProvider()
# p.dpi()
# p.nativeResolutions()
# c = iface.mapCanvas()
# c.mapUnitsPerPixel()

r3857=[0.29858214173896974, 0.5971642834779395, 1.194328566955879, 2.388657133911758, 4.777314267823516, 9.554628535647032, 19.109257071294063, 38.21851414258813, 76.43702828517625, 152.8740565703525, 305.748113140705, 611.49622628141, 1222.99245256282, 2445.98490512564, 4891.96981025128, 9783.93962050256, 19567.87924100512, 39135.75848201024, 78271.51696402048, 156543.03392804097]

r4326=[3.3527612686157227e-07, 6.705522537231445e-07, 1.341104507446289e-06, 2.682209014892578e-06, 5.364418029785156e-06, 1.0728836059570312e-05, 2.1457672119140625e-05, 4.291534423828125e-05, 8.58306884765625e-05, 0.000171661376953125, 0.00034332275390625, 0.0006866455078125, 0.001373291015625, 0.00274658203125, 0.0054931640625, 0.010986328125, 0.02197265625, 0.0439453125, 0.087890625, 0.17578125, 0.3515625, 0.703125]

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
        
        self.checkCrs()
        self.canvas.destinationCrsChanged.connect(self.checkCrs)
        self.canvas.layersChanged.connect(self.checkCrs)

    def unload(self):
        '''Unload from the QGIS interface'''
        self.iface.removePluginMenu('Lock zoom to tile scale', self.action)
        self.iface.removeToolBarIcon(self.action)
        self.canvas.destinationCrsChanged.disconnect(self.checkCrs)
        if self.islocking == True:
            try:
                self.canvas.scaleChanged.disconnect(self.lockIt)
            except Exception:
                pass

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

