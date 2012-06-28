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
    self.defineParameter('rebin','Activates the bin transformation providing a working area with top_cafe installed.')

  # Redefining start
  def start(self):
    # Redefinition of the channels
    if self.isParameter('xcheck'):
      # Redefining tag channels
      Common.Ntags = getattr(Common.XCheckNtags, self.getParameter('xcheck'))
      Common.Njets = getattr(Common.XCheckNjets, self.getParameter('xcheck'))
      Common.Systematics = []
    elif self.getParameter('testing','yeild') != 'yield':
      # Look for systematics only for yield sample 
      Common.Systematics = []
    # Running processor start
    super(HistogramProducer, self).start()

  
  ## Execute the bin transformation
  def rebinning(self, set):
    self.message('Running bin transformations for %s.' % channelName(set))
    # Variable to be rebin 
    file = open ('%s/BinTransformationDiscriminant.txt' % set['outdir'], 'w')
    file.write('EventWeight\n%s\n' % Common.NeatOutputName)
    file.close()
    # From a wrapper create the set of instructions  
    file = open ('%s/support/wrappers/RunBinTransformation.wrapper' % Common.NeatDirectory)
    template = string.Template(file.read())
    file.close()
    script = '%s/RunBinTransformation-%s.sh' % (set['outdir'], set['channel'])
    file = open(script, 'w')
    file.write(template.safe_substitute(set))
    file.close()
    os.system('csh %s' % script)
        
          
  ## Process each channel
  def process(self, set):

    channel = channelName(set)

    self.message('Processing channel %s' % channel)

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

    # Runs the bin transformation (defined in top_cafe)
    if self.isParameter('rebin'):
      # Adding the indir to the set
      set['indir'] = indir
      # Adding the indir to the set
      set['outdir'] = outdir
      # Adding signal information to the set
      set['signals'] = ''.join(Common.YieldSignals)
      # Adding rebing parameter
      set['topcafe'] = self.getParameter('rebin')
      # Adding the channel name
      set['channel'] = channelName(set)
      # Adding the neat directory
      set['neatdir'] = Common.NeatDirectory
      # Set the systematic flag if needed
      if self.isParameter('xcheck') or self.getParameter('sample','yield') != 'yield':
        set['sysflag'] = '--no-sys'
      else:
        set['sysflag'] = ''
      # Running the rebinning
      self.rebinning(set)
      # Switching move update for adding unbinned histograms
      mode = 'update'
 
    # Create the list of sample
    samples = None
    if type(Common.YieldSignals) == list:
      samples = Common.YieldBackgrounds + Common.YieldSignals
      if len(Common.YieldSignals) > 1:
        samples = samples + [''.join(Common.YieldSignals)]
    else:
      samples = Common.YieldBackgrounds + [Common.YieldSignals]
    samples = samples + ['DATA']
 
    # Loop over all the samples with trees
    for systematic in Common.Systematics + ['zero']:
      for sample in samples:

        # No systematics for QCD and DATA
        if (sample == 'DATA' or sample == 'QCD') and systematic != 'zero': continue
        
        # No systematics in case of xchecks
        if self.isParameter('xcheck') and systematic != 'zero': continue

        self.message('Processing systematic %s samples %s.' % (systematic, sample))

        infile = '%s/%s_%s.root' % (
          indir, channelName(set, sample), systematic
        )        

        # Check in the input file exist
        if not os.path.isfile(infile):
          self.message('Warning missing input file %s skipping ...' % infile)
          continue
        
        # Create a topovar reader only for neat output
        topovars = TopovarReader([Common.NeatOutputName], infile)

        outfile = '%s/%s_%s.root' % (
          outdir, channelName(set, sample), systematic
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
          histograms.fill(getattr(event,Common.NeatOutputName), event.EventWeight)
        

# Execute
HistogramProducer().loop()
