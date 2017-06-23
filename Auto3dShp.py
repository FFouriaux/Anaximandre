# -*- coding: utf-8 -*-
"""
/***************************************************************************
Auto3dShp
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


from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.utils import *
from qgis.gui import *
from math import *
import csv

# # F. Fouriaux Janvier 2017
# # create automaticaly 3D polygon with a csv file from topographic survey
# # engine of Anaximandre

def Auto3DShp(CSV,Shape3D):

	# Creation des fichiers de sortie
	# Couche shp 3D 
	crsproject=iface.mapCanvas().mapRenderer().destinationCrs()           # crs du projet

	champs=QgsFields()                                                    # creation des champs du shp
	champs.append(QgsField("US",QVariant.String))
	champs.append(QgsField("Description",QVariant.String))
	champs.append(QgsField("Z",QVariant.Double))
	# fichier polygone
	fichierPolygon=Shape3D+'.shp'
	writerPoly = QgsVectorFileWriter(fichierPolygon,"utf-8",champs,QGis.WKBPolygon25D,crsproject)
	#fichier ligne
	fichierPolyline=Shape3D+'_Line.shp'
	writerLine = QgsVectorFileWriter(fichierPolyline,"utf-8",champs,QGis.WKBLineString25D,crsproject)
	#fichier point topo (ortho, coupes, plans, stations, etc.)
	fichierPointTopo=Shape3D+'_PtTopo.shp'
	writerPt = QgsVectorFileWriter(fichierPointTopo,"utf-8",champs,QGis.WKBPoint25D,crsproject)
	#fichiers isolats
	fichierISO=Shape3D+'_ISO.shp'
	writerISO = QgsVectorFileWriter(fichierISO,"utf-8",champs,QGis.WKBPoint25D,crsproject)
	#Fichier MNT
	fichierMNT =  Shape3D+'_PtMNT.shp'
	writerMNT= QgsVectorFileWriter(fichierMNT,"utf-8",champs,QGis.WKBPoint25D,crsproject)

	# parametres fin de ligne OS
	windows='\r\n'
	linux='\n'

	# lecture du csv
	file=open(CSV,'r')
	entete=file.readline().split(',')          # 1ere ligne en list[]en tete
	print 'entete du fichier: '
	print entete

	# determination des caracteres de fin de ligne
	der=entete[len(entete)-1]
	finl=der[len(der)-2]
	if finl=='\r':
		finligne=windows
	else:
		finligne=linux
		
	line=file.readline().split(',')
	# texte de base
	Wkt='POLYGONZ(('
	WktLine='LINESTRINGZ('
	WktPoint='PointZ('
	# parcours du fichier

	while len(line)>1: 
		if line[6]=='p'+finligne:                                                      # si geom = polygone
			US=line[4]
			Desc=line[5]
			Z=[float(line[3])]
			pt=''
			pt1='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))         # point de fermeture
			while len(line)>1 and line[4]==US and line[6]=='p'+finligne:
				
				pt+='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))     # liste points 3D format texte
				Z.append(float(line[3]))                                              # liste des Z
				line=file.readline().split(',')                                 
			
			Zmoy=sum(Z)/len(Z)
			WktF=Wkt+pt+pt1+'))'                                                #PolygonZ format texte
			poly=QgsFeature()
			poly.setGeometry(QgsGeometry.fromWkt(WktF))
			poly.setAttributes([US,Desc,Zmoy])
			writerPoly.addFeature(poly)
			
		elif line[6]=='l'+finligne:                                                    # si geom = ligne
			US=line[4]
			Desc=line[5]
			Z=[]
			pt=''
			while len(line)>1 and line[4]==US:
				
				pt+='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))     # liste points 3D format texte
				Z.append(float(line[3]))                                              # liste des Z
				line=file.readline().split(',')
				
			pt=pt.strip(',')
			Zmoy=sum(Z)/len(Z)
			WktF=WktLine+pt+')'                                                #PolylineZ format texte
			poly2=QgsFeature()
			poly2.setGeometry(QgsGeometry.fromWkt(WktF))
			poly2.setAttributes([US,Desc,Zmoy])
			writerLine.addFeature(poly2)
			
		elif line[6]=='iso'+finligne:                                                    # si geom = iso
			US=line[4]
			Desc=line[5]
			Z=float(line[3])
			pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))

			WktF=WktPoint+pt+')'                                                #PointZ format texte
			poly3=QgsFeature()
			poly3.setGeometry(QgsGeometry.fromWkt(WktF))
			poly3.setAttributes([US,Desc,Z])
			writerISO.addFeature(poly3)
			line=file.readline().split(',')
			
		elif line[6]=='pt'+finligne:                                                    # si geom = pt
			US=line[4]
			Desc=line[5]
			Z=float(line[3])
			pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))

			WktF=WktPoint+pt+')'                                                #PointZ format texte
			poly3=QgsFeature()
			poly3.setGeometry(QgsGeometry.fromWkt(WktF))
			poly3.setAttributes([US,Desc,Z])
			writerPt.addFeature(poly3)
			line=file.readline().split(',')
			
		elif line[6]=='pt cpe'+finligne:                                                    # si geom = point de coupe
			US=line[4]
			Desc=line[5]
			Z=[]
			ligne=''
			while len(line)>1 and line[4]==US and line[6] == 'pt cpe'+finligne and line[5]==Desc:           # cree les points et la ligne de cpe
				
				ligne+='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))
				Z.append(float(line[3]))
				Zpt=float(line[3])
				pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))
				WktF=WktPoint+pt+')'                                                #PointZ format texte des points de cpe
				poly3=QgsFeature()
				poly3.setGeometry(QgsGeometry.fromWkt(WktF))
				poly3.setAttributes([US,Desc,Zpt])
				writerPt.addFeature(poly3)
				line=file.readline().split(',')
				
			ligne=ligne.strip(',')
			Zmoy=sum(Z)/len(Z)
			WktF=WktLine+ligne+')'                                                #PolylineZ format texte de la coupe
			poly2=QgsFeature()
			poly2.setGeometry(QgsGeometry.fromWkt(WktF))
			poly2.setAttributes([US,Desc,Zmoy])
			writerLine.addFeature(poly2)
		
		elif line[6]=='pt mnt'+finligne:
			US=line[4]
			Desc=line[5]
			Z=[]
			ligne=''
			while len(line)>1 and line[4]==US and line[6] == 'pt mnt'+finligne and line[5]==Desc:           # cree les points et l envelope englobante du mnt
				ligne+='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))
				Z.append(float(line[3]))
				Zpt=float(line[3])
			
				pt='%s %s %s' %(str(line[1]), str(line[2]), str(line[3]))
			
				WktF=WktPoint+pt+')'                                                                            #PointZ format texte
				poly3=QgsFeature()
				poly3.setGeometry(QgsGeometry.fromWkt(WktF))
				poly3.setAttributes([US,Desc,Zpt])
				writerMNT.addFeature(poly3)
				line=file.readline().split(',')
			
				
			ligne=ligne.strip(',')
			Zmoy=sum(Z)/len(Z)
			WktF=WktLine+ligne+')'                                                #PolylineZ format texte pour creation de l envelope
			poly2=QgsFeature()
			poly2.setGeometry(QgsGeometry.fromWkt(WktF))
			chmnt=poly2.geometry().convexHull().asPolygon()                                    # envelope englobante
			polyMnt=QgsFeature()                                                               # polygon du mnt
			polyMnt.setGeometry(QgsGeometry.fromPolygon(chmnt))
			polyMnt.setAttributes([US,Desc,Zmoy])
			writerPoly.addFeature(polyMnt)
			
		elif line[6]=='c':                                                        # si geom = cercle avec point central + diametre
			US=line[4]
			Desc=line[5]
			Z=float(line[3])
			rayon=float(line[7])/2
			
			pt='%s %s %s,' %(str(line[1]), str(line[2]), str(line[3]))             # liste points 3D format texte

			WktF=WktPoint+pt+')'                                               #PointZ format texte
			poly2=QgsFeature()
			poly2.setGeometry(QgsGeometry.fromWkt(WktF))
			cercle=poly2.geometry().buffer(rayon,20).asPolygon()
			polyCercle=QgsFeature()
			polyCercle.setGeometry(QgsGeometry.fromPolygon(cercle))
			polyCercle.setAttributes([US,Desc,Z])
			writerPoly.addFeature(polyCercle)
			line=file.readline().split(',')
			
		else:
			line=file.readline().split(',')
			

	del writerPoly
	del writerLine
	del writerPt
	del writerISO
	del writerMNT

	# chargement dans le Canevas

	providerstring='ogr'
	if Shape3D=='':
		providerstring='memory'
	listLayers=[]   
	layer=QgsVectorLayer(fichierPolygon,'Polygones', providerstring)
	if layer.featureCount() >0:
		listLayers.append(layer)
	layer2=QgsVectorLayer(fichierPolyline,'Lignes', providerstring)
	if layer2.featureCount() >0:
		listLayers.append(layer2)
	layer3=QgsVectorLayer(fichierISO,'ISO', providerstring)
	if layer3.featureCount() >0:
		listLayers.append(layer3)
	layer4=QgsVectorLayer(fichierPointTopo,'PtTopo', providerstring)
	if layer4.featureCount() >0:
		listLayers.append(layer4)
	layer5=QgsVectorLayer(fichierMNT,'PtMNT', providerstring)
	if layer5.featureCount() >0:
		listLayers.append(layer5)
	QgsMapLayerRegistry.instance().addMapLayers(listLayers)
	QgsMapCanvas().setExtent(layer.extent())
	QgsMapCanvas().setLayerSet([QgsMapCanvasLayer(layer)])
	QgsMapCanvas().setLayerSet([QgsMapCanvasLayer(layer2)])
	QgsMapCanvas().setLayerSet([QgsMapCanvasLayer(layer3)])
	QgsMapCanvas().setLayerSet([QgsMapCanvasLayer(layer4)])
	QgsMapCanvas().setLayerSet([QgsMapCanvasLayer(layer5)])
