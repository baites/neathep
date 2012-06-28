#! /usr/bin/env python 
# PlotProducer 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Produce histogram plots of the discriminator


import sys, time

# Enabling root in batch mode
sys.argv.append('-b')

from ROOT import gPad, TCanvas, TFile, TH1F, THStack, TLatex, TLegend

from neat.nn import  nn_cpp as nn

from Common import *
from Processor import *
from Util import *
from WebpageWriter import *


# IMPORTANT: Transfer the ownership to the user (not TFile)
TH1F.AddDirectory(ROOT.kFALSE)

# Style features
ROOT.gStyle.SetEndErrorSize(3)
ROOT.gStyle.SetErrorX(0.5)


class PlotProducer(Processor):

  ## Constructor
  def __init__(self):

    super(PlotProducer, self).__init__()
    # Initializing allowed processor parameters
    self.defineParameter('input','Provides the input directory with a neat histograms.')

    # Creating sample dictionary
    self.__samples = {}
    self.__histos = {}


  # Redefining start
  def start(self):

    # Control plots do not apply to systematic samples
    Common.Systematics = []

    # Appending combined channels
    if hasattr(Common, 'CombinedRecoVersions'):
      Common.RecoVersions.append(Common.CombinedRecoVersions)
    if hasattr(Common, 'CombinedLeptons'):
      Common.Leptons.append(Common.CombinedLeptons)
    if hasattr(Common, 'CombinedNtags'):
      Common.Ntags.append(Common.CombinedNtags)
    if hasattr(Common, 'CombinedNjets'):
      Common.Njets.append(Common.CombinedNjets)

    # Running processor start
    super(PlotProducer, self).start()

  
  ## Redefining end
  def end(self):
    # Setting the self.__outdir directory
    outdir = '%s/scratch/%s/ControlPlots' % (
      Common.NeatDirectory, self.getParameter('input')
    )
    title = 'Combined NEAT output plots for %s' % self.getParameter('input')
    WebpageWriter(title, type='profiles').write('%s/profile-plots.html' % outdir)
    

  ## Merger the channel in macro channels
  def merge(self, sample, set, indir):

    # Collecting merging combination
    
    loopset = {}
    
    values = [ set['reco'] ]
    if hasattr(Common, 'CombinedRecoVersions') and set['reco'] in Common.CombinedRecoVersions:
      values = Common.RecoVersions[:-1]
    loopset = combinedSets(loopset, { 'reco': values })
    
    values = [ set['lepton'] ]
    if hasattr(Common, 'CombinedLeptons') and set['lepton'] in Common.CombinedLeptons:
      values = Common.Leptons[:-1]
    loopset = combinedSets(loopset, { 'lepton': values })

    values = [ set['ntag'] ]
    if hasattr(Common, 'CombinedNtags') and set['ntag'] in Common.CombinedNtags:
      values = Common.Ntags[:-1]
    loopset = combinedSets(loopset, { 'ntag': values })

    values = [ set['njet'] ]
    if hasattr(Common, 'CombinedNjets') and set['njet'] in Common.CombinedNjets:
      values = Common.Njets[:-1]
    loopset = combinedSets(loopset, { 'njet': values })

    # Check for merging

    if len(loopset) == 1: return

    # List of files to merge
  
    files = ''                  
    for loop in loopset:
      file = '%s/%s_zero.root' % (indir, channelName(loop, sample))      
      files = files + ' ' + file
     
    # Merging the files
  
    merge = '%s/%s_zero.root' % (indir, channelName(set, sample))
    log = '%s/%s_zero.log' % (indir, channelName(set, sample))      

    if not os.path.isfile(merge):
      self.message('Merging in histogram files %s' % channelName(set, sample))
      command = 'hadd %s%s >& %s' % (merge, files, log)
      os.system(command)


  ## Merge signal samples 
  def mergeSignals(self, set, indir):
    # Check if there is anything to merge
    if type(Common.YieldSignals) == list and len(Common.YieldSignals) > 1:
      # Loop over all the systematics
      for systematic in Common.Systematics + ['zero']:
        files = ''
        for signal in YieldSignals:
          file = '%s/%s_%s.root' % (indir, channelName(set, signal), systematic)
          files = files + ' ' + file
        sample = ''.join(YieldSignals)
        merge = '%s/%s_%s.root' % (indir, channelName(set, sample), systematic)
        log = '%s/%s_%s.log' % (indir, channelName(set, sample), systematic)      
        if not os.path.isfile(merge):
          self.message('Merging in histogram files %s_%s' % (channelName(set, sample),systematic))
          command = 'hadd %s%s >& %s' % (merge, files, log)
          os.system(command)
        

  ## Process each channel
  def process(self, set):

    channel = channelName(set)
    self.message('Processing channel %s' % channel)

    # Setting the indir directory
    indir = '%s/scratch/%s/YieldHistograms' % (
      Common.NeatDirectory, self.getParameter('input')
    )

    # Setting the self.__outdir directory
    outdir = '%s/scratch/%s/ControlPlots' % (
      Common.NeatDirectory, self.getParameter('input')
    )

    # Check for output directory
    if not os.path.exists(outdir):
      os.makedirs(outdir)

    # Create the list of sample
    samples = None
    if type(Common.YieldSignals) == list:
      samples = Common.YieldBackgrounds + Common.YieldSignals
    else:
      samples = Common.YieldBackgrounds + [Common.YieldSignals]

    # Set canvas
    canvas = TCanvas("canvas", "Data/MC for NEAT discriminator.",1000,800)
    canvas.Clear()
    canvas.SetLeftMargin(0.14)
    canvas.SetRightMargin(0.05)
    canvas.SetBottomMargin(0.13)
    canvas.SetTopMargin(0.03)

    for bin in Common.Binning:
      # Histogram holder
      histograms = {}
      # Legend
      leg2 = TLegend(1.0,0.8,0.8,1.0)
      # Flag to indicate first plot in canvas
      flag = False
        
      # Loop over the different samples
      for subset in ['training','testing','yield']:
        # Setting the indir directory
        indir = ''
        if subset == 'training':
          indir = '%s/scratch/%s/TrainingHistograms' % (
            Common.NeatDirectory, self.getParameter('input')
          )
        elif subset == 'testing':
          indir = '%s/scratch/%s/TestingHistograms' % (
            Common.NeatDirectory, self.getParameter('input')
          )
        elif subset == 'yield':
          indir = '%s/scratch/%s/YieldHistograms' % (
            Common.NeatDirectory, self.getParameter('input')
          )
   
        # Signal and background keys
        signalkey = 'signals_%s' % subset
        backgroundkey = 'backgrounds_%s' % subset
        # Loop over signal+backgorund files
        for sample in samples:
          # Merge to create the combined channels
          self.merge(sample, set, indir)
          # Input file with histograms
          infile = '%s/%s_zero.root' % (
            indir, channelName(set, sample)
          )
          print 'Processing sample:', infile   
          # Open the file with histograms 
          file = TFile(infile)
          # Reading and clonning the histogram
          histogram = file.Get('%s_%s' % (Common.NeatOutputName, bin))

          # Check for signal and background samples
          if sample in Common.YieldSignals:
            # Add all the signal samples
            if not signalkey in histograms:
              histograms[signalkey] = histogram.Clone()
            else:
              histograms[signalkey].Add(histogram)
          elif sample in Common.YieldBackgrounds:
            # Add all the background samples
            if not backgroundkey in histograms:
              histograms[backgroundkey] = histogram.Clone()
            else:
              histograms[backgroundkey].Add(histogram)         
  
        # Creating the discriminator shapes
        signalName = ''
        # Signal name
        if type(Common.YieldSignals) == list:
          signalName = ''.join(Common.YieldSignals)      
        else:
          signalName = Common.YieldSignals
        # Normalizing the histograms
        histograms[signalkey].Scale(1./histograms[signalkey].Integral())
        # Normalizing the histograms
        histograms[backgroundkey].Scale(1./histograms[backgroundkey].Integral())

        histograms[signalkey].SetLineColor(ROOT.kBlue)
        histograms[signalkey].SetMarkerColor(ROOT.kBlue)
        histograms[signalkey].SetLineWidth(2)
        if subset == 'training':
          histograms[signalkey].SetMarkerStyle(20)
        elif subset == 'testing':
          histograms[signalkey].SetMarkerStyle(21)
        elif subset == 'yield':
          histograms[signalkey].SetMarkerStyle(22) 
     
        histograms[signalkey].GetXaxis().SetTitle('%s NEAT output' % signalName)
        leg2.AddEntry(histograms[signalkey], 'Signal on %s' % subset,'p')

        # Background is red and filled with diagonal lines 
        histograms[backgroundkey].SetLineColor(ROOT.kRed)
        histograms[backgroundkey].SetMarkerColor(ROOT.kRed)
        histograms[backgroundkey].SetLineWidth(2)
        if subset == 'training':
          histograms[backgroundkey].SetMarkerStyle(20)
        elif subset == 'testing':
          histograms[backgroundkey].SetMarkerStyle(21)
        elif subset == 'yield':
          histograms[backgroundkey].SetMarkerStyle(22)
        
        histograms[backgroundkey].GetXaxis().SetTitle('%s NEAT output' % signalName)    
        leg2.AddEntry(histograms[backgroundkey], 'Background on %s' % subset,'p')
      
        # Plot first the one with largest amplitud
        smax = histograms[signalkey].GetMaximum()
        bmax = histograms[backgroundkey].GetMaximum()      
        if smax > bmax:
          if not flag:
            histograms[signalkey].Draw()
          else:
            histograms[signalkey].Draw('same')
          histograms[backgroundkey].Draw('same')
        else:
          if not flag:
            histograms[backgroundkey].Draw()
          else:
            histograms[backgroundkey].Draw('same')
          histograms[signalkey].Draw('same')
        flag = True

      leg2.Draw()

      # Save the canvas
      outfile = '%s/profiles_%s_%s' % (
          outdir, channelName(set), bin
      )
      canvas.SaveAs('%s.eps' % outfile)
      canvas.SaveAs('%s.png' % outfile)
      
   
# Execute
PlotProducer().loop()

