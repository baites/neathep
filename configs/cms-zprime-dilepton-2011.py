# Common.py 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#
# Descrition:
#   Common configuration throughtout the analysis

# Importing basic configuration
from Util import *

# Channel configuration

Runs = 'Run2011'
Channels = ['EMU']

Luminosity = {'Run2011':'5.0'}

# Topovar back list

TopovarBlackList = [
  # Related to cmssw and event weight
  'edm', 'reco', 'pat', 'Gen'
]

# Combined channel histograms

# Plot labels

Labels = {
'EMU':'e#mu-channel'
}

# Sample configuraton

TrainingSignals = ['M750GeV_W7500MeV']
TrainingBackgrounds = ['Background']

YieldSignals = ['M750GeV_W7500MeV']
YieldBackgrounds = ['Background']

ColorCodes = {
'Signal': ROOT.kBlue, 'Background': ROOT.kRed
}

# Systematic configuration

Systematics = []

# Input variables and topovar files

Inputvars = 'inputvars.txt'
Selectvars = 'selectedvars.txt'
SampleLocation = '/Users/baites/Projects/neathep/CMSZprimeDilepton2011'
TrainingSample = 'training'
TestingSample = ''
YieldSample = 'yield'

# Rulefit configuration

RuleFitTrainingEvents = 20000 

# Analysis dependent neat parameters

import FitnessFunctions
NeatNumberGenerations = 40 
NeatNumberTries = 10
NeatFitnessFunction = FitnessFunctions.EventEuclideanDistance()

# Discriminator information

Binning = ['25', '50', '100']
NeatOutputName = 'neat'

## Please do not modufy what follows

# Getting NEATSYS
import os
NeatDirectory = os.environ['NEATSYS']

