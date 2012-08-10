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

Data = 'Run2011-'
Prefixes = 'c'
Channels = ['_emu_']
Postfixes = 'Ntuple_histograms'

Luminosity = {'c':'5.0'}

# Topovar back list

TopovarBlackList = [
  # Related to cmssw and event weight
  'edm', 'reco', 'pat', 'Gen', 'Pileup',
  # Counting variables
  'NPV', 'Nmuons', 'Nelectrons', 'Njets', 'Nbtags',
  # Event weight
  'eventWeight'
]

# Combined channel histograms

# Plot labels for each channel

Labels = {
'_emu_':'e#mu-channel'
}

# Sample configuraton

TrainingSignals = ['Zprime_M750GeV_W7500MeV-']
TrainingBackgrounds = ['bkg-']

YieldSignals = ['Zprime_M750GeV_W7500MeV']
YieldBackgrounds = ['bkg']

ColorCodes = {
'Signal': ROOT.kBlue, 'Background': ROOT.kRed
}

# Systematic configuration

Systematics = []

# Input variables and topovar files

Inputtree = 'Events'
EventWeight = 'eventWeight'
Inputvars = 'inputvars.txt'
Selectvars = 'selectedvars.txt'
SampleLocation = '/uscms/home/baites/nobackup/neathep/test'
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

