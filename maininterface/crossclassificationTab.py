# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2018 by Luca Congedo
		email				: ing.congedoluca@gmail.com
**************************************************************************************************************************/
 
/**************************************************************************************************************************
 *
 * This file is part of Semi-Automatic Classification Plugin
 * 
 * Semi-Automatic Classification Plugin is free software: you can redistribute it and/or modify it under 
 * the terms of the GNU General Public License as published by the Free Software Foundation, 
 * version 3 of the License.
 * 
 * Semi-Automatic Classification Plugin is distributed in the hope that it will be useful, 
 * but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 * FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with 
 * Semi-Automatic Classification Plugin. If not, see <http://www.gnu.org/licenses/>. 
 * 
**************************************************************************************************************************/

"""



cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class CrossClassification:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate cross classification if click on button
	def calculateCrossClassification(self):
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " calculate Cross Classification ")
		self.crossClassification(self.clssfctnNm, cfg.referenceLayer2)
	
	# classification name
	def classificationLayerName(self):
		self.clssfctnNm = cfg.ui.classification_name_combo_2.currentText()
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "classification name: " + str(self.clssfctnNm))
	
	# cross classification calculation
	def crossClassification(self, classification, reference, batch = "No", shapefileField = None, rasterOutput = None,  NoDataValue = None):
		# check if numpy is updated
		try:
			cfg.np.count_nonzero([1,1,0])
		except Exception as err:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			rstrCheck = "No"
			cfg.mx.msgErr26()
		if batch == "No":
			crossRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Save cross classification raster output"), "", "*.tif", "tif")
		else:
			crossRstPath = rasterOutput
		if crossRstPath is not False:
			if crossRstPath.lower().endswith(".tif"):
				pass
			else:
				crossRstPath = crossRstPath + ".tif"
			if batch == "No":
				iClass = cfg.utls.selectLayerbyName(classification, "Yes")
				l = cfg.utls.selectLayerbyName(reference)
			else:
				try:
					# open input with GDAL
					rD = cfg.gdalSCP.Open(reference, cfg.gdalSCP.GA_ReadOnly)
					if rD is None:
						l = cfg.utls.addVectorLayer(str(reference) , str(cfg.osSCP.path.basename(reference)), "ogr")
					else:
						l = cfg.utls.addRasterLayer(str(reference), str(cfg.osSCP.path.basename(reference)))
					reml = l
					rD = None
					if cfg.osSCP.path.isfile(classification):
						iClass = cfg.utls.addRasterLayer(str(classification), str(cfg.osSCP.path.basename(classification)))
						remiClass = iClass
					else:
						return "No"
				except:
					return "No"
			# date time for temp name
			dT = cfg.utls.getTime()
			if iClass is not None and l is not None:
				# if not reference shapefile
				if l.type() != 0:
					# check projections
					newRstrProj = cfg.utls.getCrs(iClass)
					refRstrProj = cfg.utls.getCrs(l)
					if refRstrProj != newRstrProj:
						cfg.mx.msg9()
						return "No"
				else:
					# vector EPSG
					if "MultiPolygon?crs=PROJCS" in str(cfg.utls.layerSource(l)):
						# temp shapefile
						tSHP = cfg.tmpDir + "/" + cfg.rclssTempNm + dT + ".shp"
						l = cfg.utls.saveMemoryLayerToShapefile(l, tSHP)
						vEPSG = cfg.utls.getEPSGVector(tSHP)
					else:
						ql = cfg.utls.layerSource(l)
						vEPSG = cfg.utls.getEPSGVector(ql)
					dT = cfg.utls.getTime()
					# in case of reprojection
					qll = cfg.utls.layerSource(l)
					reprjShapefile = cfg.tmpDir + "/" + dT + cfg.osSCP.path.basename(qll)
					qlll = cfg.utls.layerSource(iClass)
					rEPSG = cfg.utls.getEPSGRaster(qlll)
					if vEPSG != rEPSG:
						if cfg.osSCP.path.isfile(reprjShapefile):
							pass
						else:
							try:
								qllll = cfg.utls.layerSource(l)
								cfg.utls.repojectShapefile(qllll, int(vEPSG), reprjShapefile, int(rEPSG))
							except Exception as err:
								# remove temp layers
								try:
									cfg.utls.removeLayerByLayer(reml)
									cfg.utls.removeLayerByLayer(remiClass)
								except:
									pass
								# logger
								cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
								return "No"
						l = cfg.utls.addVectorLayer(reprjShapefile, cfg.osSCP.path.basename(reprjShapefile) , "ogr")
				if batch == "No":
					cfg.uiUtls.addProgressBar()
					# disable map canvas render for speed
					cfg.cnvs.setRenderFlag(False)
					cfg.QtWidgetsSCP.qApp.processEvents()
				# temp raster layer
				tRC= cfg.tmpDir + "/" + cfg.rclssTempNm + dT + ".tif"
				# cross classification
				eMN = dT + cfg.crossClassNm
				cfg.reportPth = str(cfg.tmpDir + "/" + eMN)
				tblOut = cfg.osSCP.path.dirname(crossRstPath) + "/" + cfg.osSCP.path.basename(crossRstPath)
				tblOut = cfg.osSCP.path.splitext(tblOut)[0] + ".csv"
				cfg.uiUtls.updateBar(10)
				# if reference shapefile
				if l.type()== 0:
					if batch == "No":
						fd = cfg.ui.class_field_comboBox_2.currentText()
					else:
						fd = shapefileField
					if batch == "No":
						# convert reference layer to raster
						qlllll = cfg.utls.layerSource(l)
						qllllll = cfg.utls.layerSource(iClass)
						vect = cfg.utls.vectorToRaster(fd, str(qlllll), classification, str(tRC), str(qllllll), extent = "Yes")
					else:
						qlllllll = cfg.utls.layerSource(l)
						vect = cfg.utls.vectorToRaster(fd, str(qlllllll), classification, str(tRC), classification, extent = "Yes")
					if vect == "No":
						if batch == "No":
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()
						return "No"	
					referenceRaster = tRC
				# if reference raster
				elif l.type()== 1:
					if batch == "No":
						referenceRaster = cfg.utls.layerSource(l)
					else:
						referenceRaster = reference
				# open input with GDAL
				refRstrDt = cfg.gdalSCP.Open(str(referenceRaster), cfg.gdalSCP.GA_ReadOnly)
				qlllllllI = cfg.utls.layerSource(iClass)
				newRstrDt = cfg.gdalSCP.Open(qlllllllI, cfg.gdalSCP.GA_ReadOnly)
				# No data value
				if NoDataValue is not None:
					nD = NoDataValue
				elif cfg.ui.nodata_checkBox_6.isChecked() is True:
					nD = cfg.ui.nodata_spinBox_7.value()
				else:
					nD = cfg.NoDataVal
				# combination finder
				# band list
				bLR = cfg.utls.readAllBandsFromRaster(refRstrDt)
				cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
				cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
				o = cfg.utls.processRaster(refRstrDt, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, nD, "No", None, None, "UniqueVal")
				cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
				refRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
				# band list
				bLN = cfg.utls.readAllBandsFromRaster(newRstrDt)
				cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
				cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
				o = cfg.utls.processRaster(newRstrDt, bLN, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, nD, "No", None, None, "UniqueVal")
				for b in range(0, len(bLR)):
					bLR[b] = None
				refRstrDt = None
				for b in range(0, len(bLN)):
					bLN[b] = None
				newRstrDt = None		
				cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
				newRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
				try:
					newRasterBandUniqueVal.remove(nD)
				except:
					pass
				cmb = list(cfg.itertoolsSCP.product(refRasterBandUniqueVal, newRasterBandUniqueVal))
				# error matrix
				col = []
				row = []
				cmbntns = {}
				# expression builder
				n = 1
				e = []
				for i in cmb:
					if str(i[0]) == "nan" or str(i[1]) == "nan" :
						pass
					else:
						e.append("cfg.np.where( (a == " + str(i[0]) + ") & (b == " + str(i[1]) + "), " + str(n) + ", 0)")
						cmbntns["combination_" + str(i[0]) + "_"+ str(i[1])] = n
						col.append(i[0])
						row.append(i[1])
						n = n + 1
				# virtual raster
				tPMN = cfg.tmpVrtNm + ".vrt"
				# date time for temp name
				dT = cfg.utls.getTime()
				tPMD = cfg.tmpDir + "/" + dT + tPMN
				tPMN2 = dT + cfg.calcRasterNm + ".tif"
				tPMD2 = cfg.tmpDir + "/" + tPMN2
				bList = [str(referenceRaster), cfg.utls.layerSource(iClass)]
				bandNumberList = [1, 1]
				vrtCheck = cfg.utls.createVirtualRaster(bList, tPMD, bandNumberList, "Yes", "Yes", 0, "No", "Yes")
				# open input with GDAL
				rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
				# output rasters
				oM = []
				oM.append(tPMD2)
				oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression, "DEFLATE21")
				# band list
				bL = cfg.utls.readAllBandsFromRaster(rD)
				# calculation
				variableList = [["im1", "a"], ["im2", "b"]]
				cfg.rasterBandUniqueVal = {}
				o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.bandCalculationMultipleWhere, None, oMR, None, None, 0, None, nD, "No", e, variableList, "Calculating raster")
				cfg.rasterBandUniqueVal.pop(nD, None)
				if o == "No":
					if batch == "No":
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr45()
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error")
					return "No"
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "cross raster output: " + str(crossRstPath))
				# pixel size
				cRG = oMR[0].GetGeoTransform()
				cRPX = abs(cRG[1])
				cRPY = abs(cRG[5])
				# check projections
				cRP = oMR[0].GetProjection()
				cRSR = cfg.osrSCP.SpatialReference(wkt=cRP)
				un = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", "Unknown")
				if cRSR.IsProjected:
					un = cRSR.GetAttrValue('unit')
				# close GDAL rasters
				for b in range(0, len(oMR)):
					oMR[b] = None
				for b in range(0, len(bL)):
					bL[b] = None
				rD = None
				if cfg.rasterCompression != "No":
					try:
						cfg.utls.GDALCopyRaster(tPMD2, crossRstPath, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						cfg.osSCP.remove(tPMD2)
					except Exception as err:
						cfg.shutilSCP.copy(tPMD2, crossRstPath)
						cfg.osSCP.remove(tPMD2)
						# logger
						if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				else:
					cfg.shutilSCP.copy(tPMD2, crossRstPath)
					cfg.osSCP.remove(tPMD2)
				cfg.uiUtls.updateBar(80)
				col2 = list(set(col))
				row2 = list(set(row))
				cols = sorted(cfg.np.unique(col2).tolist())
				rows = sorted(cfg.np.unique(row2).tolist())
				crossClass = cfg.np.zeros((len(rows), len(cols)))
				cList = "V_" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Classification') + "\t"
				try:
					l = open(tblOut, 'w')
				except Exception as err:
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except Exception as err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					return "No"
				t = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'CrossClassCode') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Reference') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Classification') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'PixelSum') + "	" + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Area [' + un + "^2]") + str("\n")
				l.write(t)
				for c in cols:
					cList = cList + str(c) + "\t"
					for r in rows:
						try:
							v = cmbntns["combination_" + str(c) + "_"+ str(r)]
							area = str(cfg.rasterBandUniqueVal[v] * cRPX * cRPY)
							if area.endswith('.0'):
								area = area.split('.')[0]
							t = str(v) + "\t" + str(c) + "\t" + str(r) + "\t" + str(cfg.rasterBandUniqueVal[v]) + "	" + area + str("\n")
							l.write(t)
							crossClass[rows.index(r), cols.index(c)] = cfg.rasterBandUniqueVal[v] * cRPX * cRPY
						except:
							crossClass[rows.index(r), cols.index(c)] = cfg.rasterBandUniqueVal[v] * cRPX * cRPY
				# save combination to table
				l.write(str("\n"))
				tStr = "\t" + "> " + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'CROSS MATRIX [') + str(un) + "^2]" + "\n"
				l.write(tStr)
				tStr = "\t" + "> " + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Reference') + "\n"
				l.write(tStr)
				tStr = cList + cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Total') + "\n"
				l.write(tStr)
				# temp matrix
				tmpMtrx= cfg.tmpDir + "/" + cfg.tempMtrxNm + dT + ".txt"
				cfg.np.savetxt(tmpMtrx, crossClass, delimiter="\t", fmt="%i")
				tM = open(tmpMtrx, 'r')
				# write matrix
				ix = 0
				for j in tM:
					tMR = str(rows[ix]) + "\t" + j.rstrip('\n') + "\t" + str(int(crossClass[ix, :].sum())) + str("\n")
					l.write(tMR)
					ix = ix + 1
				# last line
				lL = cfg.QtWidgetsSCP.QApplication.translate("semiautomaticclassificationplugin", 'Total')
				for c in range(0, len(cols)):
					lL = lL + "\t" + str(int(crossClass[:, c].sum()))
				totMat = int(crossClass.sum())
				lL = lL + "\t" + str(totMat) + str("\n")
				l.write(lL)
				l.close()
				# add raster to layers
				rstr = cfg.utls.addRasterLayer(str(crossRstPath), str(cfg.osSCP.path.basename(crossRstPath)))
				cfg.utls.rasterSymbolGeneric(rstr, "NoData")	
				try:
					f = open(tblOut)
					if cfg.osSCP.path.isfile(tblOut):
						eM = f.read()
						cfg.ui.cross_matrix_textBrowser.setText(eM)
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " cross matrix calculated")
				except Exception as err:
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				cfg.uiUtls.updateBar(100)
				if batch == "No":
					# enable map canvas render
					cfg.cnvs.setRenderFlag(True)
					cfg.utls.finishSound()
					cfg.ui.toolBox_cross_classification.setCurrentIndex(1)
					cfg.uiUtls.removeProgressBar()
				else:
					# remove temp layers
					try:
						cfg.utls.removeLayerByLayer(reml)
						cfg.utls.removeLayerByLayer(remiClass)
					except:
						pass
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "finished")
			else:
				self.refreshReferenceLayer()
				cfg.utls.refreshClassificationLayer()
				
	# reference layer name
	def referenceLayerName(self):
		cfg.referenceLayer2 = cfg.ui.reference_name_combo_2.currentText()
		cfg.ui.class_field_comboBox_2.clear()
		l = cfg.utls.selectLayerbyName(cfg.referenceLayer2)
		try:
			if l.type()== 0:
				f = l.dataProvider().fields()
				for i in f:
					if i.typeName() != "String":
						cfg.dlg.class_field_combo_2(str(i.name()))
		except:
			pass
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layer name: " + str(cfg.referenceLayer2))
	
	# refresh reference layer name
	def refreshReferenceLayer(self):
		ls = cfg.qgisCoreSCP.QgsProject.instance().mapLayers().values()
		cfg.ui.reference_name_combo_2.clear()
		# reference layer name
		cfg.referenceLayer2 = None
		for l in sorted(ls, key=lambda c: c.name()):
			if (l.type()== cfg.qgisCoreSCP.QgsMapLayer.VectorLayer):
				if (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.Polygon) or (l.wkbType() == cfg.qgisCoreSCP.QgsWkbTypes.MultiPolygon):
					cfg.dlg.reference_layer_combo_2(l.name())
			elif (l.type()== cfg.qgisCoreSCP.QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.reference_layer_combo_2(l.name())
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference layers refreshed")
