import Plotter
## configuration
from optparse import OptionParser, OptionGroup

# configparser in python3
from ConfigParser import RawConfigParser

if __name__=="__main__":
	usage=''' 
		%prog
		use to plot TH1D, TGraph, TH2D ...
		in CMSSW Style
		'''
	_parser=OptionParser(usage=usage)
	_parser.add_option()
	
	(opts,args)=parser.parse_args()
	
	## read configuration
	_cfg = RawConfigParser()
	_cfg.read('config.txt')
	cfg = dict()
	for sect in _cfg.sections():
		cfg[sect] = dict()
		for (name, value) in _cfg.items(sect):
			cfg[sect][name] = value

if __name__=="__main__":
	p=Plotter(cfg)
	p.Draw().Save()
