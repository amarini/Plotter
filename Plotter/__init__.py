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

class BaseDraw:
	''' Base Class for Objects that can be drawn'''
	def __init__(self):
		self.types={"TH1D":1,"TGraph":2,"TH2D":3}
		self.styles={"line":1,"marker":2,"band":3}
		self.style = styles["line"]
		self.styleopt = 21
		self.color = ROOT.kBlack
		self.width = 1
		self.obj = None
		pass 

	def __del__(self):
		pass

	def Draw(self):
		return self

	def SetMarker(self):
		self.style=styles["marker"]
		return self

	def SetLine(self):
		self.style=styles["line"]
		return self

	def SetBand(self):
		self.style=styles["band"]
		return self

	def SetStyle(self, string):
		if string.lower()=="band": self.SetBand()
		if string.lower()=="line": self.SetLine()
		if string.lower()=="marker": self.SetMarker()
		return self

	def CopyStyle(self, other ):
		self.style = other.style
		self.styleopt= other.styleopt
		self.color= other.color
		self.width = other.width
		self.shift = other.shift
		self.length = other.length
		return self

class Collection:
	'''Store a collection of drawable objects'''
	def __init__(self):
		self.objs={}
		self.names=[]
		self.cur=0
	def __del__(self):
		pass
	def __len__(self):
		return len(self.objs)
	def __iter__(self):
		for  x in self.objs:
			yield x
	def __next__(self):
		if self.cur < len(self) :
			self.cur +=1 
			return self.objs[ self.names[ self.cur - 1  ] ]
		else: 
			raise StopIteration
		pass
	def Add(self, name, obj):
		''' Add obj with name = name to the list '''
		self.objs.append(obj)
		self.names.append(name)
		return self
	def Remove(self, name):
		del self.objs[name]
		self.names[:] = [x for x in self.names and x != name ]
		return self
	def Get(self, name):
		return self.objs[name]

class Graph(BaseDraw):
	''' Implement a Graph object '''
	def __init__(self):
		self.graph=None
		self.graphRange=None

	def __del__(self):
		if self.graph != None:
			self.graph.Delete()
			self.graph=None

	def Empty(self, name):
		''' Init empty TGraph with name = name'''
		self.graph=ROOT.TGraphAsymmError()
		self.graph.SetName(name)
		return self

	def AddPoint(self, x, y, dx=0, dy=0):
		'''Add a point with symmetric errors '''
		n=self.graph.GetN()
		self.graph.SetPoint(n, x,y)
		self.graph.SetPointError(n, dx, dx, dy, dy)
		return self

	def AddPoint(self, x, y, exl, exh, eyl, eyh):
		'''Add a point with asymmetric errors '''
		n=self.graph.GetN()
		self.graph.SetPoint(n, x,y)
		self.graph.SetPointError(n, exl, exh, eyl, eyh)
		return self

	def Range(self, ymin,ymax):
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

	def Draw(self):
		if self.style == styles["marker"]:
			self.graph.SetMarkerStyle(self.styleopt)
			self.graph.SetLineColor(self.color)
			self.graph.SetMarkerColor(self.color)
			self.graph.SetLineWidth(self.width)
			self.graph.Draw("P SAME")
			if self.graphRange != None:
				self.graphRange.SetMarkerStyle(0)
				self.graphRange.SetMarkerSize(0)
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
				self.graphRange.SetMarkerSize(0)
				self.graphRange.SetFillStyle(self.styleopt)
				self.graphRange.SetLineColor(self.color)
				self.graphRange.SetFillColor(self.color)
				self.graphRange.SetLineWidth(self.width)
				self.graphRange.Draw("E2 SAME")

		return self

