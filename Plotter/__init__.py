import os
import sys

## regular expressions
import re

## lst subprocess
from glob import glob
from subprocess import *


# remove argv, otherwise if -b change ROOT Behaviour
sys.argv=[]
import ROOT

class BaseDraw():
	types={"TH1D":1,"TGraph":2,"TH2D":3}
	styles={"line":1,"marker":2,"band":3}

	__init__():
		self.style = styles["line"]
		self.styleopt = 21
		self.color = ROOT.kBlack
		self.width = 1
		pass
	__del__():
		pass
	def Draw():
		return self
	def SetMarker():
		self.style=styles["marker"]
		return self
	def SetLine():
		self.style=styles["line"]
		return self
	def SetBand():
		self.style=styles["band"]
		return self
	def CopyStyle( other ):
		self.style = other.style
		self.styleopt= other.styleopt
		self.color= other.color
		self.width = other.width
		self.shift = other.shift
		self.length = other.length
		return self

class DrawCollection():
	__init__():
		self.objs=[]
		self.cur=0
	__del__():
		pass
	__len__(self):
		return len(self.objs)
	__iter__(self):
		for  x in self.objs:
			yield x
	__next__(self):
		if self.cur < len(self) :
			self.cur +=1 
			return self.objs[self.cur - 1 ]
		else: 
			raise StopIteration
		pass

class Graph(BaseDraw):
	__init__():
		self.graph=None
		self.graphRange=None

	__del__():
		if self.graph != None:
			self.graph.Delete()
			self.graph=None

	def Empty(name):
		''' Init empty TGraph with name = name'''
		self.graph=ROOT.TGraphAsymmError()
		self.graph.SetName(name)
		return self

	def AddPoint(x,y,dx=0,dy=0):
		'''Add a point with symmetric errors '''
		n=self.graph.GetN()
		self.graph.SetPoint(n, x,y)
		self.graph.SetPointError(n, dx, dx, dy, dy)
		return self

	def AddPoint(x,y,exl,exh,eyl,eyh):
		'''Add a point with asymmetric errors '''
		n=self.graph.GetN()
		self.graph.SetPoint(n, x,y)
		self.graph.SetPointError(n, exl, exh, eyl, eyh)
		return self

	def Range(ymin,ymax):
		''' Change aspects points in such a way that the errors are in the yrange.
		    This is performed by filling the graphRange histo that will be drawn w/o markers
		'''
		delta=ymax-ymin
		self.graphRange=ROOT.TGraphAsymmError()  
		self.graphRange.SetName(self.graph.GetName()+"_rangefix") 
		for i in range(0,self.graph.GetN() ):
			x=self.graph.GetX()[i]
			y=self.graph.GetY()[i]
			exl=self.graph.GetEXlow()[i]
			exh=self.graph.GetEXhigh()[i]
			eyl=self.graph.GetEYlow()[i]
			eyh=self.graph.GetEYhigh()[i]
			if y> ymax and y-eyl < ymax:
				n=self.graphRange.GetN()
				self.graphRange.SetPoint(n,x,ymax)
				self.graphRange.SetPointError(n,0,0, ymax-y+eyl, eyh+y-ymax)
			if y< ymin and y+eyh > ymin:
				n=self.graphRange.GetN()
				self.graphRange.SetPoint(n,x,ymin)
				self.graphRange.SetPointError(n,0,0, ymin -y +eyl, eyh+y-ymin)
		return self	

	def Draw():
		if self.style == styles["marker"]:
			self.graph.SetMarkerStyle(self.styleopt)
			self.graph.SetLineColor(self.color)
			self.graph.SetMarkerColor(self.color)
			self.graph.SetLineWidth(self.width)
			self.graph.Draw("P SAME")
			if self.graphRange != None:
				self.graphRange.SetMarkerStyle(0)
				self.graphRange.SetMarkerSize(self.0)
				self.graphRange.SetLineColor(self.color)
				self.graphRange.SetMarkerColor(self.color)
				self.graphRange.SetLineWidth(self.width)
				self.graphRange.Draw("P SAME")
		if self.style == styles["band"]:
			self.graph.SetFillStyle(self.styleopt)
			self.graph.SetLineColor(self.color)
			self.graph.SetFillColor(self.color)
			self.graph.SetLineWidth(self.width)
			self.graph.Draw("E2 SAME")
			if self.graphRange != None:
				self.graphRange.SetMarkerStyle(0)
				self.graphRange.SetMarkerSize(self.0)
				self.graphRange.SetFillStyle(self.styleopt)
				self.graphRange.SetLineColor(self.color)
				self.graphRange.SetFillColor(self.color)
				self.graphRange.SetLineWidth(self.width)
				self.graphRange.Draw("E2 SAME")

		return self

class Histo(BaseDraw):
	__init__():
		self.hist=None
		self.xerror=False
		self.yerror=True
		# for markers and bands
		self.shift=0
		self.length=0

	def ConvertToGraph():
		g=Graph(self.hist.GetName()+"_graph")
		g.CopyStyle(self)
		for i in range(1, self.hist.GetNbinsX()+1):
			ex=0
			if self.xerror:
				ex=self.hist.GetBinWidth(i)

			x = self.hist.GetBinCenter(i)
			y = self.hist.GetBinContent(i)
			ey = self.hist.GetBinError(i) 

			#apply shift and length for bands
			if self.shift>0: x+= self.shift
			if self.shift>0 and self.length>0: ex=self.length

			g.AddPoint(  x, y, ex, ey ) 
		return g

	def Draw():
		if self.style==styles["marker"] or self.style==styles["band"]:
			# transform it to a Graph
			self.mygraph=self.ConvertToGraph()
			self.mygraph.Draw()

		elif self.style == styles["line"]:
			self.hist.SetLineColor(self.color)
			self.hist.SetLineWidth(self.width)
			self.hist.SetLineStyle(self.optstyle)
			self.hist.Draw("L SAME")

		return self

class Plotter:
	__init__(cfg, verbose=0):
		#parse config
		self.canv=None
		self.cfg=config
		self.canv_res=[800,800]
		self.verbose=verbose
		if "base" not in cfg: raise TypeError
		if "drawList" not in cfg: 
			print>>sys.stderr, "--> You should indicate what you want to draw in drawList"
			raise TypeError
		for l in cfg["base"]["drawList"]:
			if self.verbose >0: print "-> Adding Object '"+l+"' to the list to be drawn"
			if l not in cfg: 
				print>>sys.stderr, "Object '"+l+"' in drawList but not configured" 
				raise NameError
		if "legend" not in cfg: 
			self.cfg["legend"] ={}
			self.cfg["legend"]["draw"]="False"
	__del__():
		pass
	def LoadTH1(name):
		return self
	# public 
	def DrawCMS():
		return self
	def DrawLegend():
		return self
	def Draw():
		# CREATE CANVAS
		if "canv" not in cfg["base"]:
			self.canv=ROOT.TCanvas("canv","canv",800,800)
		else:
			self.canv=ROOT.TCanvas("canv","canv",
					int(self.cfg["base"]["canv"].split(',')[0]),
					int(self.cfg["base"]["canv"].split(',')[1]),
					)
		return self
	def Save():
		return self

