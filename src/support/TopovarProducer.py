#! /usr/bin/env python
# TopovarProducer.py
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Tree producer create trees with neat output as branch
#   I was implemented as external program to fix root memory leaking problems

import sys

# Enabling root in batch mode
sys.argv.append('-b')

import cPickle as pickle
from optparse import OptionParser

from neat.nn import nn_cpp as nn

from TopovarWriter import *
from VariableNormalizer import *

import Common


# Standard message print out
def message(msg):
  print 'TopovarProducer: %s' % msg


# Declaration of main function
if __name__ == "__main__":

  usage = 'Usage: %s [options]' %sys.argv[0]
  parser = OptionParser(usage=usage)
  parser.add_option('-c', '--combinations', dest='combinations', help='Provide those discriminator to be combined in the format key1:input1,...,keyn:inputn.')
  parser.add_option('-i', '--input', dest='input', help='Input topovar file.')
  parser.add_option('-o', '--output', dest='output', help='Output topovar file.')
  parser.add_option('-b', '--batch', action='store_true', dest='list', default=True, help='Set ROOT batch mode (default true).')
  
  (options, args) = parser.parse_args()
  
  message('Processing input: %s' % options.input)
  message('Processing output: %s' % options.output)

  # Collect all the inputs
  combinations = options.combinations.split(',')
    
  # Collection of neat nn
  nets = {}
  variables = {}
  normalizers = {}
    
  # Loop over the inputs
  for combination in combinations:
    
    message('Processing combination: %s' % combination)

    # Parsing the key and input
    parse = combination.split(':')

    # Checking the format
    if len(parse) != 2:
      message('Wrong combination format')
      sys.exit(1)      

    # Parsing key and input
    key = parse[0]
    input = parse[1]
      
    # Setting the indir directory
    indir = '%s/scratch/%s' % (
      Common.NeatDirectory, input
    )
    
    # Get channel winner network
    winner = pickle.load(open('%s/winner.info' % indir))
    
    # Collect the list of variables
    variables[key] = winner['variables']
    
    # Collect the net
    net = pickle.load(open('%s/%s/winner.dat' % (indir, winner['training'])))

    # Create phenotype from genome
    nets[key] = nn.create_ffphenotype(net)

    # Creating a variable normalizers
    normalizers[key] = VariableNormalizer(winner['variables'], winner['aves'], winner['stds'])

  # Create a topowriter for adding neat outputs
  topovars = None
  if len(variables) > 1:
    topovars = TopovarWriter(options.output, [], options.input)
  else:
    topovars = TopovarWriter(options.output, variables.itervalues().next(), options.input)

  # Add neat outputs
  for key in nets:
    topovars.addVariable(key, 'double')

  # Loop over the tree adding the neat output        
  for entry in xrange(topovars.getInTreeEntries()):
    if entry % 1000 == 0 and entry != 0:
      message('Reading %d events.' % entry)
    # Collection of neat discriminator
    neats = {}
    # Loop over all the nets  
    for key in nets:
      # Read one event and normalize
      event = topovars.read(entry, compress = True, variables = variables[key])
      normalizers[key].normalize(event)
      # Not strictly necessary in feedforward nets
      nets[key].flush()
      neats[key] = nets[key].sactivate(event[1:])[0]
    # Add to the tree
    topovars.fill(neats)
  # Write the events into the file
  topovars.write()
 
