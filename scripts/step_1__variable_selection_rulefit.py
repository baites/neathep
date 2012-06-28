#! /usr/bin/env python
# RuleFitInterface 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Creates the necesary operation for running
#   rulefit for variable selection in neat

import sys

# Enabling root in batch mode
sys.argv.append('-b')

import commands, shutil

from Processor import *
from TopovarReader import *
from Util import *

import RuleFitTraining

## Class the implements the interface
class RuleFitInterface(Processor):


  ## Constructor
  def __init__(self):
    # Call the constructor from parent class
    super(RuleFitInterface,self).__init__()
    # Initializing allowed processor parameters
    self.defineParameter('input', 'Provides the input directory for running rulefit (defaul: undefined).')
    self.defineParameter('output', 'Provides the output directory for running rulefit.')
    self.defineParameter('topovars', 'Provide the location of the topovars to be processed using rulefit. (default: undefined)')
    self.defineParameter('interface', 'Set the interface from root to txt files (default: true).')
    self.defineParameter('training', 'Set the rulefit training (default: true).')
    self.defineParameter('maxnum', 'Maximum number of selected events (default: undefined).')
    self.defineParameter('minimp', 'Mininmum importance for selecting variables (default: undefined).')
    

  ## Implementation of rulefit interface
  def interface(self, set, indir, outdir):
    # Copy indirvar file
    vfilename = '%s/%s' % (outdir, Common.Inputvars)
    if indir:
      shutil.copyfile('%s/%s' % (indir, Common.Selectvars), vfilename)
    else:
      # Creating output directory
      topovars = '%s/scratch/%s/%s.txt' % (
        Common.NeatDirectory, self.getParameter('topovars'), channelName(set)
      )
      shutil.copyfile(topovars, vfilename)

    # Reading variable list
    variables = open(vfilename).readlines()
    variables = [variable.rstrip() for variable in variables]

    # Reading signal topovars
    signal = TopovarReader(variables)
    self.message('Reading signal files')

    # Adding signal files
    for sample in Common.TrainingSignals:
      signal.add('%s/%s/%s_zero_Topo_%s.root' % (
          Common.SampleLocation, Common.TrainingSample, channelName(set, sample), Common.TrainingSample
        )
      )
    # Create and save a random sampling
    signal.saveRandomSampling('%s/signals.txt' % outdir, Common.RuleFitTrainingEvents)

    # Reading background topovars
    background = TopovarReader(variables)

    self.message('Reading background files')

    # Adding background files
    for sample in Common.TrainingBackgrounds:
      background.add('%s/%s/%s_zero_Topo_%s.root' % (
          Common.SampleLocation, Common.TrainingSample, channelName(set, sample), Common.TrainingSample
        )
      )

    # Create and save a random sampling
    background.saveRandomSampling('%s/backgrounds.txt' % outdir, Common.RuleFitTrainingEvents) 


  ## Rulefit training
  def training(self, set, outdir):
    self.message('Running TMVAnalysis for %s' % channelName(set))
    status, stdout = commands.getstatusoutput(
      '%s/support/python/RuleFitTraining.py --outdir=%s >& %s/tmva.log' % (
        Common.NeatDirectory, outdir, outdir
      )
    )
    if status != 0:
      raise ProcessorError('TMVAnalysis return with error(s).')


  ## Variable selection
  def selection(self, outdir):
    # Read tmva output 
    table = ReadRuleFitImportance('%s/tmva.log' % outdir)
    # Save the names of the selected variables
    index = 0
    file = open('%s/%s' % (outdir, Common.Selectvars), 'w')
    for variable, importance in table:
      index = index + 1
      if self.isParameter('maxnum'):
        if index > int(self.getParameter('maxnum')):
          break
      if self.isParameter('minimp'):
        if importance < float(self.getParameter('minimp')):
          break
      file.write('%s\n' % variable)
    file.close()


  ## Process each channel
  def process(self, set):

    channel = channelName(set)    
    self.message('Processing channel %s' % channel)

    # Setting the indir directory
    indir = None
    if self.isParameter('input'):
      indir = '%s/scratch/%s/%s' % (
        Common.NeatDirectory, self.getParameter('input'), channel
      )

    # Creating output directory
    outdir = '%s/scratch/%s/%s' % (
      Common.NeatDirectory, self.getParameter('output'), channel
    )

    # Check for output directory
    if not os.path.exists(outdir):
      if self.getParameter('interface','true') == 'true':
        os.makedirs(outdir)
      else:
        raise ProcessorError('Missing working directory %s' % outdir)
   
    # Run rulefit interface
    if self.getParameter('interface','true') == 'true':
      self.interface(set, indir, outdir)

    # Run rulefit training
    if self.getParameter('training','true') == 'true':
      self.training(set, outdir)      

    # Run rulefit selection
    self.selection(outdir)

    
# Execute the interface
RuleFitInterface().loop()
