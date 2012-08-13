#! /usr/bin/env python
# HistogramProducer 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Produce histograms with different binning options


import os, string, sys

# Enabling root in batch mode
sys.argv.append('-b')

from Common import *
from HistogramWriter import *
from Processor import *
from TopovarReader import *
from Util import *

import Neat


class HistogramProducer(Processor):

  ## Constructor
  def __init__(self):

    super(HistogramProducer, self).__init__()
    # Initializing allowed processor parameters
    self.defineParameter('input','Provides the input directory with a neat tree directory.')
    self.defineParameter('xcheck','Name for creating xcheck sample trees.')    
    self.defineParameter('sample','Sample use to produce the histograms (default=yield).')


  # Redefining start
  def start(self):
    print Common.Systematics
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
    super(HistogramProducer, self).start()

          
  ## Process each channel
  def process(self, set):

    self.message('Processing channel %s' % set['channel'])

    # Setting the indir directory
    indir = '%s/scratch/%s/YieldTrees' % (
      Common.NeatDirectory, self.getParameter('input')
    )
    sampletype = self.getParameter('sample','yield')
    if sampletype == 'training':
      indir = '%s/scratch/%s/TrainingTrees' % (
        Common.NeatDirectory, self.getParameter('input')
      )
    elif sampletype == 'testing':
      indir = '%s/scratch/%s/TestingTrees' % (
        Common.NeatDirectory, self.getParameter('input')
      )
    elif sampletype != 'yield':
      raise ProcessorError('Unknown sample option %s (allowed options: training, testing and yield).' % sampletype)

    if self.isParameter('xcheck'):
      indir = '%s/scratch/%s/XCheckTrees/%s' % (
        Common.NeatDirectory, self.getParameter('input'), self.getParameter('xcheck')
      )
            
    # Setting the outdir directory
    outdir = '%s/scratch/%s/YieldHistograms' % (
      Common.NeatDirectory, self.getParameter('input')
    )
    if sampletype == 'training':
      outdir = '%s/scratch/%s/TrainingHistograms' % (
        Common.NeatDirectory, self.getParameter('input')
      )
    elif sampletype == 'testing':
      outdir = '%s/scratch/%s/TestingHistograms' % (
        Common.NeatDirectory, self.getParameter('input')
      )
      
    if self.isParameter('xcheck'):
      outdir = '%s/scratch/%s/XCheckHistograms/%s' % (
        Common.NeatDirectory, self.getParameter('input'), self.getParameter('xcheck')
      )
          
    # Check for output directory
    if not os.path.exists(outdir):
      os.makedirs(outdir)

    # File mode for writting histograms
    mode = 'recreate'
 
    # Create the list of sample
    samples = None
    if type(Common.YieldSignals) == list:
      samples = Common.YieldBackgrounds + Common.YieldSignals
      if len(Common.YieldSignals) > 1:
        samples = samples + [''.join(Common.YieldSignals)]
    else:
      samples = Common.YieldBackgrounds + [Common.YieldSignals]
    samples = samples + [Common.Data] 

    # Loop over all the samples with trees
    for systematic in Common.Systematics + ['']:
      for sample in samples:

        # No systematics for QCD and DATA
        if (sample in Common.NoSystematics) and systematic != '': continue

        # No systematics in case of xchecks
        if self.isParameter('xcheck') and systematic != '': continue

        self.message('Processing systematic %s samples %s.' % (systematic, sample))

        infile = '%s/%s.root' % (
          indir, Common.filename(set, sample, systematic)
        )        

        # Check in the input file exist
        if not os.path.isfile(infile):
          self.message('Warning missing input file %s skipping ...' % infile)
          continue
        
        # Create a topovar reader only for neat output
        topovars = TopovarReader([Common.NeatOutputName], infile)

        outfile = '%s/%s.root' % (
          outdir, Common.filename(set, sample, systematic)
        )        
        
        # Create a histogram producer
        histograms = HistogramWriter(outfile, mode)
        # Histogram booking (hardcoded not many options really)
        histograms.book('%s_400' % Common.NeatOutputName, 400, 0., 1.)
        histograms.book('%s_200' % Common.NeatOutputName, 200, 0., 1.)
        histograms.book('%s_100' % Common.NeatOutputName, 100, 0., 1.)
        histograms.book('%s_50' % Common.NeatOutputName, 50, 0., 1.)
        histograms.book('%s_25' % Common.NeatOutputName, 25, 0., 1.)
        
        # Loop over the tree producing histograms of neat output        
        for entry in xrange(topovars.getEntries()):
          if entry % 5000 == 0 and entry != 0:
            self.message('Reading %d events.' % entry)
          # Read one event
          event = topovars.read(entry)
          # Fill the histogram
          histograms.fill(getattr(event,Common.NeatOutputName), getattr(event,Common.EventWeight))
        

# Execute
HistogramProducer().loop()
