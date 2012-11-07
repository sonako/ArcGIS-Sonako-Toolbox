# -*- coding: utf-8 -*-

"""
Allows to the user to truncate all tables in ArcGIS GDB.

ArcGIS: 10.1
"""

__author__ = 'Hidenori TERANO'
__version__ = '0.9.0'
__date__ = '06 November 2012'

import os
import arcpy

class Toolbox(object):
    def __init__(self):
        self.label =  u'terano toolbox'
        self.alias  = u'teranotools"'

        # List of tool classes associated with this toolbox
        self.tools = [WorkspaceTruncater] 


class WorkspaceTruncater(object):
	def __init__(self):
		self.label = u'WorkspaceTruncater'
		self.description = u'allows to the user to truncate all tables in workspace.'
		self.canRunInBackground = False
	
	
	def getParameterInfo(self):
		params = []
		# arcgis bug?
		# params.append(arcpy.Parameter(displayName = u'Target Workspace', name = 't_workspace', datatype = u'Workspace', parameterType = 'Required', direction = 'Input'))
		params.append(arcpy.Parameter(displayName = u'Target Workspace', name = 't_workspace', datatype = u'ワークスペース', parameterType = 'Required', direction = 'Input'))
		params.append(arcpy.Parameter(displayName = u'Skip Table', name = 'skip_obj', datatype = 'String', parameterType = 'Optional', direction = 'Input', multiValue = True))
		
		return params
	
	
	def isLicensed(self):
		return True
	
	
	def updateParameters(self, parameters):
		workspace = parameters[0].valueAsText
		if arcpy.env.workspace != workspace:
			arcpy.env.workspace = workspace
			listobj = arcpy.ListFeatureClasses()
			listobj.extend(arcpy.ListTables())
			parameters[1].filter.list = listobj
		
		return
	
	
	def updateMessages(self, parameters):
		return
	
	
	def execute(self, parameters, message):
		# パラメータの設定
		targetWs = parameters[0].valueAsText
		skipItems = None
		if parameters[1].values != None:
			skipItems = parameters[1].values
		
		
		self.truncate(targetWs, skipItems)
	
	
	def truncate(self, targetWorkspace, skip = None):
		'''
			ArcGISのFGDBの全フィーチャクラス、全テーブルのレコードをトランケートする。
			トランケート対象としないオブジェクト(fcやテーブル)を文字列の配列で指定する
		'''
		if skip == None:
			skip = ()
		
		# 処理対象の取得
		if arcpy.env.workspace != targetWorkspace:
			arcpy.env.workspace = targetWorkspace
		targetList = arcpy.ListFeatureClasses()
		targetList.extend(arcpy.ListTables())
		
		
		# トランケートする
		self.truncateObjects([ os.path.join(targetWorkspace, obj) for obj in targetList if not obj in skip ])


	def truncateObjects(self, targetObject):
		'''
			指定されたオブジェクトをトランケートする
		'''
		if isinstance(targetObject, basestring):
			targetObject = (targetObject,)
		
		for obj in targetObject:
			arcpy.TruncateTable_management(obj)
			arcpy.AddMessage(u'%sを削除しました' % obj)
		
		
