## configuration
from optparse import OptionParser, OptionGroup
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
	if opts.verbose: print "SECTION", sect
	cfg[sect] = {}
	for (name, value) in _cfg.items(sect):
		if opts.verbose: print "* ",name," = ",value
		cfg[sect][name] = value

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
