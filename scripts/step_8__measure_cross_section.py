#! /usr/bin/env python 
# XSectionWrapper 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Xsectio wrapper to measure xsection using top_statistics


import glob, string, sys, shutil

# Enabling root in batch mode
sys.argv.append('-b')

from Common import *
from Processor import *
from Util import *
from WebpageWriter import *

class XSectionWrapper(Processor):

  ## Constructor
  def __init__(self):
    super(XSectionWrapper, self).__init__()
    # Initializing allowed processor parameters
    self.defineParameter('input', 'Provides the input directory with a neat histograms.')
    self.defineParameter('limit', 'Type of limit to be computed (default expected)')
    self.defineParameter('topstat', 'Location of top_statistics. If no provided only posterior plots are created.')
    # Command to execute top statistics interface
    self.__njets = ''
    self.__command = None
    
  
  # Auxiliary function to write to command   
  def __write(self, string):
    if not self.__command:
      self.__command = string
    else:
      self.__command = self.__command + ' %s' % string 


  # Redefining start
  def start(self):
    # Hack for jet combined
    if type(Common.XSectionNjets) == list:
      if 'JetsCombined' in Common.XSectionNjets: 
        self.__njets = ','.join(Common.Njets)
    else:
      if Common.XSectionNjets == 'JetsCombined': 
        self.__njets = ','.join(Common.Njets)      
    # Redefining channels for measuring xsection
    Common.RecoVersions = Common.XSectionRecoVersions
    Common.Leptons = Common.XSectionLeptons
    Common.Ntags = Common.XSectionNtags
    Common.Njets = Common.XSectionNjets
    # Running processor start
    super(XSectionWrapper, self).start()
    # Add bininng and systematic to the loops
    self.addLoop('binning', Common.XSectionBinnings)
    self.addLoop('systematic', Common.XSectionSystematics)
    self.addLoop('signal', Common.XSectionSignals)


  ## Redefining end
  def end(self):
    # Setting the self.__outdir directory
    outdir = '%s/scratch/%s/XSection' % (
      Common.NeatDirectory, self.getParameter('input')
    )
    
    # Prepare the looping option for signal and systematics
    Signals = Common.XSectionSignals
    if type(Signals) != list:
      Signals = [Common.XSectionSignals]

    # Prepare the looping option for signal and systematics
    Systematics = Common.XSectionSystematics
    if type(Systematics) != list:
      Systematics = [Common.XSectionSystematics]

    # Webpage type
    webtype = ''
    limit = self.getParameter('limit', 'expected')
    if limit == 'expected':
      webtype = 'expected_limits'
    elif limit == 'observed':
      webtype = 'limits'
    else:
      raise ProcessorError('Unknown limit option (options: expected, observed).')
        
    # Producing the webpages    
    for signal in Signals:
      for systematic in Systematics:
        # Webpage title
        title = 'Combined NEAT output plots for %s, signal %s and systematic %s' % (self.getParameter('input'), signal, systematic)
        options = {'signal':signal, 'systematic':systematic}
        WebpageWriter(title, webtype, options).write('%s/%s-posterior-%s-%s-plots.html' % (outdir, limit, signal, systematic))
        

  ## Process each channel
  def process(self, set):

    channel = channelName(set)
    self.message(
      'Processing channel %s, binning %s, systematic %s and signal %s' % (channel, set['binning'], set['systematic'], set['signal'])
    )

    # Setting the indir directory
    indir = '%s/scratch/%s/YieldHistograms' % (
      Common.NeatDirectory, self.getParameter('input')
    )

    limit = self.getParameter('limit', 'expected')
    if limit == 'expected':
      limitname = 'expected_limit'
    elif limit == 'observed':
      limitname = 'limit'
    else:
      raise ProcessorError('Unknown limit option (options: expected, observed).')    

    # Setting the self.__outdir directory
    outdir = '%s/scratch/%s/XSection/%s_%s_%s_%s_%s' % (
      Common.NeatDirectory, self.getParameter('input'),
      limitname, set['signal'], channel, set['binning'], set['systematic']
    )

    # Check for output directory
    if not os.path.exists(outdir):
      os.makedirs(outdir)
    
    # Do the measurement if topstat is defined
    if self.isParameter('topstat'):

      # Copy the flat systematic tables
      for file in glob.glob(os.path.join('%s/configs/' % Common.NeatDirectory, 'sys*.txt')):
        shutil.copy(file, outdir) 

      # Writting csh source 
      file = open ('%s/support/wrappers/RunTopStatistics.wrapper' % Common.NeatDirectory)
      template = string.Template(file.read())
      file.close()
      script = '%s/RunTopStatistics.csh' % outdir
      file = open(script, 'w')
      file.write(template.safe_substitute(topstat=self.getParameter('topstat')))
      file.close()

      # Editing command line to execute top statistic interface
      config = {}
      config['indir'] = indir
      limit = self.getParameter('limit', 'expected')
      if limit == 'expected':
        config['limit'] = 'expected_limit'
      elif limit == 'observed':
        config['limit'] = 'limit'
      else:
        raise ProcessorError('Unknown limit option (options: expected, observed).')
      config['systype'] = set['systematic']
      config['nbins'] = set['binning']
      config['recover'] = set['reco']
      config['leptontype'] = set['lepton']
      config['tagtype'] = set['ntag']
      if set['njet'] == 'JetsCombined':
        config['jettype'] = self.__njets
      else:
        config['jettype'] = set['njet']      
      config['signaltype'] = set['signal']
      config['NeatOutputName'] = Common.NeatOutputName
 
      # Writting top statistics script 
      file = open ('%s/support/wrappers/TopStatisticInterface.wrapper' % Common.NeatDirectory)
      template = string.Template(file.read())
      file.close()
      script = '%s/TopStatisticInterface.sh' % outdir
      file = open(script, 'w')
      file.write(template.safe_substitute(config))
      file.close()
    
      # Execute top statistics
      os.system('cd %s; csh RunTopStatistics.csh >& top-statistics.log' % outdir)

    # Configuration 
    config = {}
    config['signaltype'] = set['signal']
    config['luminosity'] = Common.Luminosity[set['reco']]

    # Writting make posterior plot script 
    file = open ('%s/support/wrappers/MakePosteriorPlot.wrapper' % Common.NeatDirectory)
    template = string.Template(file.read())
    file.close()
    script = '%s/MakePosteriorPlot.sh' % outdir
    file = open(script, 'w')
    file.write(template.safe_substitute(config))
    file.close()
    
    # Execute the script
    os.system('cd %s; bash MakePosteriorPlot.sh >& make-posterior-plot.log' % outdir)


XSectionWrapper().loop()
