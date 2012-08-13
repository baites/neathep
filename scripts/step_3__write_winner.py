#! /usr/bin/env python

# This script implements the selection of the best NN for each channel
# and writes it to channel_winner.txt located in each channel directory.

import sys

# Enabling root in batch mode
sys.argv.append('-b')

from ROOT import gRandom,TCanvas,TH1F
import shutil, string, pickle, os

from neat.config import Config as NeatParameters
from neat.nn import  nn_cpp as nn

from Processor import *
from Common import *
from Util import *
from TopovarReader import *
from VariableNormalizer import *

import Neat
import Training


class WriteWinner(Processor):

  ##Constructor
  def __init__(self):
    super(WriteWinner, self).__init__()
    self.defineParameter('input','Provides the input directory with neat variable selection.')
    self.defineParameter('normalize','Run the normalization (default true)')
    self.__setNeatParameters(Neat)
      
  
  ## Process each channel
  def process(self, set, lock=None):

    # Print channel being processed
    self.message('Processing channel %s.' % set['channel'])
    
    # Placeholder for winner
    winner = None
    # Variable Normalization
    aves = {}; stds = {}
    
    # Loop over the training sets
    for counter in xrange(1,Common.NeatNumberTries+1):

      # Setting the indir directory
      indir = '%s/scratch/%s/Trainings/%s/Training%05d' % (
        Common.NeatDirectory, self.getParameter('input'), set['channel'], counter
      )

      # Creating output directory
      outdir = '%s/scratch/%s/Trainings/%s' % (
        Common.NeatDirectory, self.getParameter('input'), set['channel']
      )

      # Look for missing files  
      files = ['neat.config', 'winner.dat']
      missing = False      
      for file in files:
        if not os.path.isfile("%s/%s" % (indir, file)):
          self.message('%s does not exist in %s.' % (file, indir))
          missing = True
      if missing: continue
     
      # Compute the normalization if needed
      if len (aves) == 0 and self.getParameter('normalization','true') == 'true':
        variables = open('%s/inputvars.txt' % indir).readlines()
        variables = [variable.rstrip() for variable in variables]

        # Reading training sample for computing normalization
        training = TopovarReader(variables)

        # Adding training files
        for sample in Common.TrainingBackgrounds + Common.TrainingSignals:
          training.add('%s/%s/%s.root' % (
              Common.SampleLocation, Common.TrainingSample, filename(set, sample)
            )
          )

        normalizer = VariableNormalizer(variables)
        normalizer.add(training.sample(True))
        normalizer.report()

        for variable in variables:
          ave, std = normalizer(variable)
          aves[variable] = ave
          stds[variable] = std

      ## Write winner files
      
      # Read the winner
      net = pickle.load(open('%s/winner.dat' % indir))
  
      # Winner information
      candidate = {
      	'training' : 'Training%05d' % counter,
      	'fitness' : net.fitness,
      	'variables' : variables,
      	'aves' : aves,
      	'stds' : stds
      }

      if not winner or candidate['fitness'] > winner['fitness']:
        self.message('Winner candidate for channel %s found in training %s with fitness %.4g' % (
            set['channel'], candidate['training'], candidate['fitness']
          )
        )
        winner = candidate
            
    file = open('%s/winner.info' % outdir,'w')
    pickle.dump(winner, file)


  ## Set all the neat parameters as loops
  def __setNeatParameters(self, neat):
    for parameter in dir(neat):
      if not parameter.startswith('__'):
        try:
          getattr(NeatParameters, parameter)
        except AttributeError:
          raise ProcessorError('Unknown neat parameter %s.' % parameter)
        self.addLoop(parameter, getattr(neat, parameter))


# Execute
WriteWinner().loop()
