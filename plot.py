## configuration
from optparse import OptionParser, OptionGroup
import re
usage=''' 
	%prog
	use to plot TH1D, TGraph, TH2D ...
	in CMSSW Style.
       '''

parser=OptionParser(usage=usage)
parser.add_option("-d","--dat", dest="dat", help="configuration file %default.", type="string", default="config.txt")
parser.add_option("-v","--verbose", dest="verbose",action='store_true', help="Verbose. %default.", default=False)

(opts,args)=parser.parse_args()

# configparser in python3
from ConfigParser import RawConfigParser

## read configuration
if opts.verbose:  print "-> Reading configuration from:", opts.dat
_cfg = RawConfigParser()
_cfg.read(opts.dat)
cfg = {}
for sect in _cfg.sections():
	cfg[sect] = {}
	for (name, value) in _cfg.items(sect):
		cfg[sect][name] = value.split('#')[0].split()[0]
del _cfg

while "include" in cfg:
	sub = []
	file = cfg["include"]["file"]
	if "sub" in cfg["include"]: 
	   for s in cfg["include"]["sub"].split(','):
		   sub.append( (s.split(':')[0],s.split(':')[1]  )  )
		
	_cfg = RawConfigParser()
	_cfg.read( cfg["include"]["file"] )
	# remove include key from dictionary
	del cfg["include"]
	# add info to the cfg
	for sect in _cfg.sections():
		if sect not in cfg: cfg[sect]= {}
		for (name,value) in _cfg.items(sect):
			#never overwrite
			if name not in cfg[sect]:
				for a,b in sub:
					value = re.sub(a,b,value)
				cfg[sect][name] = value.split('#')[0].split()[0]
	del _cfg	
#PRINT CFG
if opts.verbose:
	print "====================== CFG ===================="
	for sec in cfg:
		print "["+sec+"]"
		for name in cfg[sec]:
			print name + " = "+ cfg[sec][name]
		print
	print "==============================================="


if opts.verbose:
	if "verbose" in cfg["base"]: 
		vLevel = int( cfg["base"]["verbose"]) + 1
		cfg["base"]["verbose"] = str(vLevel)
	else: cfg["base"]["verbose"]="1"
	print "--> Current Verbosity level is ", cfg["base"]["verbose"]

print "--- Loading Plotter ---" 
import Plotter
p=Plotter.Plotter(cfg)
p.Draw().Save()
print "--- DONE ---"
