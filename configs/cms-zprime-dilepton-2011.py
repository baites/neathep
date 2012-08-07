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

RecoVersions = 'Run2011'
Leptons = ['EMU']
Ntags = ['EqOneTag']
Njets = ['EqTwoJet']

Luminosity = {'Run2011':'5.0'}

# Topovar back list
TopovarBlackList = [
  # Related event weight
  'scale','w_','weight', 'EventWeight',
  # Related to MC trueh
  'Parton','Flavor','index','Is',
  # Related to channel information
  'Analysis', 'NGoodJets','NTaggedJets','LeptonCharge',
  # Related PV
  'NAllPrimaryVertex', 'PV',
  # Related event information
  'EventNumber','RunNumber','RunPeriod',
  # Relate to discrit or bool variables
  'Has','OP','Fired','Charge','Taggability',
  # Lepton information
  'LeptonChis', 'LeptonDCA', 'LeptonDetEta',
  # Misc.
  'Lumi','KS','Hits','Track','Error',
]

# Combined channel histograms

CombinedNtags = 'TagsCombined'
CombinedNjets = 'JetsCombined'

# XCheck configurations

XCheckNtags.ttbar = ['EqOneTag','EqTwoTag']
XCheckNjets.ttbar = ['EqFourJet']
XCheckNtags.wjets = ['EqOneTag','EqTwoTag']
XCheckNjets.wjets = ['EqTwoJet']

CombinedXCheckNtags.ttbar = 'TagsCombined'
CombinedXCheckNtags.wjets = 'TagsCombined'

# Plot labels

Labels = {
'CC':'e+#mu-channel',
'EqOneTag':'1 b-tag', 'EqTwoTag':'2 b-tags', 'TagsCombined':'1-2 b-tags',
'EqTwoJet':'2 jets', 'EqThreeJet':'3 jets', 'EqFourJet':'4 jets', 'JetsCombined':'2-4 jets'
}

# Sample configuraton

TrainingSignals = ['tqb']
TrainingBackgrounds = ['QCD','ttbar-lepjets','ttbar-dilepton','diboson','zlp','zcc','zbb','wlp','wcc','wbb','tb']

YieldSignals = ['tqb']
YieldBackgrounds = ['QCD','ttbar-lepjets','ttbar-dilepton','diboson','zlp','zcc','zbb','wlp','wcc','wbb','tb']

ColorCodes = {
'wlp':ROOT.kGreen, 'wcc':ROOT.kGreen-3, 'wbb':ROOT.kGreen-2,
'zlp':ROOT.kYellow, 'zcc':ROOT.kYellow+1, 'zbb':ROOT.kYellow+2,
'diboson':ROOT.kOrange+1, 'QCD':ROOT.kRed-5,
'ttbar-dilepton':ROOT.kMagenta-4, 'ttbar-lepjets':ROOT.kRed,
'tb':ROOT.kCyan, 'tqb':ROOT.kBlue, 'DATA':ROOT.kBlack
}

# Systematic configuration

Systematics = [
  'JETIDplus', 'JETIDminus', 'JERplus', 'JERminus', 
  'JESplus', 'JESminus', 'VCplus', 'VCminus',
  'ACplus', 'ACminus', 'BTagplus', 'BTagminus'
]

# Input variables and topovar files

Inputvars = 'inputvars.txt'
Selectvars = 'selectedvars.txt'
SampleLocation = '/prj_root/7007/top_write/jyoti/SingleTop2011.v9.ext/LooseTight/subsets'
TrainingSample = 'small_training_sample'
TestingSample = 'testing_sample'
YieldSample = 'yield_sample'

# Rulefit configuration

RuleFitTrainingEvents = 20000 

# Analysis dependent neat parameters

import FitnessFunctions
NeatNumberGenerations = 40 
NeatNumberTries = 10
NeatFitnessFunction = FitnessFunctions.EventEuclideanDistance()

# Discriminator information

Binning = ['25', '50', '100', '25maxit', '50maxit', '100maxit']
NeatOutputName = 'NEAT_output'

# Xsection measurement

XSectionRecoVersions = 'p17'
XSectionLeptons = 'CC'
XSectionNtags = Ntags + ['TagsCombined']
XSectionNjets = Njets + ['JetsCombined']
XSectionBinnings = '25maxit'
XSectionSystematics = ['nosys','flatMCstats','fullsys']
XSectionSignals = 'tqb'

## Please do not modufy what follows

# Getting NEATSYS
import os
NeatDirectory = os.environ['NEATSYS']

