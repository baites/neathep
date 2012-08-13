#! /usr/bin/env python 
# TreeProducer 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Produce trees with neat output


import sys

# Enabling root in batch mode
sys.argv.append('-b')

import cPickle as pickle

from neat.nn import nn_cpp as nn

from Common import *
from Processor import *
from TopovarReader import *
from TopovarWriter import *
from Util import *
from VariableNormalizer import *

import Neat


class TreeProducer(Processor):

  ## Constructor
  def __init__(self):    
    # Processor constructor
    super(TreeProducer, self).__init__()
    # Initializing allowed processor parameters
    self.defineParameter('input','Provides the input directory with neat winner.')
    self.defineParameter('xcheck','Name for creating xcheck sample trees.')
    self.defineParameter('sample','Sample use to produce the trees (default=yield).')

  # Redefining start
  def start(self):
    # Redefinition of the channels
    if self.isParameter('xcheck'):
      # Redefining tag channels
      Common.Ntags = getattr(Common.XCheckNtags, self.getParameter('xcheck'))
      Common.Njets = getattr(Common.XCheckNjets, self.getParameter('xcheck'))
      Common.Systematics = []
    elif self.getParameter('sample','yield') != 'yield':
      # Look for systematics only for yield sample
      Common.Systematics = []
    # Running processor start
    super(TreeProducer, self).start()
    
          
  # Process each channel
  def process(self, set):

    self.message('Processing channel %s' % set['channel'])

    # Setting the indir directory
    indir = '%s/scratch/%s/Trainings/%s' % (
      Common.NeatDirectory, self.getParameter('input'), set['channel']
    )

    # Setting channel dir
    chdir = '%s/Trainings/%s' % (
      self.getParameter('input'), set['channel']
    )
     
    # Setting the outdir directory
    sampletype = self.getParameter('sample','yield')
    outdir = '%s/scratch/%s/YieldTrees' % (
      Common.NeatDirectory, self.getParameter('input')
    )
    sampletype = self.getParameter('sample','yield')
    if sampletype == 'training':
      outdir = '%s/scratch/%s/TrainingTrees' % (
        Common.NeatDirectory, self.getParameter('input')
      )
    elif sampletype == 'testing':
      outdir = '%s/scratch/%s/TestingTrees' % (
        Common.NeatDirectory, self.getParameter('input')
      )
    elif sampletype != 'yield':
      raise ProcessorError('Unknown sample option %s (allowed options: training, testing and yield).' % sampletype)      

    # Setting 
    if self.isParameter('xcheck'):
      outdir = '%s/scratch/%s/XCheckTrees/%s' % (
        Common.NeatDirectory, self.getParameter('input'), self.getParameter('xcheck')
      )
      
    # Check for output directory
    if not os.path.exists(outdir):
      os.makedirs(outdir)
   
    # Loop over all the samples producing the trees
    for systematic in Common.Systematics + ['']:
      for sample in Common.YieldBackgrounds + Common.YieldSignals + [Common.Data]:

        # No systematics for QCD and DATA
        if (sample in Common.NoSystematics) and systematic != '': continue

        self.message('Processing systematic %s sample %s.' % (systematic, sample))

        infile = '%s/%s/%s.root' % (
          Common.SampleLocation, Common.YieldSample, Common.filename(set, sample, systematic)
        )        

        if sampletype == 'training':
          infile = '%s/%s/%s.root' % (
            Common.SampleLocation, Common.TrainingSample, Common.filename(set, sample, systematic)
          )
        elif sampletype == 'testing':
          infile = '%s/%s/%s.root' % (
            Common.SampleLocation, Common.TestingSample, Common.filename(set, sample, systematic)
          )
          
        if self.isParameter('xcheck'):
          infile = '%s/crosscheck_sample/%s/%s.root' % (
            Common.SampleLocation, self.getParameter('xcheck'), Common.filename(set, sample, systematic)
          )

        # Check if the file already exist
        if not os.path.isfile(infile):
          self.message('Tree file %s already exist skipping ...' % infile)
          continue

        outfile = '%s/%s.root' % (
          outdir, Common.filename(set, sample, systematic)
        )        

        logfile = '%s/%s.log' % (
          outdir, Common.filename(set, sample, systematic)
        )        
                  
        # Executing the tree production
        command = '%s/src/support/TopovarProducer.py --combinations=%s:%s --input=%s --output=%s >& %s' % (
          Common.NeatDirectory, Common.NeatOutputName, chdir, infile, outfile, logfile
        )
        print command
        os.system(command)
                  
    ## Merge signal samples 

    # Check if there is anything to merge
    if type(Common.YieldSignals) == list and len(Common.YieldSignals) > 1 and Common.MergeSignals == True:
      # Loop over all the systematics
      for systematic in Common.Systematics + ['']:
        files = ''
        for signal in YieldSignals:
          file = '%s/%s.root' % (outdir, Common.filename(set, signal, systematic))
          if os.path.isfile(file):
            files = files + ' ' + file
        if len(files.split(' ')) < 3:
          self.message('No signal files to be merged for systematic %s ...' % systematic)
          continue 
        sample = ''.join(YieldSignals)
        merge = '%s/%s.root' % (outdir, Common.filename(set, sample, systematic))
        log = '%s/%s.log' % (outdir, Common.filename(set, sample, systematic))
        if not os.path.isfile(merge):
          self.message('Merging tree file %s' % merge)
          command = 'hadd %s%s >& %s' % (merge, files, log)
          os.system(command)
        else:
          self.message('Tree file %s already exist skipping ...' % merge)
    

# Execute
TreeProducer().loop()
