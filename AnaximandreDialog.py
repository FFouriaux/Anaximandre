# -*- coding: utf-8 -*-
"""
/***************************************************************************
Anaximandre
								 A QGIS plugin
 Génération de couches vectorielles de Polygone, Lignes et Points en 3D shp
							 -------------------
		begin                : 2016-01
		copyright            : 2017 F.Fouriaux - Eveha
		email                : francois.fouriaux@eveha.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

#using Unicode for all strings
from __future__ import unicode_literals

import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.utils import *
from qgis.core import *
from qgis.gui import *
import ntpath


def selectLayer(layerName):
	layers=iface.legendInterface().layers()
	for l in layers:
		if l.name() == layerName:
			return l

def AjoutLayer(fileName):
	nom= ntpath.basename(fileName)
	iface.addVectorLayer(fileName,nom,"delimitedtext")


class AnaxDialg(QDialog):
	def __init__(self):
		QDialog.__init__(self)
	
	# Affichage du formatage attendu    
	def listeCodes(self):
		codif=['Num : numéro de point','X : coordonnée Est','Y : coordonnée Nord','Z: altitude','US : champ de regroupement','Desc : decription','Code : géométrie', 'Code2 : diametre(option)']
		for n in codif:
			self.listCodes.addItem(n)
		
	 
	# list of layers 'csv' already charged in the interface   
	def layerList(self):
		layers = iface.legendInterface().layers()
		layer_list = []
		self.cbox_FichierCsv.clear()
		for layer in layers:
			if layer.providerType()== 'delimitedtext':
				layer_list.append(layer.name())
		
		self.cbox_FichierCsv.addItems(layer_list)

	def selectedLayer(self):
	 
		if self.cbox_FichierCsv.currentText():
			return selectLayer(self.cbox_FichierCsv.currentText())


	# adopted from 'points2one Plugin'
	# Copyright (C) 2010 Pavol Kapusta
	# Copyright (C) 2010, 2013 Goyo
	# Copyright (C) Hatami 2014   

	def updateFieldCombos(self):
		self.listChp.clear()
		layer = self.selectedLayer()
		if layer is not None:            
			fields = layer.dataProvider().fields()
			for field in fields:
				name = field.name()
				self.listChp.addItem(name)

   
	def selectDirectory(self):
		self.lineEdit.setText(QFileDialog.getExistingDirectory(self))

	def OpenCsv(self):
		filtre= 'Text files (*.csv *.txt)'
		FileName= QFileDialog(filter=filtre)
		if FileName.exec_():
			fileName=FileName.selectedFiles()
		AjoutLayer(fileName[0]) 
		self.layerList()


	def outFile(self):
		"""Opens a file save dialog and sets the output file path."""
		
		outFilePath = saveFileDialog(self)
		if not outFilePath:
			return
		self.setOutFilePath(outFilePath)
	
	def getOutputFilePath(self):
		"""Returns the output file path."""
		
		return self.outFileLine.text()

	def setOutFilePath(self, outFilePath):
		"""Sets the output file path."""
		
		self.outFileLine.setText(outFilePath)
		
	def groupAttrName(self):
		"""Returns the name of the grouping attribute."""
		
		if self.chkBoxFieldGroup.isChecked():
			return unicode(self.comboGroup.currentText()) 
		
	def outputEncoding(self):
		"""Returns the selected encoding for the output Shapefile."""
		
		return unicode(self.comboEncoding.currentText())
	
	def getGeoChoiceAttr(self):
		"""Returns the name of the 'geometry choice' attribute """
		
		return unicode(self.comboGeoChoice.currentText())
	
	# adopted from 'points2one Plugin'
	# Copyright (C) 2010 Pavol Kapusta
	# Copyright (C) 2010, 2013 Goyo
	def showWarning(self, engine):
		
		logMsg = '\n'.join(engine.getLogger())
		if logMsg:
			warningBox = QMessageBox(self)
			warningBox.setWindowTitle('ArcheOCAD')
			message = QtGui.QApplication.translate("SDialog","Output Shapefile created.", None, QtGui.QApplication.UnicodeUTF8)
			warningBox.setText(message)
			message = QtGui.QApplication.translate("SDialog","There were some issues, maybe some features could not be created.", None, QtGui.QApplication.UnicodeUTF8)
			warningBox.setInformativeText(message)
			warningBox.setDetailedText(logMsg)
			warningBox.setIcon(QMessageBox.Warning)
			warningBox.exec_()        
	
	# adopted from 'points2one Plugin'
	# Copyright (C) 2010 Pavol Kapusta
	# Copyright (C) 2010, 2013 Goyo
	def addShapeToCanvas(self):
		message = unicode(QtGui.QApplication.translate("SDialog","Created output shapefile:", None, QtGui.QApplication.UnicodeUTF8))
		message = '\n'.join([message, unicode(self.getOutputFilePath())])
		message = '\n'.join([message,
			unicode(QtGui.QApplication.translate("SDialog","Would you like to add the new layer to your project?", None, QtGui.QApplication.UnicodeUTF8))])
		addToTOC = QMessageBox.question(self, "ArcheoCAD", message,
			QMessageBox.Yes, QMessageBox.No, QMessageBox.NoButton)
		if addToTOC == QMessageBox.Yes:
			Utilities.addShapeToCanvas(unicode(self.getOutputFilePath()))
			
	def hideDialog(self):        
		self.chkBoxFieldGroup.setCheckState(Qt.Unchecked)
		self.chkBoxSelected.setCheckState(Qt.Unchecked)
		self.outFileLine.clear()
		self.hide()
   
