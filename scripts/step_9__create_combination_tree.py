#! /usr/bin/env python 
# CombinationTreeProducer 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Produce trees with neat output


import sys, string

# Enabling root in batch mode
sys.argv.append('-b')

from ROOT import TCanvas, TH1F, THStack
import pickle

from neat.nn import  nn_cpp as nn

from Common import *
from Processor import *
from TopovarReader import *
from TopovarWriter import *
from Util import *
from VariableNormalizer import *

import Neat

ROOT.SetMemoryPolicy( ROOT.kMemoryStrict )

class CombinationTreeProducer(Processor):

  ## Constructor
  def __init__(self):    
    # Processor constructor
    super(CombinationTreeProducer, self).__init__()
    # Initializing allowed processor parameters
    self.defineParameter('combs','Provide those discriminator to be combined in the format --combs=key1:input1,...,keyn:inputn.')
    self.defineParameter('input','Input directory with the use for combination.')
    self.defineParameter('output','Drirectory output for combination tree producer.')
    self.defineParameter('postfix','File name postfix.')
    self.defineParameter('systematics', 'Set the production of systematic samples (default false).')
    self.defineParameter('xcheck','Name for creating xcheck sample trees.')
    self.defineParameter('rebuild', 'Provide dzero working area to rebuild topovars with compatible root version.')


  # Redefining start
  def start(self):
    # Redefinition of the channels
    if self.isParameter('xcheck'):
      # Redefining tag channels
      Common.Ntags = getattr(Common.XCheckNtags, self.getParameter('xcheck'))
      Common.Njets = getattr(Common.XCheckNjets, self.getParameter('xcheck'))
      Common.Systematics = []
    # Running processor start
    super(CombinationTreeProducer, self).start()
    

  ## Rebuild root compatible topovars
  def rebuild(self, set, systematics, outdir):

    # Channel name
    channel = channelName(set)
    pattern = '%s_%s_*_%s_%s' % (set['reco'], set['lepton'], set['ntag'], set['njet'])
    self.message('Rebuilding channel %s' % channel)  
    # Writting topovar rebuilder
    file = open ('%s/support/wrappers/RebuildTopovarFiles.wrapper' % Common.NeatDirectory)
    template = string.Template(file.read())
    file.close()
    script = '%s/RebuildTopovarFiles-%s.sh' % (outdir, channel)
    file = open(script, 'w')
    file.write(template.safe_substitute(systematics=' '.join(systematics), channel=pattern))
    file.close()

    # Writting run topovar rebuilder
    file = open ('%s/support/wrappers/RunRebuildTopovarFiles.wrapper' % Common.NeatDirectory)
    template = string.Template(file.read())
    file.close()
    script = '%s/RunRebuildTopovarFiles-%s.csh' % (outdir, channel)
    file = open(script, 'w')
    file.write(template.safe_substitute(release=self.getParameter('rebuild'), channel=channel))
    file.close()
    
    # Execute top statistics
    os.system('cd %s; csh RunRebuildTopovarFiles-%s.csh >& rebuild-%s-topovars.log' % (outdir, channel, channel))
    
          
  ## Process each channel
  def process(self, set):

    channel = channelName(set)

    self.message('Processing channel %s' % channel)

    # Setting outdir directory
    outdir = '%s' % self.getParameter('output') 

    # Check for output directory
    if not os.path.exists(outdir):
      os.makedirs(outdir)

    combinations = [] 
    # Loop over the inputs
    for combination in self.getParameter('combs').split(','):
      # Parsing the key and input
      parse = combination.split(':')
      # Checking the format
      if len(parse) != 2:
        raise ProcessorError('Wrong combination format')
      # Parsing key and input
      combinations.append('%s:%s/Trainings/%s' % (parse[0],parse[1], channel))
    combinations = ','.join(combinations)
    
    # Set the list of systematic samples
    systematics = None
    if self.getParameter('systematics', 'false') == 'true':
      systematics = Common.Systematics + ['zero']
    else:
      systematics = ['zero']

    # Loop over all the samples producing the trees
    for systematic in systematics:
      for sample in Common.YieldBackgrounds + Common.YieldSignals + ['DATA']:

        # No systematics for QCD and DATA
        if (sample == 'DATA' or sample == 'QCD') and systematic != 'zero': continue

        self.message('Processing systematic %s samples %s.' % (systematic, sample))

        infile = '%s/%s_%s%s.root' % (
          self.getParameter('input'), channelName(set, sample), systematic, self.getParameter('postfix','')
        )
        
        outfile = '%s/%s_%s%s.root' % (
          outdir, channelName(set, sample), systematic, self.getParameter('postfix','')
        )        

        logfile = '%s/%s_%s%s.log' % (
          outdir, channelName(set, sample), systematic, self.getParameter('postfix','')
        )

        # Check in the input file exist
        if not os.path.isfile(infile):
          self.message('Warning missing input file %s skipping ...' % infile)
          continue
                  
        # Check if the file already exist
        if os.path.isfile(outfile):
          self.message('Tree file %s already exists skipping ...' % outfile)
          continue          

        # Executing the tree production
        command = '%s/support/python/TopovarProducer.py --combinations=%s --input=%s --output=%s >& %s' % (
          Common.NeatDirectory, combinations, infile, outfile, logfile
        )        
        os.system(command)
                  
    # Merge signal samples 
    # Check if there is anything to merge
    if type(Common.YieldSignals) == list and len(Common.YieldSignals) > 1:
      # Loop over all the systematics
      for systematic in systematics:
        files = ''
        for signal in YieldSignals:
          file = '%s/%s_%s%s.root' % (outdir, channelName(set, signal), systematic, self.getParameter('postfix',''))
          if os.path.isfile(file):
            files = files + ' ' + file
        if len(files.split(' ')) < 3:
          self.message('No signal files to be merged for systematic %s ...' % systematic)
          continue
        sample = ''.join(YieldSignals)
        merge = '%s/%s_%s%s.root' % (outdir, channelName(set, sample), systematic, self.getParameter('postfix',''))
        log = '%s/%s_%s%s.log' % (outdir, channelName(set, sample), systematic, self.getParameter('postfix',''))      
        if not os.path.isfile(merge):
          self.message('Merging tree file %s' % merge)
          command = 'hadd %s%s >& %s' % (merge, files, log)
          os.system(command)
        else:
          self.message('Tree file %s already exist skipping ...' % merge)

    # Rebuild if needed
    if self.isParameter('rebuild'):
      self.rebuild(set, systematics, outdir)


# Execute
CombinationTreeProducer().loop()

