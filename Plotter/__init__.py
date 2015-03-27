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

class BaseDraw(object): # object "newclass type", make super and co behave differently. This are type and objects
	''' Base Class for Objects that can be drawn'''
	def __init__(self):
		self.types={"TH1D":1,"TGraph":2,"TH2D":3}
		self.styles={"line":1,"marker":2,"band":4}
		self.style = self.styles["line"]
		self.styleopt = 21
		self.color = ROOT.kBlack
		self.width = 1
		self.obj = None
		self.drawerrors=False
		self.legendobj=None
		pass 

	def __del__(self):
		pass

	def Draw(self):
		return self

	def SetMarker(self):
		self.style=self.styles["marker"]
		return self

	def SetLine(self):
		self.style=self.styles["line"]
		return self

	def SetBand(self):
		self.style=self.styles["band"]
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
		self.drawerrors= other.drawerrors
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
			yield self.objs[x]
	def __next__(): #in python3
	#def next(self):
		if self.cur < len(self) :
			self.cur +=1 
			#print "NEXT-DEBUG: RETURNING",self.objs[ self.names[ self.cur - 1  ] ]
			return self.objs[ self.names[ self.cur - 1  ] ]
		else: 
			raise StopIteration
		pass
	def Add(self, name, obj):
		''' Add obj with name = name to the list '''
		self.objs[name]=obj
		self.names.append(name)
		return self
	def Remove(self, name):
		del self.objs[name]
		self.names[:] = [x for x in self.names and x != name ]
		return self
	def Get(self, name):
		return self.objs[name]

	def GetName(self, x):
		for n in self.names:
			if self.objs[n]==x: return n
		return "Not Found"

