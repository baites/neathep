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

Data = 'Run2011'
Channels = ['electron','muon','emu']

Luminosity = {
  'emu':'5.0',
  'electron':'5.0',
  'muon':'5.0'
}

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
'emu':'e#mu-channel',
'electron':'e-channel',
'muon':'#mu-channel'
}

# Sample configuraton

TrainingSignals = ['Zprime_M750GeV_W7500MeV']
TrainingBackgrounds = ['bkg']

YieldSignals = ['Zprime_M750GeV_W7500MeV']
YieldBackgrounds = ['TTJets', 'DY', 'VV', 'WJets', 'singleTop', 'QCD']

MergeSignals = False

ColorCodes = {
Data: ROOT.kBlack,
'Signal': ROOT.kBlue, 'Background': ROOT.kRed,
'Zprime_M750GeV_W7500MeV': ROOT.kWhite,
'TTJets': ROOT.kRed, 'DY': ROOT.kBlue,
'VV': ROOT.kGray, 'WJets' : ROOT.kGreen,
'singleTop': ROOT.kViolet, 'QCD': ROOT.kYellow-7
}

# Systematic configuration

Systematics = ['JES_plus', 'JES_minus', 'PU_plus', 'PU_minus']
NoSystematics = [Data, 'QCD']

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

## Funtion for formated file name

def filename(set, sample='', systematic=''):
  name = ''

  if not 'Zprime' in sample:
    name = 'c_'

  if 'channel' in set:
    name = name + set['channel']

  if systematic != '':
    name = name + '_%s' % systematic 

  if sample != '':
    name = name + '_%s' % sample

  name = name + '-Ntuple_histograms'

  return name

## Please do not modufy what follows

# Getting NEATSYS
import os
NeatDirectory = os.environ['NEATSYS']

