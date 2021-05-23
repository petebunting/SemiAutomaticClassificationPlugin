# -*- coding: utf-8 -*-
'''
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright		: (C) 2012-2021 by Luca Congedo
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

'''



cfg = __import__(str(__name__).split('.')[0] + '.core.config', fromlist=[''])

class BandCombination:

	def __init__(self):
		self.clssfctnNm = None
		
	# calculate band set combination if click on button
	def calculateBandSetCombination(self):
		# logger
		cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' calculate band combination ')
		self.bandSetCombination()
	
	# cross classification calculation
	def bandSetCombination(self, batch = 'No', bandSetNumber = None, rasterOutput = None):
		if batch == 'No':
			combRstPath = cfg.utls.getSaveFileName(None, cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Save band combination raster output'), '', 'TIF file (*.tif);;VRT file (*.vrt)')
		else:
			combRstPath = rasterOutput
		# virtual raster
		vrtR = 'No'
		if combRstPath is not False:
			if combRstPath.lower().endswith('.vrt'):
				vrtR = 'Yes'
			elif combRstPath.lower().endswith('.tif'):
				pass
			else:
				combRstPath = combRstPath + '.tif'
			if bandSetNumber is None:
				bandSet = cfg.ui.band_set_comb_spinBox.value()
				bandSetNumber = bandSet - 1
			if batch == 'No':
				cfg.uiUtls.addProgressBar()
			# create list of rasters
			try:
				cfg.bandSetsList[bandSetNumber][0]
			except:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
				return 'No'
			if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
				ckB = cfg.utls.checkBandSet(bandSetNumber)
			else:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar29()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
				return 'No'
			if ckB != 'Yes':
				pass
			if len(cfg.bndSetLst) == 0:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
				return 'No'
			cfg.uiUtls.updateBar(10)
			cfg.utls.makeDirectory(cfg.osSCP.path.dirname(combRstPath))
			NoDataVal = cfg.NoDataVal
			rCrs = cfg.utls.getCrsGDAL(cfg.bndSetLst[0])
			rEPSG = cfg.osrSCP.SpatialReference()
			rEPSG.ImportFromWkt(rCrs)
			if rEPSG is None:
				if batch == 'No':
					cfg.uiUtls.removeProgressBar()
				cfg.mx.msgWar28()
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
				return 'No'
			cfg.uiUtls.updateBar(20)
			for b in range(0, len(cfg.bndSetLst)):
				eCrs = cfg.utls.getCrsGDAL(cfg.bndSetLst[b])
				EPSG = cfg.osrSCP.SpatialReference()
				EPSG.ImportFromWkt(eCrs)
				if EPSG.IsSame(rEPSG) != 1:
					if cfg.bandSetsList[bandSetNumber][0] == 'Yes':
						nD = cfg.utls.imageNoDataValue(cfg.bndSetLst[b])
						if nD is None:
							nD = NoDataVal
						tPMD = cfg.utls.createTempRasterPath('vrt')
						cfg.utls.createWarpedVrt(cfg.bndSetLst[b], tPMD, str(rCrs))
						cfg.mx.msg9()
						#tPMD = cfg.utls.createTempRasterPath('tif')
						#cfg.utls.GDALReprojectRaster(cfg.bndSetLst[b], tPMD, 'GTiff', None, str(rCrs), '-ot Float32 -dstnodata ' + str(nD))
						if cfg.osSCP.path.isfile(tPMD):
							cfg.bndSetLst[b] = tPMD
						else:
							if batch == 'No':
								cfg.uiUtls.removeProgressBar()
							cfg.mx.msgErr60()
							# logger
							cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' Warning')
							return 'No'
			cfg.uiUtls.updateBar(40)
			# reference raster
			referenceR = cfg.bndSetLst[0]
			# No data value
			nD = cfg.utls.imageNoDataValue(referenceR)
			if nD is None:
				nD = NoDataVal
			cfg.parallelArrayDict = {}
			o = cfg.utls.multiProcessRaster(rasterPath = referenceR, functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = nD, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values step ') + '0')
			# calculate unique values
			values = cfg.np.array([])
			for x in sorted(cfg.parallelArrayDict):
				try:
					for ar in cfg.parallelArrayDict[x]:
						values = cfg.np.append(values, ar[0, ::])
				except:
					if batch == 'No':
						cfg.utls.finishSound()
						cfg.utls.sendSMTPMessage(None, str(__name__))
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()			
					# logger
					cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
					cfg.mx.msgErr9()		
					return 'No'
			rasterBandUniqueVal = cfg.np.unique(values).tolist()
			refRasterBandUniqueVal = sorted(rasterBandUniqueVal)
			try:
				refRasterBandUniqueVal.remove(nD)
			except:
				pass
			tempRasters = []
			# iteration
			for b in range(1, len(cfg.bndSetLst)):
				bList = [referenceR, cfg.bndSetLst[b]]
				bListNum = [1, 1]
				bandsUniqueVal = []
				bandsUniqueVal.append(refRasterBandUniqueVal)
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = cfg.bndSetLst[b], functionBand = 'No', functionRaster = cfg.utls.rasterUniqueValuesWithSum, nodataValue = nD, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Unique values step ') + str(b) + '/' + str(len(cfg.bndSetLst)-1))
				# calculate unique values
				values = cfg.np.array([])
				for x in sorted(cfg.parallelArrayDict):
					try:
						for ar in cfg.parallelArrayDict[x]:
							values = cfg.np.append(values, ar[0, ::])
					except:
						if batch == 'No':
							cfg.utls.finishSound()
							cfg.utls.sendSMTPMessage(None, str(__name__))
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()			
						# logger
						cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
						cfg.mx.msgErr9()		
						return 'No'
				rasterBandUniqueVal = cfg.np.unique(values).tolist()
				newRasterBandUniqueVal = sorted(rasterBandUniqueVal)
				try:
					newRasterBandUniqueVal.remove(nD)
				except:
					pass
				bandsUniqueVal.append(newRasterBandUniqueVal)
				try:
					cmb = list(cfg.itertoolsSCP.product(*bandsUniqueVal))
					testCmb = cmb[0]
				except Exception as err:
					if batch == 'No':
						cfg.uiUtls.removeProgressBar()
					cfg.mx.msgErr63()
					# logger
					if cfg.logSetVal == 'Yes': cfg.utls.logToFile(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
					return 'No'
				# expression builder
				check = 'No'
				t = 0
				while t < 100:
					t = t + 1
					rndVarList = []
					# first try fixed list
					if t == 1:
						coT = 333
						for cmbI in range(0, len(cmb[0])):
							rndVarList.append(coT)
							coT = coT + 1
					# random list
					else:
						for cmbI in range(0, len(cmb[0])):
							rndVarList.append(int(999 * cfg.np.random.random()))
					newValueList = []
					reclassDict = {}
					for i in cmb:
						if nD not in i:
							newVl = cfg.np.multiply(rndVarList, i).sum()
							reclassDict[newVl] = i
							newValueList.append(newVl)
					uniqueValList = cfg.np.unique(newValueList)
					if int(uniqueValList.shape[0]) == len(newValueList):
						n = 1
						reclassList = []
						cmbntns = {}	
						for newVl in sorted(reclassDict.keys()):
							i = reclassDict[newVl]
							reclassList.append(newVl)
							try:
								listCB = []
								for bc in oldCmbntns[int(i[0])]:
									listCB.append(bc)
								listCB.append(i[1])
								cmbntns[n] = listCB
							except:
								cmbntns[n] = [i[0], i[1]]
							n = n + 1
						check = 'Yes'
						break
				if check == 'No':
					if batch == 'No':
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.uiUtls.removeProgressBar()
					return 'No'
				oldCmbntns = cmbntns.copy()
				e = ''
				for rE in range(0, len(rndVarList)):
					e = e + 'rasterSCPArrayfunctionBand[::, ::, ' + str(rE) + '] * ' + str(rndVarList[rE]) + ' + '
				e = e.rstrip(' + ')
				vrtCheck = cfg.utls.createTempVirtualRaster(bList, bListNum, 'Yes', 'Yes', 0, 'No', 'Yes')
				# last iteration
				if b == len(cfg.bndSetLst)-1:
					crossRstPath = combRstPath
				else:
					if vrtR == 'No':
						crossRstPath = cfg.utls.createTempRasterPath('tif')
					else:
						crossRstPath = cfg.utls.createTempRasterPath('vrt')
					tempRasters.append(crossRstPath)
				# check projections
				left, right, top, bottom, cRPX, cRPY, rP, un = cfg.utls.imageGeoTransform(vrtCheck)
				# calculation
				cfg.parallelArrayDict = {}
				o = cfg.utls.multiProcessRaster(rasterPath = vrtCheck, functionBand = 'No', functionRaster = cfg.utls.crossRasters, outputRasterList = [crossRstPath], nodataValue = nD,  functionBandArgument = reclassList, functionVariable = e, progressMessage = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Cross classification step ') + str(b) + '/' + str(len(cfg.bndSetLst)-1), outputNoDataValue = 0,  virtualRaster = vrtR, compress = cfg.rasterCompression, dataType = 'UInt16')
				# calculate unique values
				values = cfg.np.array([])
				sumVal = cfg.np.array([])
				for x in sorted(cfg.parallelArrayDict):
					try:
						for ar in cfg.parallelArrayDict[x]:
							values = cfg.np.append(values, ar[1][0, ::])
							sumVal = cfg.np.append(sumVal, ar[1][1, ::])
					except:
						if batch == 'No':
							cfg.utls.finishSound()
							cfg.utls.sendSMTPMessage(None, str(__name__))
							# enable map canvas render
							cfg.cnvs.setRenderFlag(True)
							cfg.uiUtls.removeProgressBar()			
						# logger
						cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR values')
						cfg.mx.msgErr9()		
						return 'No'
				reclRasterBandUniqueVal = {}
				values = values.astype(int)
				for v in range(0, len(values)):
					try:
						reclRasterBandUniqueVal[values[v]] = reclRasterBandUniqueVal[values[v]] + sumVal[v]
					except:
						reclRasterBandUniqueVal[values[v]] = sumVal[v]
				rasterBandUniqueVal = {}
				for v in range(0, len(values)):
					cmbX = cmbntns[values[v]]
					rasterBandUniqueVal[tuple(cmbX)] = [reclRasterBandUniqueVal[values[v]], values[v]]
				referenceR = crossRstPath
				refRasterBandUniqueVal = list(set(values))
			# remove temporary rasters
			tempRasters
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'cross raster output: ' + str(combRstPath))
			cfg.uiUtls.updateBar(80)
			# table output
			tblOut = cfg.osSCP.path.dirname(combRstPath) + '/' + cfg.utls.fileNameNoExt(combRstPath) + '.csv'
			try:
				l = open(tblOut, 'w')
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
				return 'No'
			t = cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'RasterValue') + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Combination') + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'PixelSum') + '\t' + cfg.QtWidgetsSCP.QApplication.translate('semiautomaticclassificationplugin', 'Area [' + un + '^2]') + str('\n')
			l.write(t)
			for c in cmbntns:
				try:
					v = tuple(cmbntns[c])
					if rasterBandUniqueVal[v][0] > 0:
						area = str(rasterBandUniqueVal[v][0] * cRPX * cRPY)
						cList = str(c) + '\t' + ','.join([str(l).replace('.0', '') for l in cmbntns[c]]) + '\t' + str(rasterBandUniqueVal[v][0]) + '\t' + area + str('\n')
						l.write(cList)
				except:
					pass
			l.close()
			# add raster to layers
			rastUniqueVal = cfg.np.unique(values).tolist()
			rstr =cfg.utls.addRasterLayer(combRstPath)
			cfg.utls.rasterSymbolGeneric(rstr, 'NoData', rasterUniqueValueList = rastUniqueVal)	
			try:
				f = open(tblOut)
				if cfg.osSCP.path.isfile(tblOut):
					eM = f.read()
					cfg.ui.band_set_comb_textBrowser.setText(eM)
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' cross matrix calculated')
			except Exception as err:
				# logger
				cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), ' ERROR exception: ' + str(err))
			cfg.uiUtls.updateBar(100)
			if batch == 'No':
				# enable map canvas render
				cfg.cnvs.setRenderFlag(True)
				cfg.utls.finishSound()
				cfg.utls.sendSMTPMessage(None, str(__name__))
				cfg.ui.toolBox_band_set_combination.setCurrentIndex(1)
				cfg.uiUtls.removeProgressBar()
			# logger
			cfg.utls.logCondition(str(__name__) + '-' + str(cfg.inspectSCP.stack()[0][3])+ ' ' + cfg.utls.lineOfCode(), 'finished')
	