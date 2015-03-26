## configuration
from optparse import OptionParser, OptionGroup
usage=''' 
	%prog
	use to plot TH1D, TGraph, TH2D ...
	in CMSSW Style.
       '''

parser=OptionParser(usage=usage)
parser.add_option("-d","--dat", dest="dat", help="configuration file %default.", type="string", default="config.txt")

(opts,args)=parser.parse_args()

# configparser in python3
from ConfigParser import RawConfigParser

## read configuration
_cfg = RawConfigParser()
_cfg.read('config.txt')
cfg = dict()
for sect in _cfg.sections():
	cfg[sect] = dict()
	for (name, value) in _cfg.items(sect):
		cfg[sect][name] = value

print "--- Loading Plotter ---" 
import Plotter
p=Plotter.Plotter(cfg)
p.Draw().Save()
print "--- DONE ---"
