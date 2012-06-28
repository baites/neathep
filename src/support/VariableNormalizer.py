# VariableNormalizer 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Normalize a group variables from the samples. 


import copy, math
import pickle

class VariableNormalizer:

  ## Constructor
  def __init__(self, variables, aves=None, stds=None):
    self.__variables = copy.copy(variables)
    self.__variables.insert(0, 'EventNumber')
    self.__variables.insert(1, 'EventWeight')    
    self.reset(aves,stds)

  
  ## Call overwrite to normalize sample
  def __call__(self, variable):
    ave = self.__average[variable]
    std = math.sqrt(self.__sqaverage[variable] - self.__average[variable]**2)
    return ave, std
    

  ## Report the variable average and std
  def report(self):
    for variable in self.__variables[2:]:
      ave, std = self(variable)
      self.__message('Variable %s: %0.2f +- %0.2f' % (variable, ave, std))


  ## Normalize an event
  def normalize(self, event):
    for i in xrange(2,len(self.__variables)):
      ave, std = self(self.__variables[i])
      event[i] = (event[i] - ave)/std
                

  ## Normalize a sample
  def normalizeSample(self, sample):
    self.__message('Normalizing variables in sample.')
    for event in sample:
      self.normalize(event)


  ## Reset holder of the ave and std
  def reset(self, aves=None, stds=None):
    self.__sumweight = None
    if not aves:
      self.__average = {}
      self.__sqaverage = {}
      return
    assert stds != None
    self.__average = aves
    self.__sqaverage = {}
    for variable in self.__variables[2:]:
      self.__sqaverage[variable] = aves[variable]**2 + stds[variable]**2


  ## Return list of variables read
  def getVariables(self):
    return self.__variables


  ## Get the total weight
  def getTotalWeight(self):
    if self.__sumweight:
      return self.__sumweight
    return 0.

    
  ## Add a sample (in topovar reader compact format) 
  def add(self, sample):

    # Primitive set of maps
    A = {}; B = {}; W = 0
    OldA = self.__average
    OldB = self.__sqaverage
    OldW = self.__sumweight
    variables = self.__variables
    
    self.__message('Computing average and std for each variable in %d events.' % len(sample))    

    # Computing weighted average iteractevily
    for event in sample:
      if not OldW:
        W = event[1]
        for i in xrange(2, len(self.__variables)):
          A[variables[i]] = event[i]
          B[variables[i]] = event[i]**2  
      else:
        weight = event[1]
        for i in xrange(2, len(self.__variables)):
          value = event[i]
          A[variables[i]] = (OldW*OldA[variables[i]] + weight*value)/(OldW+weight) 
          B[variables[i]] = (OldW*OldB[variables[i]] + weight*value**2)/(OldW+weight)
        W = OldW+weight
      OldA = copy.deepcopy(A); OldB = copy.deepcopy(B); OldW = W
    
    # Save the result
    self.__average = A
    self.__sqaverage = B
    self.__sumweight = W
      

  ## Auxiliary function for log
  def __message(self, msg):
    print '%s: %s' % (self.__class__.__name__, msg)