class Graph(BaseDraw):
	''' Implement a Graph object '''
	def __init__(self):
		super(Graph, self).__init__()
		self.graph=self.obj
		self.graph=None
		self.graphRange=None

	def __del__(self):
		if self.graph != None:
			self.graph.Delete()
			self.graph=None
	
	def Empty(self, name):
		''' Init empty TGraph with name = name'''
		self.graph=ROOT.TGraphAsymmErrors()
		self.graph.SetName(name)
		self.obj=self.graph
		return self

	def AddPoint(self, x, y, dx=0, dy=0):
		'''Add a point with symmetric errors '''
		n=self.graph.GetN()
		self.graph.SetPoint(n, x,y)
		self.graph.SetPointError(n, dx, dx, dy, dy)
		return self

	def AddPointAsymmErrors(self, x, y, exl, exh, eyl, eyh):
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
		self.graphRange=ROOT.TGraphAsymmErrors() 
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
		if self.style == self.styles["marker"]:
			self.graph.SetMarkerStyle(self.styleopt)
			self.graph.SetLineColor(self.color)
			self.graph.SetMarkerColor(self.color)
			self.graph.SetLineWidth(self.width)
			opt="P SAME"
			if self.drawerrors:
				opt="PE SAME"
			self.graph.Draw(opt)
			self.legendobj= self.graph
			if self.graphRange != None:
				self.graphRange.SetMarkerStyle(0)
				self.graphRange.SetMarkerSize(0)
				self.graphRange.SetLineColor(self.color)
				self.graphRange.SetMarkerColor(self.color)
				self.graphRange.SetLineWidth(self.width)
				self.graphRange.Draw(opt)

		if self.style == self.styles["band"]:
			self.graph.SetFillStyle(self.styleopt)
			self.graph.SetLineColor(self.color)
			self.graph.SetFillColor(self.color)
			self.graph.SetLineWidth(self.width)
			self.graph.Draw("E2 SAME")
			self.legendobj=self.graph
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
		#fill for line
		self.fillcolor = 0
		self.fillstyle = 0

	def CopyStyle(self, other):
		super(Histo, self).CopyStyle(other)
		# check if called from BaseDraw
		if isinstance(other,Histo):
			self.shift=other.shift
			self.length=other.length
			self.fillcolor=other.fillcolor
			self.fillstyle=other.fillstyle
			self.xerror=other.xerror
			self.yerror=other.yerror
		return self

	def ConvertToGraph(self):
		''' Convert the current histogram to a Graph'''
		if self.hist == None: self.hist=self.obj

		g=Graph()
		g.Empty(self.hist.GetName()+"_graph")
		g.CopyStyle(self)
		for i in range(1, self.hist.GetNbinsX()+1):
			ex=0
			if self.xerror:
				#print "DEBUG: setting Histo ex to bin width for h",self.hist.GetName()
				ex=self.hist.GetBinWidth(i)/2.

			x = self.hist.GetBinCenter(i)
			y = self.hist.GetBinContent(i)
			ey = self.hist.GetBinError(i) 

			if not self.drawerrors : 
				ex=0
				ey=0

			#apply shift and length for bands
			if self.shift>0: x+= self.shift
			if self.shift>0 and self.length>0: ex=self.length

			g.AddPoint(  x, y, ex, ey ) 
		return g

	def Draw(self):
		'''Draw'''
		if self.xerror or self.yerror: self.drawerrors=True # update info

		if self.hist == None: self.hist=self.obj  #update ref
		##
		if self.style==self.styles["marker"] or \
			self.style==self.styles["band"]:
			# transform it to a Graph
			self.mygraph=self.ConvertToGraph()
			self.mygraph.Draw()
			self.legendobj=self.mygraph.obj

		elif self.style == self.styles["line"]:
			self.hist.SetLineColor(self.color)
			self.hist.SetLineWidth(self.width)
			if self.fillstyle>0:
				self.hist.SetFillStyle(self.fillstyle)
				self.hist.SetFillColor(self.fillcolor)
			#print "Setting line style for Histo",self.hist.GetName(),"to",self.styleopt
			self.hist.SetLineStyle(self.styleopt)
			self.hist.Draw("HIST SAME")
			self.legendobj=self.hist

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
		self.garbage=[] ## it's not garbag
		## sanity checks
		if "base" not in cfg: raise TypeError
		if "drawlist" not in cfg["base"]: 
			print>>sys.stderr, "--> You should indicate what you want to draw in drawList"
			raise TypeError

		if "legend" not in cfg: 
			self.cfg["legend"] ={}
			self.cfg["legend"]["draw"]="False"
		if "ratio" not in cfg:
			self.cfg["ratio"]={}
			self.cfg["ratio"]["draw"]="False"

		for name in cfg["base"]["drawlist"].split(','):
			if self.verbose >0: print "-> Adding Object '"+name+"' to the list to be drawn"
			if name not in cfg: 
				print>>sys.stderr, "Object '"+name+"' in drawList but not configured" 
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
			obj=Histo()
			obj.obj = h
			obj.fillstyle=self.ColorKey(name,"fillstyle")
			obj.fillcolor=self.ColorKey(name,"fillcolor")

		if self.cfg[name]["type"].lower() == "tgraph":
			obj=Graph()
			obj.obj = h
		if self.BoolKey(name,"xerror") or self.BoolKey(name,"yerror"):
			obj.drawerrors=True
		if self.BoolKey(name,"xerror"): 
			obj.xerror=True
		if self.BoolKey(name,"yerror"):
			obj.yerror=True

		if "style" in self.cfg[name]:obj.SetStyle(self.cfg[name]["style"])
		# 
		color = self.ColorKey(name,"color")
		if color>=0: obj.color=color
		#
		styleopt = self.ColorKey(name,"styleopt")
		if styleopt >=0 : obj.styleopt=styleopt
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
		latex.SetTextSize(0.04)
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
			latex.SetTextAlign(13)
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
			latex.SetTextAlign(31)
			x=1-self.canv.GetRightMargin()- 0.02
			y=self.canv.GetBottomMargin() +0.02

		latex.DrawLatex(x,y,mytext)

		#lumi always tr
		x=1-self.canv.GetRightMargin()- 0.01
		y=1-self.canv.GetTopMargin() +0.01
		latex.SetTextSize(0.03)
		latex.SetTextAlign(31)
		if "lumi" not in self.cfg["text"]: self.cfg["text"]["lumi"]="19.7 fb^{-1} (8TeV)"
		self.cfg["text"]["lumi"] = self.ParseStr( self.cfg["text"]["lumi"]  )
		latex.DrawLatex(x,y,self.cfg["text"]["lumi"])

		if "extra" in self.cfg["text"]:
			latex.SetTextAlign(11)
			latex.SetTextSize(0.03)
			x=float(self.cfg["text"]["extra"].split('!')[0] )
			y=float(self.cfg["text"]["extra"].split('!')[1] )
			mytext=self.cfg["text"]["extra"].split('!')[2]
			mytext = self.ParseStr(mytext)
			latex.DrawLatex(x,y,mytext)

		return self

	def DrawLogo(self):
		''' Draw a logo on Top of the plot'''
		if "logo" not in self.cfg: return self
		if "draw" not in self.cfg["logo"]: return self
		if not self.BoolKey("logo","draw") : return self
		if "file" not in self.cfg["logo"]: 
			print >>sys.stderr, "You need to specify a file for the logo"
			raise NameError
		print "DEBUG LOGO: loading image",self.cfg["logo"]["file"]

		i=ROOT.TASImage(self.cfg["logo"]["file"])
		size=0.1
		if "size" in self.cfg["logo"]:
			size= float( self.cfg["logo"]["size"])
		xh=1-self.canv.GetRightMargin() -0.01 ## TODO use pad and Pad dimension to figure it out
		yh=1-self.canv.GetTopMargin() -0.01
		xl=xh-size
		yl=yh-size

		if "position" in self.cfg["logo"]:
			xl= float(  self.cfg["logo"]["position"].split(',')[0]   )
			yl= float(  self.cfg["logo"]["position"].split(',')[1]   )
			xh= float(  self.cfg["logo"]["position"].split(',')[2]   )
			yh= float(  self.cfg["logo"]["position"].split(',')[3]   )
		self.padlogo=ROOT.TPad("padlogo","logo",xl,yl,xh,yh)
		self.padlogo.Draw()
		self.padlogo.cd()
		i.Draw()
		self.garbage.append(i)
		self.pad1.cd()

		return self

	def ParseStr(self, string):
		''' Standard reparsing in the configfile for displayed text'''
		r=re.sub('~',' ',string)
		r=re.sub('@','#',r)
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
		colortext=self.cfg[section][field]
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
		''' Draw legend'''
		if not self.BoolKey("legend","draw"): 
			if self.verbose>0: print "Not drawing Legend: config ",config["legend"]["draw"]
			return self

		xl=0.6
		yl=0.6
		xh=0.9
		yh=0.9

		if "position" in self.cfg["legend"]:
			xl = float ( self.cfg["legend"]["position"].split(',')[0] )
			yl = float ( self.cfg["legend"]["position"].split(',')[1] )
			xh = float ( self.cfg["legend"]["position"].split(',')[2] )
			yh = float ( self.cfg["legend"]["position"].split(',')[3] )

		if self.verbose >0:
			print "Legend position is", xl,yl,xh,yh

		l=ROOT.TLegend(xl,yl,xh,yh)
		l.SetFillStyle(0)
		l.SetBorderSize(0)
		if "header" in self.cfg["legend"]:
			mytext= self.ParseStr(self.cfg["legend"]["header"])
			e=l.SetHeader(mytext)
			l.SetTextFont(43)
			l.SetTextSize(self.entrysize)
		if "legendlist" not in self.cfg["legend"]: self.cfg["legend"]["legendlist"]=""

		for name in self.cfg["legend"]["legendlist"].split(','):
			if name =='' : continue
			if self.verbose >0 : print "-> adding '"+name+"' to the legend"
			if "label" in self.cfg[name] : mylabel=self.cfg[name]["label"]
			else: mylabel = name

			mylabel=self.ParseStr(mylabel)

			if self.cfg[name]["style"].lower() == "marker": 
				mytype = "P"
				if self.BoolKey(name,"xerror"):
					mytype += "L"
				if self.BoolKey(name,"yerror"):
					mytype += "E"
			if self.cfg[name]["style"].lower() == "line": 
				mytype = "L"
			if self.cfg[name]["style"].lower() == "band": 
				mytype = "F"
			#if self.verbose>0:
			#print "DEBUG Entry:", self.collection.Get(name).legendobj.GetName(),"label=",mylabel,"opts",mytype
			e=l.AddEntry(self.collection.Get(name).legendobj, mylabel, mytype)
			e.SetTextFont(43)
			e.SetTextSize(self.entrysize)
			e.SetTextAlign(12)
		l.Draw("SAME")
		#l.Print("V") ## DEBUG
		self.garbage.append(l) # not sure it is useful

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
					int(self.cfg["base"]["canv"].split(',')[0]),
					int(self.cfg["base"]["canv"].split(',')[1]),
					)
		if self.BoolKey("ratio","draw"):
			if "fraction" in self.cfg["ratio"]: self.ratiofraction= float(self.cfg["ratio"]["fraction"] )
			self.pad1=ROOT.TPad("p1","p1",0,self.ratiofraction,1,1)
			self.pad2=ROOT.TPad("p2","p2",0,0,1,self.ratiofraction)
			self.pad1.SetBottomMargin(0) ## one on top of the other
			self.pad2.SetTopMargin(0)

			self.pad2.SetBottomMargin(0.3)
			self.pad1.SetTopMargin(0.05/(1.-self.ratiofraction))

			self.pad1.Draw()
			self.pad2.Draw()
		else:
			self.pad1=self.canv
			self.pad2=None
		self.pad1.cd()
		## Draw AXIS from the first
		base = self.cfg["base"]["drawlist"].split(',')[0]	
		if self.cfg[base]["type"].lower() == "th1d":
			xmin = self.collection.Get(base).obj.GetBinLowEdge(1)
			n= self.collection.Get(base).obj.GetNbinsX()
			xmax = self.collection.Get(base).obj.GetBinLowEdge(n+1)
			ymin = self.collection.Get(base).obj.GetMinimum()
			ymax = self.collection.Get(base).obj.GetMaximum()
		if self.BoolKey("base","xrange",True):
			xmin=float( self.cfg["base"]["xrange"].split(',')[0]  )
			xmax=float( self.cfg["base"]["xrange"].split(',')[1]  )
		if self.BoolKey("base","yrange",True):
			ymin=float( self.cfg["base"]["yrange"].split(',')[0]  )
			ymax=float( self.cfg["base"]["yrange"].split(',')[1]  )


		axisHist= ROOT.TH2D("axis","axis",100,xmin,xmax,100,ymin,ymax)
		axisHist.GetYaxis().SetRangeUser(ymin,ymax)
		axisHist.GetXaxis().SetRangeUser(xmin,xmax)

		## Set Title
		xtitle=""
		ytitle=""
		if "xtitle" in self.cfg["base"]: xtitle=self.ParseStr( self.cfg["base"]["xtitle"])
		if "ytitle" in self.cfg["base"]: ytitle=self.ParseStr( self.cfg["base"]["ytitle"])
		axisHist.GetXaxis().SetTitle(xtitle)
		axisHist.GetYaxis().SetTitle(ytitle)
		axisHist.GetXaxis().SetTitleOffset(1.2)
		axisHist.GetYaxis().SetTitleOffset(1.5)

		axisHist.GetXaxis().SetTitleFont(43) # in point, maybe configurable ?
		axisHist.GetXaxis().SetTitleSize(24)
		axisHist.GetXaxis().SetLabelFont(43)
		axisHist.GetXaxis().SetLabelSize(20)
		axisHist.GetYaxis().SetTitleFont(43) # in point
		axisHist.GetYaxis().SetTitleSize(24)
		axisHist.GetYaxis().SetLabelFont(43)
		axisHist.GetYaxis().SetLabelSize(20)

		##
		axisHist.Draw("AXIS")
		axisHist.Draw("AXIS X+Y+ SAME")
		self.axisHist=axisHist
		if self.BoolKey("base","xlog"): self.pad1.SetLogx()
		if self.BoolKey("base","ylog"): self.pad1.SetLogy()
		return self

	def RedrawAxis(self):
		self.pad1.cd()
		self.axisHist.Draw("AXIS SAME")
		self.axisHist.Draw("AXIS X+ Y+ SAME")
		return self

	def MakeRatio(self):
		ratioBaseName=self.cfg["ratio"]["base"]
		if ratioBaseName not in self.cfg: 
			print >>sys.stderr,"Ratio Base name referred to a non configured histo",ratioBaseName
			raise NameError
		self.ratiobase=self.collection.Get(ratioBaseName).obj.Clone(ratioBaseName + "_ratiobase")
		if not isinstance(self.collection.Get(ratioBaseName),Histo):
			print >>sys.stderr, "Ratio non implemented for base different from histo (TH1)"
			raise TypeError
		## TODO:
		## reset errors
		## ASSUMPTION: base is a TH1
		for i in range(1,self.ratiobase.GetNbinsX()+1): self.ratiobase.SetBinError(i,0)
		## clone the collection in collratio
		self.collectionratio=Collection()
		## and perform the division
		for o in self.collection:
			if isinstance(o,Graph):
				t = Graph()
				t.Empty(o.obj.GetName() + "_ratio")
				for i in range(0,o.obj.GetN()):
					x = t.graph.GetX()[i]
					y = t.graph.GetY()[i]
					exl = t.graph.GetEXlow()[i]
					exh = t.graph.GetEXhigh()[i]
					eyl = t.graph.GetEYlow()[i]
					eyh = t.graph.GetEYhigh()[i]
					if ( x< self.ratiobase.GetBinLowEdge(i) or x > self.ratiobase.GetBinLowEdge(i+1) ):
							print >>sys.stderr, "Warning: Possible mistake in bin range conversion from histo to graph"
					val = self.ratiobase.GetBinContent(i)
					y /=  val
					eyl /= val
					eyh /= val
					t.AddPointAsymmErrors( x, y, exl, exh, eyl, eyh)
				name = self.collection.GetName(o)
				t.CopyStyle(o)
				self.collectionratio.Add(name,t)
			elif isinstance(o,Histo):
				t = Histo()
				t.obj = o.obj.Clone(o.obj.GetName() + "_ratio")
				## assume same binning
				t.obj.Divide(self.ratiobase)
				t.CopyStyle(o)
				name = self.collection.GetName(o)
				self.collectionratio.Add(name,t)
			
			else: 
				print >>sys.stderr,"class not implemented in ratio"
		return self

	def DrawRatio(self):
		self.pad2.cd()
		xmin = self.axisHist.GetXaxis().GetXmin()
		xmax = self.axisHist.GetXaxis().GetXmax()
		ymin = 0.5
		ymax = 1.5

		if self.BoolKey("ratio","yrange",True):
			ymin=float( self.cfg["ratio"]["yrange"].split(',')[0]  )
			ymax=float( self.cfg["ratio"]["yrange"].split(',')[1]  )

		self.ratioaxisHist = ROOT.TH2D("axisR","axisR",100,xmin,xmax,100,ymin,ymax)
		for axis in ["GetXaxis()","GetYaxis()"]:
			for tocopy in ["Title","TitleOffset","TitleFont","TitleSize","LabelFont","LabelSize"]:
				exec("self.ratioaxisHist."+axis+".Set"+tocopy+"( self.axisHist."+axis+".Get" + tocopy +"()" +")")
		## adjust Title Offset
		offset = self.ratioaxisHist.GetXaxis().GetTitleOffset()
		self.ratioaxisHist.GetXaxis().SetTitleOffset( offset/self.ratiofraction * 0.7 ) # magic number
		length = self.axisHist.GetTickLength()
		self.ratioaxisHist.GetXaxis().SetTickLength( length / self.ratiofraction * 0.7)
		self.ratioaxisHist.GetYaxis().SetNdivisions(505)
		##
		if "ytitle" in self.cfg["ratio"]:
			self.ratioaxisHist.GetYaxis().SetTitle( self.ParseStr(self.cfg["ratio"]["ytitle"] ))
		
		self.ratioaxisHist.Draw("AXIS ")
		self.ratioaxisHist.Draw("AXIS X+Y+ SAME")
		for x in self.collectionratio:
			x.Draw()
		self.pad1.cd()
		return self

	def Draw(self):
		self.Style().DrawCanvas().DrawObjects().DrawLegend().DrawCMS().DrawLogo().RedrawAxis()
		if self.BoolKey("ratio","draw"):
			self.MakeRatio().DrawRatio()
		return self

	def Save(self):
		self.canv.Modified()
		self.canv.Update()
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
		ROOT.gStyle.SetPadColor(ROOT.kWhite);
		ROOT.gStyle.SetPadGridX(0);
		ROOT.gStyle.SetPadGridY(0);
		ROOT.gStyle.SetGridColor(0);
		ROOT.gStyle.SetGridStyle(3);
		ROOT.gStyle.SetGridWidth(1);
		ROOT.gStyle.SetCanvasBorderMode(0);
		ROOT.gStyle.SetCanvasColor(ROOT.kWhite);
		ROOT.gStyle.SetCanvasDefH(600); 
		ROOT.gStyle.SetCanvasDefW(600); #Width of canvas
		ROOT.gStyle.SetCanvasDefX(0);   #Position on screen
		ROOT.gStyle.SetCanvasDefY(0);
		return self
#### END ####

