# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- animation workbench
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
from __future__ import unicode_literals

__vers__="05.04.2016  0.3"



import sys
import os
import random
import numpy as np
import time


__dir__ = os.path.dirname(__file__)	

import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import PySide
from PySide import QtCore, QtGui

import reconstruction
reload (reconstruction.projectiontools)
from reconstruction.projectiontools import *

import reconstruction.miki as miki
reload(miki)


def sayd(s):
	if hasattr(FreeCAD,'animation_debug'):
		pass
		FreeCAD.Console.PrintMessage(str(s)+"\n")

def say(s):
		FreeCAD.Console.PrintMessage(str(s)+"\n")

def sayErr(s):
		FreeCAD.Console.PrintError(str(s)+"\n")


import Animation

class _MPL(Animation._Actor):

	def __init__(self,obj,icon='/icons/animation.png'):
		obj.Proxy = self
		self.Type = self.__class__.__name__
		self.obj2 = obj
		
		self.vals={}
#		self.vals1={}
#		self.vals2={}
#		self.vals3={}
#		
		_ViewProviderMPL(obj.ViewObject,icon) 


	def onChanged(self,obj,prop):
#		say(["onChanged " + str(self),obj,prop,obj.getPropertyByName(prop)])
		if prop == 'countSources':
			for i in range(obj.countSources):
				try:
					obj.getPropertyByName('source'+str(i+1)+'Object')
				except:
					obj.addProperty('App::PropertyLink','source'+str(i+1)+'Object',"Source " + str(i+1))
					obj.addProperty('App::PropertyString','source'+str(i+1)+'Data',"Source " + str(i+1))
					obj.addProperty('App::PropertyFloatList','source'+str(i+1)+'Values',"Source " + str(i+1))
					obj.addProperty('App::PropertyBool','source'+str(i+1)+'Off',"Source " + str(i+1))
					exec("self.vals"+str(i+1)+"={}")
			for i in range(10):
				if i<obj.countSources: mode=0
				else: mode=2
				try:
					obj.setEditorMode("source"+str(i+1)+"Object", mode)
					obj.setEditorMode("source"+str(i+1)+"Data", mode)
					obj.setEditorMode("source"+str(i+1)+"Values", mode)
					obj.setEditorMode("source"+str(i+1)+"Off", mode)
				except:
					break
		pass

	def onBeforeChange(self,obj,prop):
		#say(["on Before Changed ",obj.Label,prop,obj.getPropertyByName(prop)])
		pass


	def execute(self,obj):
		print "execute"
		if not obj.record:
			print "no recording"
			return

		print obj.sourceObject.Label
		src=obj.sourceObject
		vs='src.'+obj.sourceData
		v=eval(vs)
		self.vals[v]=v

		for i in range(obj.countSources):
			exec("src"+str(i+1)+"=obj.source"+str(i+1)+"Object")
			exec("ss=obj.source"+str(i+1)+"Object")
			if ss <> None:
				vs2="obj.source"+str(i+1)+"Data"
				v2=eval(vs2)
				vs3="ss."+v2
				v3=eval(vs3)
				tt=eval("self.vals"+str(i+1))
				tt[v]=v3
		return

	def onDocumentRestored(self, fp):
		say(["onDocumentRestored",fp,fp.Label])




class _ViewProviderMPL(Animation._ViewProviderActor):
 
	def __init__(self,vobj,icon='/icons/icon1.svg'):
		self.iconpath = icon
		print self.iconpath
		self.Object = vobj.Object
		vobj.Proxy = self
		self.cmenu=[]
		self.emenu=[]
		self.vers=__vers__
 
	def getIcon(self):
		return  __dir__+ '/icons/icon1.svg'

	def attach(self,vobj):
		print "attach---------------------MLP-----------"
		self.emenu=[]
		self.Object = vobj.Object

	def createDialog(self):
		app=MyApp()
		miki2=miki.Miki()
		miki2.app=app
		app.root=miki2
		app.obj=self.Object
		self.Object.Proxy.app=app
		self.edit= lambda:miki2.run(MyApp.s6,app.create2)

	def setupContextMenu(self, obj, menu):
		self.createDialog()

		cl=self.Object.Proxy.__class__.__name__
		action = menu.addAction("About " + cl)
		action.triggered.connect(self.showVersion)

		action = menu.addAction("Edit ...")
		action.triggered.connect(self.edit)


	def setEdit(self,vobj,mode=0):
		self.createDialog()
		self.edit()
		FreeCAD.ActiveDocument.recompute()
		return True



