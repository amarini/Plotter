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
parser.add_option("-e","--extrasub", dest="extrasub", help="Extra substitutions. {'dir':'plotall'} [%default]", default='{}')

(opts,args)=parser.parse_args()

exec("extrasub="+opts.extrasub) ## useful for 

if opts.verbose:
	print "---- EXTRA ----"
	print extrasub
	print "---------------"


# configparser in python3
from ConfigParser import RawConfigParser

def GetSubdict(cfg):
	subdict={}
	if 'substitute' in cfg:
		for key in cfg['substitute']:
			subdict[key]=cfg['substitute'][key]
	for key in extrasub:
		subdict[key]=extrasub[key]
	return subdict

def Substitute(cfg):
	''' Final Substitution of all the keys'''
	if 'substitute' in cfg:
		subdict=GetSubdict(cfg)
		del cfg["substitute"]
		## loop over the cfg and apply sub
		for sect in cfg:
			for name in cfg[sect]:
				value=cfg[sect][name]%subdict
				cfg[sect][name]=value
	return 

## read configuration
if opts.verbose:  print "-> Reading configuration from:", opts.dat
_cfg = RawConfigParser()
_cfg.read(opts.dat)
cfg = {}
for sect in _cfg.sections():
	cfg[sect] = {}
	for (name, value) in _cfg.items(sect):
		if value == '' : cfg[sect][name]=''
		else: cfg[sect][name] = value.split('#')[0].split()[0]
del _cfg

while "include" in cfg:
	sub = []
	file = cfg["include"]["file"]
	if "sub" in cfg["include"]: 
	   for s in cfg["include"]["sub"].split(','):
		   sub.append( (s.split(':')[0],s.split(':')[1]  )  )

	subdict=GetSubdict(cfg)
	cfg['include']['file'] = cfg['include']['file']%subdict
	print "-> Reading file",cfg["include"]["file"]
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
				#print "section",sect,"name",name,"value=",value
				cfg[sect][name] = value.split('#')[0].split()[0]
	del _cfg	

#### STANDARD SET OF substitutions
Substitute(cfg)

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
