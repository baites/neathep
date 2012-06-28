:q
#! /usr/bin/env python
# NeatTraining.py
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Implemantation of neat training


import string, time
import cPickle as pickle

from neat import config, population, chromosome, genome #, visualize

from TopovarReader import *
from Util import *
from VariableNormalizer import *

import Common


# Sinal and background topovar holders
signalYield = None
signalSample = None
backgroundYield = None
backgroundSample = None

  
## Main fuction
def Evaluate(set):
  global signalYield, signalSample, backgroundYield, backgroundSample

  # Reading variable list
  variables = open('%s/inputvars.txt' % set['directory']).readlines()
  variables = [variable.rstrip() for variable in variables]

  # Setting the number of input and output in the neat config file
  file = open ('%s/neat.config' % set['directory'])
  template = string.Template(file.read())
  file.close()
  file = open ('%s/neat.config' % set['directory'], 'w')
  file.write(template.safe_substitute(input_nodes = len(variables), output_nodes = 1))
  file.close()

  # Read neat configuration file
  config.load('%s/neat.config' % set['directory'])
  
  print('Training: Reading signal files')

  # Signal topovars
  signals = TopovarReader(variables)

  # Adding signal files
  for sample in Common.TrainingSignals:
    signals.add('%s/%s/%s_zero_Topo_%s.root' % (
        Common.SampleLocation, Common.TrainingSample, channelName(set, sample), Common.TrainingSample
      )
    )

  # Creating a variable normalizer
  normalizer = VariableNormalizer(variables)

  # Saving the population in buffer
  signalSample = signals.sample(compress = True)
  
  # Adding the sample to the normalizer
  normalizer.add(signalSample)
    
  # Compute the total weight
  signalYield = normalizer.getTotalWeight()

  print ('Training: Reading background files')

  # Background topovars
  backgrounds = TopovarReader(variables)

  # Adding background files
  for sample in Common.TrainingBackgrounds:
    backgrounds.add('%s/%s/%s_zero_Topo_%s.root' % (
        Common.SampleLocation, Common.TrainingSample, channelName(set, sample), Common.TrainingSample
      )
    )

  # Saving the population in buffer
  backgroundSample = backgrounds.sample(compress = True)

  # Adding the sample to the normalizer
  normalizer.add(backgroundSample)

  # Compute the total weight
  backgroundYield = normalizer.getTotalWeight() - signalYield

  # Reporting the normalization
  normalizer.report()

  # Normalization of the variables
  normalizer.normalizeSample(signalSample)
  normalizer.normalizeSample(backgroundSample)

  # NEAT training
  chromosome.node_gene_type = genome.NodeGene  
  population.Population.evaluate = FitnessFunctionWrapper
  pop = population.Population()
  pop.epoch(int(set['number_generations']), report=True, save_best=False, checkpoint_interval = None)
  winner = pop.stats[0][-1]
  print 'Training: Number of evaluations: %d' % winner.id
  print 'Training: Best NN fitness: %0.2f' % winner.fitness

  # Save the best network
  file = open('%s/winner.dat' % set['directory'], 'w')
  pickle.dump(winner, file)
  file.close()
  # Save the best network
  file = open('%s/winner-fitness.txt' % set['directory'], 'w')
  file.write('%f' % winner.fitness)
  file.close()


# Funtion fitness wrapper 
def FitnessFunctionWrapper(population):
  global signalYield, signalSample, backgroundYield, backgroundSample
  print 'FitnessFunctionWrapper: Evaluating the population fitness ...'
  start = time.time()
  Common.NeatFitnessFunction(population, signalYield, signalSample, backgroundYield, backgroundSample)
  print 'FitnessFunctionWrapper: Evaluation complete in %0.1f minutes.' % ((time.time() - start)/60)


import sys
from optparse import OptionParser


# Declaration of main function
if __name__ == "__main__":

  usage = 'Usage: %s [options]' %sys.argv[0]
  parser = OptionParser(usage=usage)

  parser.add_option('-r', '--reco', dest='reco', help='Reco version.')
  parser.add_option('-l', '--lepton', dest='lepton', help='Lepton channel.')
  parser.add_option('-t', '--ntag', dest='ntag', help='Number of tags.')
  parser.add_option('-n', '--njet', dest='njet', help='Number of jets.')
  parser.add_option('-d', '--directory', dest='directory', help='Directory trainning.')
  parser.add_option('-m', '--number_generations', dest='number_generations', help='Number of generations.')

  (options, args) = parser.parse_args()

  Evaluate(options.__dict__)