class MatplotlibWidget(FigureCanvas):

	def __init__(self, parent=None, width=5, height=4, dpi=100):

		super(MatplotlibWidget, self).__init__(Figure())
		self.setParent(parent)
		self.figure = Figure(figsize=(width, height), dpi=dpi) 
		self.canvas = FigureCanvas(self.figure)

		FigureCanvas.setSizePolicy(self,
				QtGui.QSizePolicy.Expanding,
				QtGui.QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

		self.axes = self.figure.add_subplot(111)
		self.setMinimumSize(self.size())



class MyApp(object):


	s6='''
VerticalLayout:
		id:'main'
#		setFixedHeight: 500
#		setFixedWidth: 500
#		move:  PySide.QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"***    My    M A T P L O T L I B     ***"
		
'''

	def plot(self):
		
		self.mpl.figure.clf()
		self.mpl.canvas = FigureCanvas(self.mpl.figure)
		FigureCanvas.updateGeometry(self.mpl)

		self.mpl.axes = self.mpl.figure.add_subplot(111)
		self.mpl.draw()

		vals=self.obj.Proxy.vals
		x=[]
		y=[]

		for k in vals:
			x.append(k)
			y.append(vals[k])

		self.obj.sourceValues=y

		for i in range(self.obj.countSources):
			nr=str(i+1)
			ss=eval("self.obj.source"+nr+"Object")
			sf=eval("self.obj.source"+nr+"Off")
			if ss<>None and not sf:
				exec("vals=self.obj.Proxy.vals"+nr)
				x2=[k for k in vals]
				y1=[vals[k] for k in vals]
				exec("label=self.obj.source"+nr+"Object.Label + ': ' + self.obj.source"+nr+"Data")
				t=self.mpl.axes.plot(x,y1,label=label)
				exec("self.obj.source"+nr+"Values=y1")

		if self.obj.useNumpy:
			self.obj.outTime=self.obj.sourceNumpy.outTime

		FreeCAD.activeDocument().recompute()

		for i in range(10):
				if eval("self.obj.useOut"+str(i))
					y=self.obj.sourceNumpy.getPropertyByName('out'+str(i))
					label=self.obj.sourceNumpy.getPropertyByName('label'+str(i))
					if label=='':
						label="numpy " + str(i)

					x=range(len(y))
					t=self.mpl.axes.plot(x,y,label=label)
					exec("self.obj.out"+str(i)+"="+str(y))

		legend = self.mpl.axes.legend(loc='upper right', shadow=True)
		self.mpl.draw()
		self.mpl.figure.canvas.draw()


	def reset(self):
		self.obj.Proxy.vals={}
		self.obj.sourceValues=[]
		for i in range(self.obj.countSources):
			nr=str(i+1)
			exec("self.obj.Proxy.vals"+nr+"={}")
			exec("self.obj.source"+nr+"Values=[]"

		self.mpl.figure.clf()
		self.mpl.canvas = FigureCanvas(self.mpl.figure)

		FigureCanvas.updateGeometry(self.mpl)
		self.mpl.axes = self.mpl.figure.add_subplot(111)
		self.mpl.draw()
		self.plot()


	def create2(self):
		par=self.root.ids['main']

		self.mpl=MatplotlibWidget()
		bt=QtGui.QPushButton("update diagram")
		bt.clicked.connect(self.plot)

		bt2=QtGui.QPushButton("reset data")
		bt2.clicked.connect(self.reset)

		self.root.ids['main'].layout.addWidget(self.mpl)
		self.root.ids['main'].layout.addWidget(bt)
		self.root.ids['main'].layout.addWidget(bt2)
		self.root.ids['main'].layout.setStretchFactor(self.mpl, 1)

		self.plot()



def createMPL(base=False):

	print "create MPL ..."
	obj=FreeCAD.ActiveDocument.addObject('App::DocumentObjectGroupPython','Plot')

	obj.addProperty('App::PropertyBool','record',"Base",'true record, false no record data')
	obj.addProperty('App::PropertyInteger','countSources',"Base")
	obj.countSources=0

	# base data time/step
	obj.addProperty('App::PropertyLink','sourceObject',"Time")
	obj.addProperty('App::PropertyString','sourceData',"Time")
	obj.addProperty('App::PropertyFloatList','sourceValues',"Time")

	obj.addProperty('App::PropertyBool','useNumpy',"numpy source" )
	obj.addProperty('App::PropertyLink','sourceNumpy',"numpy source" )

	for i in range(10):
		obj.addProperty('App::PropertyBool','useOut'+str(i),"numpy source" )
		obj.addProperty('App::PropertyFloatList','out'+str(i),"out values")

	obj.addProperty('App::PropertyFloatList','outTime',"out values")

	if not base:
		_MPL(obj,'/icons/bounder.png')
		_ViewProviderMPL(obj.ViewObject,__dir__+ '/icons/icon1.svg') 
		
		obj.countSources=1

		app=MyApp()
		miki2=miki.Miki()
		miki2.app=app
		app.root=miki2
		app.obj=obj
		obj.Proxy.app=app

		obj.ViewObject.Proxy.edit= lambda:miki2.run(MyApp.s6,app.create2)
	return obj



if False:

	t=createMPL()
	t.sourceObject= App.ActiveDocument.My_Manager
	t.sourceData="step"

	t.source1Object= App.ActiveDocument.Box001
	t.source1Data="Placement.Rotation.Angle"


	t.source2Object= App.ActiveDocument.Box001
	t.source2Data="Placement.Base.x"

	t.source3Object= App.ActiveDocument.Box001
	t.source3Data="Placement.Base.y"

	# t.expression2="2* np.arctan2(in2,in3)"

	t.record=True

	t.source2Values=[1,2,3,4]
	t.source3Values=[1,3,2,5]
	App.ActiveDocument.Numpy.sourceObject=t


	t2=createMPL()
	t2.sourceObject= App.ActiveDocument.My_Manager
	t2.sourceData="step"

	t2.source1Object= App.ActiveDocument.Box001
	t2.source1Data="Placement.Rotation.Angle"


	t2.sourceObject= App.ActiveDocument.My_Manager
	t2.useNumpy=True
	t2.sourceNumpy=App.ActiveDocument.Numpy
	t2.useOut0=True
	t2.useOut1=True
	t2.useOut2=True
	t2.record=True

		
