#! /usr/bin/env python
# TMVARuleFit.py 
#
# Developers:
#   Victor Eduardo Bazterra 2012 (UIC)
#
# Descrition:
#   pyROOT implementation of TMVARuleFit

import sys

# Enabling root in batch mode
sys.argv.append('-b')

from ROOT import TCut, TFile, TMVA

## Main fuction
def Evaluate(outdir):

  sys.stdout = open(outdir + '/tmva.log', 'w') 

  # Output file
  output = TFile(outdir + '/tmva.root', 'RECREATE')

  # Create instance of TMVA factory (see TMVA/macros/TMVAClassification.C for more factory options)
  # All TMVA output can be suppressed by removing the "!" (not) in 
  # front of the "Silent" argument in the option string
  factory = TMVA.Factory("TMVARuleFit", output, "!V:!Silent:Color" )

  # Set the variables use for the analysis
  input = open(outdir + '/inputvars.txt')
  for variable in input.readlines():
    factory.AddVariable(variable[:-1], 'F')

  # Set the weight directory
  TMVA.gConfig().GetIONames().fWeightFileDir = outdir + "/weights"

  # Limit the creation of correlation plots
  TMVA.gConfig().GetVariablePlotting().fMaxNumOfAllowedVariablesForScatterPlots = 20  

  # Set the input file with signal and background events
  factory.SetInputTrees(
    outdir + '/signals.txt',
    outdir + '/backgrounds.txt'
  )

  cutsig = TCut('')
  cutbkg = TCut('')
  
  factory.PrepareTrainingAndTestTree( cutsig, cutbkg, "SplitMode=Random:NormMode=NumEvents:!V" )   

  factory.BookMethod( TMVA.Types.kRuleFit, "RuleFit",
    "H:!V:RuleFitModule=RFTMVA:Model=ModRuleLinear:MinImp=0.00001:RuleMinDist=0.001:NTrees=20:fEventsMin=0.01:fEventsMax=0.5:GDTau=-1.:GDTauPrec=0.01:GDStep=0.01:GDNSteps=10000:GDErrScale=1.02" ) 

  # Train MVAs
  factory.TrainAllMethods()

  # Test MVAs
  factory.TestAllMethods()

  # Evaluate MVAs
  factory.EvaluateAllMethods()

  # Save the output.
  output.Close()

import sys
from optparse import OptionParser

# Declaration of main function
if __name__ == "__main__":

  usage = 'Usage: %s [options]' %sys.argv[0]
  parser = OptionParser(usage=usage)

  parser.add_option('-o', '--outdir', dest='outdir', help='Ouput directory were rulefit is executed.')
  parser.add_option("-b", action="store_false", dest="verbose", default=True, help="Run root in batch mode.")  

  (options, args) = parser.parse_args()

  print options.outdir

  Evaluate(options.outdir)

