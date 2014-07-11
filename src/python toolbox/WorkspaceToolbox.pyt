# -*- coding: utf-8 -*-

"""
1. Allows to the user to truncate all tables in ArcGIS GDB.
1. Allows to the user to delete all tables and domains in ArcGIS GDB.
"""

__author__ = 'Hidenori TERANO'
__version__ = '0.9.1'
__date__ = '15 November 2012'

import os
import arcpy

class Toolbox(object):
    def __init__(self):
        self.label =  u'terano toolbox'
        self.alias  = u'teranotools"'

        # List of tool classes associated with this toolbox
        self.tools = [WorkspaceTruncater, WorkspaceCleaner] 


class WorkspaceTruncater(object):
	'''
		ワークスペース内にある全テーブル、フィーチャクラスのレコードを削除します
	'''
	def __init__(self):
		self.label = u'WorkspaceTruncater'
		# self.description = u'allows to the user to truncate all tables in workspace.'
		self.description = u'ワークスペース内にある全テーブル、フィーチャクラスのレコードを削除します'
		self.canRunInBackground = False
	
	
	def getParameterInfo(self):
		params = []
		# params.append(arcpy.Parameter(displayName = u'Target Workspace', name = 't_workspace', datatype = u'Workspace', parameterType = 'Required', direction = 'Input'))
		params.append(arcpy.Parameter(displayName = u'処理対象のワークスペース', name = 't_workspace', datatype = u'ワークスペース', parameterType = 'Required', direction = 'Input'))
		params.append(arcpy.Parameter(displayName = u'処理対象外のオブジェクト', name = 'skip_obj', datatype = 'String', parameterType = 'Optional', direction = 'Input', multiValue = True))
		
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


class WorkspaceCleaner(object):
	'''
		ワークスペース内にある全テーブル、フィーチャクラス、ドメインを削除します
	'''
	def __init__(self):
		self.label = u'WorkspaceCleaner'
		# self.description = u'allows to the user to delete all tables and domains in workspace.'
		self.description = u'ワークスペース内にある全テーブル、フィーチャクラス、ドメインを削除します'
		self.canRunInBackground = False
	
	
	def getParameterInfo(self):
		params = []
		# arcgis bug?
		# params.append(arcpy.Parameter(displayName = u'Target Workspace', name = 't_workspace', datatype = u'Workspace', parameterType = 'Required', direction = 'Input'))
		params.append(arcpy.Parameter(displayName = u'処理対象のワークスペース', name = 't_workspace', datatype = u'ワークスペース', parameterType = 'Required', direction = 'Input'))
		params.append(arcpy.Parameter(displayName = u'処理対象外のオブジェクト', name = 'skip_obj', datatype = 'String', parameterType = 'Optional', direction = 'Input', multiValue = True))
		params.append(arcpy.Parameter(displayName = u'処理対象外のドメイン', name = 'skip_domain', datatype = 'String', parameterType = 'Optional', direction = 'Input', multiValue = True))
		
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
			domains = arcpy.da.ListDomains(workspace)
			parameters[2].filter.list = [ domain.name for domain in domains ]
		return
	
	
	def updateMessages(self, parameters):
		return
	
	
	def execute(self, parameters, message):
		# パラメータの設定
		targetWs = parameters[0].valueAsText
		skipTables = skipDomains = None
		if parameters[1].values != None:
			skipTables = parameters[1].values
		if parameters[2].values != None:
			skipDomains = parameters[2].values
		
		
		self.deleteObject(targetWs, skipTables, skipDomains)
	
	
	def deleteObject(self, targetWorkspace, skip_obj = None, skip_domain = None):
		'''
			ArcGISのFGDBの全フィーチャクラス、全テーブルのレコードをトランケートする。
			トランケート対象としないオブジェクト(fcやテーブル)を文字列の配列で指定する
		'''
		if skip_obj == None:
			skip_obj = ()
		
		if skip_domain == None:
			skip_domain = ()
		
		
		# 処理対象のテーブル取得
		if arcpy.env.workspace != targetWorkspace:
			arcpy.env.workspace = targetWorkspace
		targetList = arcpy.ListFeatureClasses()
		targetList.extend(arcpy.ListTables())
		
		# トランケートする
		self.deleteTables([ os.path.join(targetWorkspace, obj) for obj in targetList if not obj in skip_obj ])
		
		# 処理対象のドメイン取得
		if arcpy.env.workspace != targetWorkspace:
			arcpy.env.workspace = targetWorkspace
		targetList = arcpy.da.ListDomains(targetWorkspace)
		
		# ドメイン削除する
		self.deleteDomains(targetWorkspace, [ obj.name for obj in targetList if not obj in skip_domain ])
	
	
	def deleteTables(self, targetTables):
		'''
			指定されたオブジェクトをトランケートする
		'''
		if isinstance(targetTables, basestring):
			targetTables = (targetTables,)
		
		for obj in targetTables:
			arcpy.Delete_management(obj)
			arcpy.AddMessage(u'%sを削除しました' % obj)
	
	
	def deleteDomains(self, workspace, targetDomains):
		'''
			指定されたドメインを削除する
		'''
		if isinstance(targetDomains, basestring):
			targetDomains = (targetDomains,)
		
		for obj in targetDomains:
			arcpy.DeleteDomain_management(workspace, obj)
			arcpy.AddMessage(u'%sを削除しました' % obj)