class Histo(BaseDraw):
	def __init__(self):
		super(Histo, self).__init__()
		self.hist=None
		self.xerror=False
		self.yerror=True
		# for markers and bands
		self.shift=0
		self.length=0

	def ConvertToGraph(self):
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

	def Draw(self):
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
	def __init__(self, cfg, verbose=0):
		#parse config
		self.canv=None
		self.cfg=cfg
		self.canv_res=[800,800]
		self.verbose=verbose
		self.collection=Collection()
		self.newcolorindex=2340  ## just unused
		self.newcolors=[]
		## make me configurable
		self.labelsize=24
		self.titlesize=28
		self.entrysize=24
		self.ratiofraction=0.2
		self.axisHist=None
		## sanity checks
		if "base" not in cfg: raise TypeError
		if "drawList" not in cfg: 
			print>>sys.stderr, "--> You should indicate what you want to draw in drawList"
			raise TypeError

		if "legend" not in cfg: 
			self.cfg["legend"] ={}
			self.cfg["legend"]["draw"]="False"

		for name in cfg["base"]["drawList"]:
			if self.verbose >0: print "-> Adding Object '"+l+"' to the list to be drawn"
			if name not in cfg: 
				print>>sys.stderr, "Object '"+l+"' in drawList but not configured" 
				raise NameError
			##### Create obj
			self.LoadObj( name )
	def __del__(self):
		pass
	def LoadObj(self, name):
		if self.verbose:
			print "--- Loading Histo "+name+" ---"
		if "file" not in self.cfg[name]: 
			print >>sys.stderr, "file not specified in cfg for histo", name
			raise TypeError
		if "obj"  not in self.cfg[name]:
			print >>sys.stderr, "obj not specified in cfg for histo", name
			raise TypeError
		f = ROOT.TFile.Open(self.cfg[name]["file"] )
		h = f.Get(self.cfg[name]["obj"])
		#TODO -> TH2D
		if self.cfg[name]["type"].lower() ==  "th1d":
			obj=Histo(name)
			obj.obj = h
		if self.cfg[name]["type"].lower() == "tgraph":
			obj=Graph(name)
			obj.obj = h

		if "style" in self.cfg[name]:obj.SetStyle(self.cfg[name]["style"])
		# 
		color = ColorKey(name,"color")
		if color>=0: obj.color=color
		#
		styleopt = ColorKey(name,"styleopt")
		if styleopt >0 : obj.styleopt=styleopt
		#
		if "len" in self.cfg[name]: obj.length = float(self.cfg[name]["len"])
		if "shift" in self.cfg[name]: obj.shift = float(self.cfg[name]["shift"])
		if "width" in self.cfg[name]: obj.width = int(self.cfg[name]["width"])
		#
		self.collection.Add(name,obj)
		return self
	# public 
	def DrawCMS(self):
		if "text" not in self.cfg["text"]: self.cfg["text"]["text"]= "CMS"
		latex = ROOT.TLatex()
		latex.SetNDC()
		latex.SetFontSize(0.04)
		latex.SetTextFont(42)
		mytext="CMS"
		if self.cfg["text"]["text"].lower() == "cms": mytext="#bf{CMS}"
		if self.cfg["text"]["text"].lower() == "preliminary" : mytext="#bf{CMS},#scale[0.75]{ #it{Preliminary}}"
		if self.cfg["text"]["text"].lower() == "unpublished" : mytext="#bf{CMS},#scale[0.75]{ #it{Unpublished}}"
		if "position" not in self.cfg["text"] :  self.cfg["text"]["position"]="tl"

		if self.cfg["text"]["position"].lower()[0] == "d":
			if self.cfg["text"]["text"].lower() == "preliminary": mytext="#splitline{#bf{CMS}}{#scale[0.75]{#it{Preliminary}}}"
			if self.cfg["text"]["text"].lower() == "unpublished": mytext="#splitline{#bf{CMS}}{#scale[0.75]{#it{Unpublished}}}"
			if self.cfg["text"]["position"].lower() == "dtl": self.cfg["text"]["position"] = "tl"
			if self.cfg["text"]["position"].lower() == "dtr": self.cfg["text"]["position"] = "tr"
			if self.cfg["text"]["position"].lower() == "dbl": self.cfg["text"]["position"] = "bl"
			if self.cfg["text"]["position"].lower() == "dbr": self.cfg["text"]["position"] = "br"

		if self.cfg["text"]["position"].lower()=="tl":
			latex.SetTextAlign(31)
			x=self.canv.GetLeftMargin()+ 0.02
			y=1-self.canv.GetTopMargin() -0.02
		elif self.cfg["text"]["position"].lower()=="tr":
			latex.SetTextAlign(33)
			x=1-self.canv.GetRightMargin()- 0.02
			y=1-self.canv.GetTopMargin() -0.02
		elif self.cfg["text"]["position"].lower()=="bl":
			latex.SetTextAlign(11)
			x=self.canv.GetLeftMargin()+ 0.02
			y=self.canv.GetBottomMargin() +0.02
		elif self.cfg["text"]["position"].lower()=="br":
			latex.SetTextAlign(13)
			x=1-self.canv.GetRightMargin()- 0.02
			y=self.canv.GetBottomMargin() +0.02

		latex.DrawLatex(mytext,x,y)

		#lumi always tr
		x=1-self.canv.GetRightMargin()- 0.01
		y=1-self.canv.GetTopMargin() +0.02
		latex.SetFontSize(0.03)
		latex.SetTextAlign(13)
		if "lumi" not in self.cfg["text"]: self.cfg["text"]["lumi"]="19.7 fb^{-1} (8TeV)"
		self.cfg["text"]["lumi"] = ParseString(self.cfg["text"]["lumi"]  )
		latex.DrawLatex(x,y,self.cfg["text"]["lumi"])

		if "extra" in self.cfg["text"]:
			latex.SetTextAlign(11)
			latex.SetTextSize(0.03)
			x=float(self.cfg["text"]["extra"].split('!')[0] )
			y=float(self.cfg["text"]["extra"].split('!')[1] )
			mytext=self.cfg["text"]["extra"].split('!')[2]
			mytext = ParseString(mytext)
			latex.DrawLatex(x,y,mytext)

		return self

	def ParseStr(self, string):
		''' Standard reparsing in the configfile for displayed text'''
		r=re.sub('~',' ',string)
		r=re.sub('@','#',string)
		return r

	def BoolKey(self, section, field, extraValues=False):
		'''Parse cfg section and field to return a bool'''
		if section not in self.cfg:
			print >>sys.stderr, "section ", section,"not in cfg"
			raise NameError
		if field not in self.cfg[section]:
			return False
		if self.cfg[section][field].lower() == "false": return False
		if self.cfg[section][field].lower() == "none": return False
		if self.cfg[section][field].lower() == "no": return False
		if self.cfg[section][field].lower() == "true": return True
		if self.cfg[section][field].lower() == "yes": return True

		if extraValues: return True
		print>>sys.stderr, "Unrecognized bool option", self.cfg[section][field],"in",section+":"+field
		raise NameError

	def ColorKey(self, section,field):
		''' return -1 in case of not found'''
		#self.newcolorindex=2340  ## just unused
		if section not in self.cfg:
			return -1
		if field not in self.cfg[section]:
			return -1
		colortext=cfg[section][field]
		if "ROOT" in colortext:
			exec("color="+colortext)
		elif "RGB" in colortext:
			r=float( colortext.split(',')[1])
			g=float( colortext.split(',')[2])
			b=float( colortext.split(',')[3])
			c=ROOT.TColor(self.newcolorindex,r,g,b)
			self.colors.append(c) ## garbage collector
			color=self.newcolorindex
			self.newcolorindex+=1
		else:
			color=int( colortext )
		return color

	def NumKey(self, section, field):
		if section not in self.cfg:
			print >> sys.stderr, "cfg section",section ," does not exist"
			raise TypeError
		if field not in self.cfg[section]:
			print >> sys.stderr, "cfg field",field, "in section",section,"does not exist"
			raise TypeError
		return int(self.cfg[section][field])

	def DrawLegend(self):
		if self.cfg["legend"]["draw"].lower() == "false": return self
		if self.cfg["legend"]["draw"].lower() == "no": return self

		if self.cfg["legend"]["draw"].lower() != "yes" and \
		   self.cfg["legend"]["draw"].lower() != "true":
			   print >>sys.stderr, "Unrecognized legend draw:",self.cfg["legend"]["draw"]
			   raise TypeError

		l=ROOT.TLegend()
		l.SetFillStyle(0)
		l.SetBorderSize(0)
		if "header" in self.cfg["legend"]:
			mytext= ParseStr(self.cfg["legend"]["header"])
			e=l.SetHeader(mytext)
			e.SetTextFont(43)
			e.SetTextSize(self.entrysize)
		if "legendList" not in self.cfg["legend"]: self.cfg["legend"]["legendList"]=""

		for p1 in self.cfg["legend"]["legendList"]:
			for name in p1.split(','):
				if "label" in self.cfg[name] : mylabel=self.cfg[name]["label"]
				else: mylabel = name

				mylabel=ParseStr(mylabel)

				if self.cfg[name]["style"].lower() == "marker": 
					mytype = "P"
					if BoolKey(name,"xerror"):
						mytype += "L"
					if BoolKey(name,"yerror"):
						mytype += "E"
				if self.cfg[name]["style"].lower() == "line": 
					mytype = "L"
				if self.cfg[name]["style"].lower() == "band": 
					mytype = "F"
				e=l.AddEntry(self.collection.Get(name),mylabel,mytype)
				e.SetTextFont(43)
				e.SetTextSize(self.entrysize)
		l.Draw()

		return self

	def DrawObjects(self):
		''' Draw all objects in the collection'''
		for x in self.collection:
			x.Draw()
		return self

	def DrawCanvas(self):
		# CREATE CANVAS
		if "canv" not in self.cfg["base"]:
			self.canv=ROOT.TCanvas("canv","canv",800,800)
		else:
			self.canv=ROOT.TCanvas("canv","canv",
					int(self.self.cfg["base"]["canv"].split(',')[0]),
					int(self.self.cfg["base"]["canv"].split(',')[1]),
					)
		if BoolKey("base","ratio",True):
			self.pad1=ROOT.TPad("p1","p1",0,self.ratiofraction,1,1)
			self.pad2=ROOT.TPad("p2","p2",0,0,1,self.ratiofraction)
			self.pad1.Draw()
			self.pad2.Draw()
		else:
			self.pad1=self.canv
			self.pad2=None
		self.pad1.cd()
		## Draw AXIS from the first
		base = self.cfg["base"]["drawList"].split(',')[0]	
		if self.cfg[base]["type"].lower() == "th1d":
			xmin = self.collection.Get(base).GetBinLowEdge(1)
			n= self.collection.Get(base).GetNbinsX()
			xmax = self.collection.Get(base).GetBinLowEdge(n+1)
			ymin = self.collection.Get(base).GetMinimum()
			ymax = self.collection.Get(base).GetMaximum()
		if BoolKey("base","xRange",True):
			xmin=float( self.cfg["base"]["xRange"].split(',')[0]  )
			xmax=float( self.cfg["base"]["xRange"].split(',')[1]  )
		if BoolKey("base","yRange",True):
			ymin=float( self.cfg["base"]["yRange"].split(',')[0]  )
			ymax=float( self.cfg["base"]["yRange"].split(',')[1]  )

		axisHist= ROOT.TH2D("axis","axis",100,xmin,xmax,100,ymin,ymax)
		axisHist.Draw("AXIS")
		axisHist.Draw("AXIS X+Y+ SAME")
		self.axisHist=axisHist
		if BoolKey("base","xLog"): self.pad1.SetLogx()
		if BoolKey("base","yLog"): self.pad1.SetLogy()
		return self

	def RedrawAxis(self):
		self.pad1.cd()
		axisHist.Draw("AXIS SAME")
		axisHist.Draw("AXIS X+ Y+ SAME")
		return self

	def MakeRatio(self):
		ratioBaseName=self.cfg["base"]["ratio"]
		if ratioBaseName not in self.cfg: 
			print >>sys.stderr,"Ratio Base name referred to a non configured histo",ratioBaseName
			raise NameError
		b=self.collection.Get(ratioBaseName).Clone(ratioBaseName + "_ratiobase")
		## TODO:
		## reset errors
		## clone the collection in collratio
		## perform the division
		return self

	def DrawRatio(self):
		self.pad2.cd()
		return self

	def Draw(self):
		Style().DrawCanvas().DrawObjects().DrawLegend().DrawCMS().RedrawAxis()
		if BoolKey("base","ratio",True):
			MakeRatio().DrawRatio()
		return self

	def Save(self):
		for ext in self.cfg["base"]["format"].split(','):
			self.canv.SaveAs( self.cfg["base"]["output"] + "."+ext)
		return self

	def Style(self):
		''' Set Style TDR'''
		ROOT.gStyle.SetOptTitle(0)
		ROOT.gStyle.SetPadTopMargin(0.05)
		ROOT.gStyle.SetPadBottomMargin(0.13)
		ROOT.gStyle.SetPadLeftMargin(0.16)
		ROOT.gStyle.SetPadRightMargin(0.02)
		ROOT.gStyle.SetOptFile(0);
		ROOT.gStyle.SetOptStat(0); 
		ROOT.gStyle.SetOptDate(0);
		ROOT.gStyle.SetOptFit(1);
		ROOT.gStyle.SetFitFormat("5.4g");
		ROOT.gStyle.SetFuncColor(2);
		ROOT.gStyle.SetFuncStyle(1);
		ROOT.gStyle.SetFuncWidth(1);
		ROOT.gStyle.SetHistLineColor(1);
		ROOT.gStyle.SetHistLineStyle(0);
		ROOT.gStyle.SetHistLineWidth(1);
		ROOT.gStyle.SetFrameBorderMode(0);
		ROOT.gStyle.SetFrameBorderSize(1);
		ROOT.gStyle.SetFrameFillColor(0);
		ROOT.gStyle.SetFrameFillStyle(0);
		ROOT.gStyle.SetFrameLineColor(1);
		ROOT.gStyle.SetFrameLineStyle(1);
		ROOT.gStyle.SetFrameLineWidth(1);
		ROOT.gStyle.SetPadBorderMode(0);
		#ROOSetPadBorderSize(Width_t size = 1);
		ROOT.gStyle.SetPadColor(kWhite);
		ROOT.gStyle.SetPadGridX(false);
		ROOT.gStyle.SetPadGridY(false);
		ROOT.gStyle.SetGridColor(0);
		ROOT.gStyle.SetGridStyle(3);
		ROOT.gStyle.SetGridWidth(1);
		ROOT.gStyle.SetCanvasBorderMode(0);
		ROOT.gStyle.SetCanvasColor(kWhite);
		ROOT.gStyle.SetCanvasDefH(600); 
		ROOT.gStyle.SetCanvasDefW(600); #Width of canvas
		ROOT.gStyle.SetCanvasDefX(0);   #Position on screen
		ROOT.gStyle.SetCanvasDefY(0);
		return self
#### END ####

