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
    self.defineParameter('xcheck','Name for creating xcheck sample trees.')
    self.defineParameter('discriminator-legends','Flag to activate or deactivate discriminator legends (default false).')
    self.defineParameter('profile-legends','Flag to activate or deactivate profile legends (default true).')

    # Creating sample dictionary
    self.__samples = {}
    self.__histos = {}


  # Redefining start
  def start(self):

    # Special case for xcheck
    if self.isParameter('xcheck'):       
      # Redefining channels
      Common.Ntags = getattr(Common.XCheckNtags, self.getParameter('xcheck'))
      Common.Njets = getattr(Common.XCheckNjets, self.getParameter('xcheck'))
      # Redefining combined channels
      if hasattr(Common, 'CombinedXCheckNtags'):
        Common.CombinedNtags = getattr(Common.CombinedXCheckNtags, self.getParameter('xcheck'))
      else:
        del Common.CombinedNtags
      if hasattr(Common, 'CombinedXCheckNJets'):
        Common.CombinedNjets = getattr(Common.CombinedXCheckNjets, self.getParameter('xcheck'))
      else:
        del Common.CombinedNjets
      # Removing systematics from the loops
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
    outdir = '%s/scratch/%s/YieldPlots' % (
      Common.NeatDirectory, self.getParameter('input')
    )
    if self.isParameter('xcheck'):
      outdir = '%s/scratch/%s/XCheckPlots/%s' % (
        Common.NeatDirectory, self.getParameter('input'), self.getParameter('xcheck')
      )      
    title = 'Combined NEAT output plots for %s' % self.getParameter('input')
    #WebpageWriter(title, type='discriminators').write('%s/discriminator-plots.html' % outdir)
    #if not self.isParameter('xcheck'):
    #  WebpageWriter(title, type='profiles').write('%s/profile-plots.html' % outdir)
    

  ## Process each channel
  def process(self, set):

    self.message('Processing channel %s' % set['channel'])

    # Setting the indir directory
    indir = '%s/scratch/%s/YieldHistograms' % (
      Common.NeatDirectory, self.getParameter('input')
    )
    if self.isParameter('xcheck'):
      indir = '%s/scratch/%s/XCheckHistograms/%s' % (
        Common.NeatDirectory, self.getParameter('input'), self.getParameter('xcheck')
      )

    # Setting the self.__outdir directory
    outdir = '%s/scratch/%s/YieldPlots' % (
      Common.NeatDirectory, self.getParameter('input')
    )
    if self.isParameter('xcheck'):
      outdir = '%s/scratch/%s/XCheckPlots/%s' % (
        Common.NeatDirectory, self.getParameter('input'), self.getParameter('xcheck')
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
    samples = samples + [Common.Data]

    # Set canvas
    canvas = TCanvas("canvas", "Data/MC for NEAT discriminator.",1000,800)
    canvas.Clear()
    canvas.SetLeftMargin(0.14)
    canvas.SetRightMargin(0.05)
    canvas.SetBottomMargin(0.13)
    canvas.SetTopMargin(0.03)
        
    # Loop over the different binning
    for bin in Common.Binning:
      # Histogram holder
      histograms = {}
      stack = THStack('stack','%s' % set['channel'])
      # Legend
      leg = TLegend(1.0,0.6,0.6,1.0)
      leg.SetNColumns(2)

      # Loop over signal+backgorund files
      for sample in samples:
        # Merge to create the combined channels
        # self.merge(sample, set, indir)
        # Input file with histograms
        infile = '%s/%s.root' % (
          indir, Common.filename(set, sample)
        )
        print 'Processing sample:', infile   
        # Open the file with histograms 
        file = TFile(infile)
        # Reading and clonning the histogram
        histogram = file.Get('%s_%s' % (Common.NeatOutputName,bin))

        # Check for signal and background samples
        if sample in Common.YieldSignals:
          # Add all the signal samples
          if not 'signals' in histograms:
            histograms['signals'] = histogram.Clone()
          else:
            histograms['signals'].Add(histogram)
        elif sample in Common.YieldBackgrounds:
          # Add all the background samples
          if not 'backgrounds' in histograms:
            histograms['backgrounds'] = histogram.Clone()
          else:
            histograms['backgrounds'].Add(histogram)         

        # Do not add data to the stack
        if sample != Common.Data:
          histogram.SetLineColor(Common.ColorCodes[sample])
          histogram.SetFillColor(Common.ColorCodes[sample])
          histograms[sample] = histogram.Clone()
          stack.Add(histograms[sample])
          leg.AddEntry(histogram, '%s' % sample,'f')
        else:
          histogram.SetLineColor(Common.ColorCodes[sample])        
          histogram.SetMarkerStyle(8)
          histograms[sample] = histogram.Clone()   

      # Creating the data/mc

      # Stack axes only exist after drawing
      stack.Draw('hist')
      # Compute user range
      maxdata = histograms[Common.Data].GetMaximum() + histograms[Common.Data].GetBinError(histograms[Common.Data].GetMaximumBin())
      maxcount = max(stack.GetMaximum(), maxdata)
      signalName = ''
      # Signal name
      if type(Common.YieldSignals) == list:
        signalName = ''.join(Common.YieldSignals)      
      else:
        signalName = Common.YieldSignals
      histograms[Common.Data].GetXaxis().SetTitle('%s NEAT output' % signalName)
      histograms[Common.Data].GetYaxis().SetTitle('Event Yield')
      histograms[Common.Data].GetYaxis().SetTitleOffset(1.2)
      histograms[Common.Data].GetYaxis().SetRangeUser(0, 1.1*maxcount)
      histograms[Common.Data].SetMarkerSize(3) 
      if histograms[Common.Data].GetNbinsX() >= 50:
        histograms[Common.Data].SetMarkerSize(2)
      histograms[Common.Data].SetLineWidth(3)
      histograms[Common.Data].SetMarkerStyle(8)
      histograms[Common.Data].Draw('e1')
      stack.Draw('samehist')
      # Draw data point
      histograms[Common.Data].Draw('e1,same')
      # Draw legend
      if self.getParameter('discriminator-legends', 'false') == 'true': leg.Draw()
      # Draw text
      text = TLatex()
      text.SetTextFont(62)
      text.SetTextAlign(32)
      text.SetNDC()
      text.SetTextSize(0.050)
      text.DrawLatex(0.94, 0.94-0*0.05, 'CMS %s fb^{-1}' % Common.Luminosity[set['channel']]);
      text.SetTextColor(13)      
      text.DrawLatex(0.94, 0.94-1*0.05, '%s' % Common.Labels[set['channel']] ) 

      # Update canvas
      canvas.Update()
      # Save the canvas
      outfile = '%s/%s_%s' % (
          outdir, Common.filename(set), bin
      )
      canvas.SaveAs('%s.eps' % outfile)
      canvas.SaveAs('%s.png' % outfile)

      # Creating the discriminator shapes

      # No profile plots for xchecks
      if self.isParameter('xcheck'): continue
      
      # Normalizing the histograms
      histograms['signals'].Scale(1./histograms['signals'].Integral())
      # Normalizing the histograms
      histograms['backgrounds'].Scale(1./histograms['backgrounds'].Integral())
      # Legend
      #if self.isParameter('legend'):
      leg2 = TLegend(1.0,0.8,0.8,1.0)
      #else:
        #leg2 = TLegend(0,0,0,0)
      # Signal is blue and solid fill style
      histograms['signals'].SetLineColor(ROOT.kBlue)
      histograms['signals'].SetFillColor(ROOT.kBlue)
      histograms['signals'].SetFillStyle(3002)
      histograms['signals'].SetLineWidth(3)
      histograms['signals'].GetXaxis().SetTitle('%s NEAT output' % signalName)
      leg2.AddEntry(histograms['signals'], 'Signal','f')

      # Background is red and filled with diagonal lines 
      histograms['backgrounds'].SetLineColor(ROOT.kRed)
      histograms['backgrounds'].SetFillColor(ROOT.kRed)
      histograms['backgrounds'].SetFillStyle(3004)
      histograms['backgrounds'].SetLineWidth(3)      
      histograms['backgrounds'].GetXaxis().SetTitle('%s NEAT output' % signalName)    
      leg2.AddEntry(histograms['backgrounds'], 'Background','f')
      
      # Plot first the one with largest amplitud
      smax = histograms['signals'].GetMaximum()
      bmax = histograms['backgrounds'].GetMaximum()      
      if smax > bmax:
        histograms['signals'].Draw('hist')
        histograms['backgrounds'].Draw('samehist')
      else:
        histograms['backgrounds'].Draw('hist')
        histograms['signals'].Draw('samehist')
      if self.getParameter('profile-legends', 'true') == 'true': leg2.Draw()   
      # Save the canvas
      outfile = '%s/profiles_%s_%s' % (
          outdir, set['channel'], bin
      )
      canvas.SaveAs('%s.eps' % outfile)
      canvas.SaveAs('%s.png' % outfile)
      
   
# Execute
PlotProducer().loop()

