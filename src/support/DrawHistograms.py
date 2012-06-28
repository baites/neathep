#! /usr/bin/env python

## Produces plots from  sample inputs
from ROOT import gRandom,TCanvas,TH1F
import shutil, string, pickle, os

from neat.config import Config as NeatParameters
from neat.nn import nn_cpp as nn

def drawHistos(signalSample, backgroundSample, net_pheno, outdir, channel):
  
  ## Produce histograms

  # Set Canvas
  c1 = TCanvas('c1','Discriminator_output',200,10,700,500)


  signal_histo = TH1F('signal_histo','Discriminator output', 80, 0, 1)
  signal_histo.Sumw2()

  for event in signalSample:
    # Extract variables and weight
    variables = event[1:]
    weight = event[0]
    # Not strictly necessary in feedforward nets
    net_pheno.flush()
    # Evaluate NN
    discriminator =  net_pheno.sactivate(variables)[0]
    signal_histo.Fill(discriminator, weight)
  
  # Signal is blue and solid fill style
  signal_histo.SetLineColor(4)
  signal_histo.SetFillColor(4)
  signal_histo.SetFillStyle(3002)
  signal_histo.SetLineWidth(3)
  signal_histo.DrawNormalized('hist')

  
  background_histo = TH1F('background_histo','Discriminator output', 80, 0, 1)
  background_histo.Sumw2()
  
  for event in backgroundSample:
    # Extract variables and weight
    variables = event[1:]
    weight = event[0]
    # Not strictly necessary in feedforward nets
    net_pheno.flush()
    # Evaluate NN
    discriminator =  net_pheno.sactivate(variables)[0]
    background_histo.Fill(discriminator, weight)
  
  # Background is red and filled with diagonal lines  
  background_histo.SetLineColor(2)
  background_histo.SetFillColor(2)
  background_histo.SetFillStyle(3004)
  background_histo.SetLineWidth(3)
  background_histo.DrawNormalized('histsame')

 
  # Output
  c1.Update()

  # Save file
  trynumber = 1
  if os.path.isfile('%s/discriminator_output_%s_1.png' % (outdir, channel)):
    while os.path.isfile('%s/discriminator_output_%s_%s.png' % (outdir, channel, trynumber)):
      trynumber += 1

  c1.SaveAs('%s/discriminator_output_%s_%s.png' % (outdir, channel, trynumber))

