# FitnessFunctions.py
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Implements the different fitness functions for neat

from ROOT import Math

from neat.nn import nn_cpp as nn


## Base class for a fitness function
class FitnessFunction(object):

  #3 Constructor and variable initialization 
  def __init__(self, args):
    for arg in args:
      setattr(self, arg, args[arg])

  ## Function call redirection
  def __call__(population, signalYield, signalSample, backgroundYield, backgroundSample):
    pass

  ## Generic message from the processor 
  def message(self, msg):
    print '%s: %s' % (self.__class__.__name__, msg)


def setDefault(args, arg, value):
  if not arg in args: args[arg] = value 
       

## Event Euclidean distance (n-norm)
class EventEuclideanDistance(FitnessFunction):

  # Constructor
  def __init__(self, **args):
    # Default values
    setDefault(args, 'norm', 2.)
    # Call the constructor from parent class
    super(EventEuclideanDistance,self).__init__(args)


  # Implementation
  def __call__(self, population, signalYield, signalSample, backgroundYield, backgroundSample):
    # Loop over the chromosomes in the population 
    for genome in population:
  
      # Get a nn describe by the chromosome (feed foreward)
      net = nn.create_ffphenotype(genome)   
      error = 0.0
      # Loop over the events
      for event in signalSample:
        # Extract variables and weight
        variables = event[1:]
        weight = event[0]/signalYield
        # Not strictly necessary in feedforward nets
        net.flush()
        # Computing the error
        error = error + weight*(1 - net.sactivate(variables)[0])**self.norm

      # Loop over the events
      for event in backgroundSample:
        # Extract variables and weight
        variables = event[1:]
        weight = event[0]/backgroundYield
        # Not strictly necessary in feedforward nets
        net.flush()
        # Computing the error
        error = error + weight*(net.sactivate(variables)[0])**self.norm
    
      # Set the fitness value to the chomosome
      genome.fitness = 1 - Math.pow(error/2, 1./self.norm)
    

import random, math
from ROOT import Math, TH1F, TRandom3


## SchwienhorstEllerMetric was developed withing BDT and NEAT
class SchwienhorstEllerMetric(FitnessFunction):

  # Constructor
  def __init__(self, **args):
    # Default values
    setDefault(args, 'nbins', 25)
    # Call the constructor from parent class
    super(SchwienhorstEllerMetric,self).__init__(args)


  # Implementation
  def __call__(self, population, signalYield, signalSample, backgroundYield, backgroundSample):

    # Histogram holders
    signalHistogram = TH1F('signalHistogram', 'signal', self.nbins, 0, 1)
    backgroundHistogram = TH1F('backgroundHistogram', 'background', self.nbins, 0, 1)

    # Loop over the chromosomes in the population 
    for genome in population:
  
      # Reset histograms
      signalHistogram.Reset()
      backgroundHistogram.Reset()

      # Get a nn describe by the chromosome (feed foreward)
      net = nn.create_ffphenotype(genome)   

      # Loop over the events creating signal histogram
      for event in signalSample:
        # Extract variables and weight
        variables = event[1:]
        weight = event[0]
        # Not strictly necessary in feedforward nets
        net.flush()
        # Net output
        output = net.sactivate(variables)[0]
        # Filling histograms
        signalHistogram.Fill(output, weight)
            
      # Loop over the events creating background histogram
      for event in backgroundSample:
        # Extract variables and weight
        variables = event[1:]
        weight = event[0]
        # Not strictly necessary in feedforward nets
        net.flush()
        # Net output
        output = net.sactivate(variables)[0]
        # Filling histograms
        backgroundHistogram.Fill(output, weight)
    
      fitness = 0
  
      # Computing fitness
      for bin in xrange(1,signalHistogram.GetNbinsX()+1):
        signal = signalHistogram.GetBinContent(bin)
        background = backgroundHistogram.GetBinContent(bin)
        total = signal + background
        if total > 0:
          fitness = fitness + signal**2/(signal+background)

      # Adding fitness to genome
      genome.fitness = Math.sqrt(fitness)



## Z-score base on the weighted Stouffer's Z-score 
## method for combining significances
class ZScore(FitnessFunction):

  # Constructor
  def __init__(self, **args):
    # Default values
    setDefault(args, 'error', 0.01)
    setDefault(args, 'nbins', 25)
    setDefault(args, 'minz', -10.0)
    setDefault(args, 'mpoints', 1000)
    setDefault(args, 'weight', linear)
    # Call the constructor from parent class
    super(ZScore,self).__init__(args)


  # Implementation
  def __call__(self, population, signalYield, signalSample, backgroundYield, backgroundSample):

    # Histogram holders
    signalHistogram = TH1F('signalHistogram', 'signal', self.nbins, 0, 1)
    backgroundHistogram = TH1F('backgroundHistogram', 'background', self.nbins, 0, 1)

    # Loop over the chromosomes in the population 
    for genome in population:
  
      # Reset histograms
      signalHistogram.Reset()
      backgroundHistogram.Reset()

      # Get a nn describe by the chromosome (feed foreward)
      net = nn.create_ffphenotype(genome)   

      # Loop over the events creating signal histogram
      for event in signalSample:
        # Extract variables and weight
        variables = event[1:]
        weight = event[0]
        # Not strictly necessary in feedforward nets
        net.flush()
        # Net output
        output = net.sactivate(variables)[0]
        # Filling histograms
        signalHistogram.Fill(output, weight)

      # Signal overall normalization scale
      signalScale = signalYield/len(signalSample)
            
      # Loop over the events creating background histogram
      for event in backgroundSample:
        # Extract variables and weight
        variables = event[1:]
        weight = event[0]
        # Not strictly necessary in feedforward nets
        net.flush()
        # Net output
        output = net.sactivate(variables)[0]
        # Filling histograms
        backgroundHistogram.Fill(output, weight)

      # Background overall normalization scale
      backgroundScale = backgroundYield/len(backgroundSample)
  
      # Random generators
      rcount = TRandom3(int(random.uniform(0,65535)))
      rsignal = TRandom3(int(random.uniform(0,65535)))
      rbackground = TRandom3(int(random.uniform(0,65535)))

      zscore = 0.; sqweight = 0.
  
      # Computing weighted z-score
      for bin in xrange(1,signalHistogram.GetNbinsX()+1):

        newz = 0.; oldz = 0.

        # Computing the zvalue per bin
        for point in xrange(1,self.mpoints+1):
          # Sample background
          background = Math.gamma_quantile(rbackground.Uniform(), 
            (backgroundHistogram.GetBinContent(bin)/backgroundScale)+1., backgroundScale
          )
          # Background larger that zero
          if background > 0.:
            # Sampling signal
            signal = Math.gamma_quantile(rsignal.Uniform(),
              (signalHistogram.GetBinContent(bin)/signalScale)+1., signalScale
            )
            # Sampling count
            count = rcount.Poisson(signal+background)
            # Computing pvalue
            pvalue = Math.poisson_cdf_c(count,background) + Math.poisson_pdf(count,background)
            # Computing zvalue
            zvalue = self.minz
            if pvalue < 1.0: zvalue = Math.normal_quantile_c(pvalue,1)
            # zvalue iterative average 
            newz = (zvalue + (point - 1)*oldz)/point
            # Computing relative difference
            error = math.fabs((newz - oldz)/newz)
            # Convergency criteria
            if error < self.error: break
            # Updating oldz
            oldz = newz  
            if point == self.mpoints:
              self.message('Warning reach maximum number of integration %s points.' % point)

        weight = self.weight(signalHistogram.GetBinCenter(bin))
        zscore = zscore + weight * newz
        sqweight = sqweight + weight**2
        
      # Fitness function is zscore transform back to 1 - pvalue
      # Set the fitness value to the chomosome
      genome.fitness = 1. - Math.normal_cdf_c(zscore/Math.sqrt(sqweight))


## Weighting functions
def ConstantWeighting(x):
  return 1

def LinearWeighting(x):
  return x

