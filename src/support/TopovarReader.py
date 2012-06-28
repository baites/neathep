# TopovarReader 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Wrapper python class to a TChain object containing a group of topovar files. 

import copy, math, os, random, sys

from ROOT import TChain
from ROOT import TFile


## Dummy object hold an event
class Event: pass


## Custom exception for topovar reader
class TopovarReaderError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


## Minimum interface to create processors
class TopovarReader(object):

  ## Constructor (a variable list needs to be provided)
  def __init__(self, variables = [], filename = None):
    self.__chain = TChain('TopologicalVariables')
    # self.__chain.SetCacheSize()
    self.__filenames = []
    self.__variables = copy.copy(variables)
    self.__variables.insert(0, 'EventNumber')
    self.__variables.insert(1, 'EventWeight')
    self.__setActiveBranches()
    self.__sumWeights = None
    if filename: self.add(filename)


  ## Return list of variables read
  def getVariables(self):
    return self.__variables


  ## Get this list of files
  def getFilenames(self):
    return self.__filenames


  ## Get chain size
  def getEntries(self):
    return self.__chain.GetEntries()


  ## Add a file to pool
  def add(self, filename):
    if not os.path.exists(filename):
      raise TopovarReaderError('Missing file %s' % filename)
    self.__message('Adding file %s' % filename)
    self.__filenames.append(filename)
    self.__chain.Add(filename)


  ## Read a even in the chain  
  def read(self, entry, compress = False):
    # Check if the entry is in the chain
    if entry < 0 or entry >= self.__chain.GetEntries():
      raise TopovarReaderError('Entry out of range.')
    # Set the chain entry
    self.__chain.GetEntry(entry)
    # Check for compress format
    if compress:
      # Compact format return a list of variables
      event = []
      for variable in self.__variables:
        event.append(getattr(self.__chain, variable))
      return event
    else:
      # No compact format return event object
      event = Event()
      for variable in self.__variables:
        # Variable value is process first (Normalization, etc..)
        setattr(event, variable, getattr(self.__chain, variable))
      return event
  
  
  ## Return a list with the content of the whole sample
  def sample(self, compress = False):
    self.__message('Reading the whole sample in one step.')
    sample = []
    for entry in xrange(self.getEntries()):
      # Print number of event processed
      if entry % 5000 == 0 and entry != 0:
        self.__message('Reading %d events.' % entry)
      sample.append(self.read(entry, compress))
    return sample 


  ## Create a list of random events
  def randomSampling(self, size, compress=False):
    collection = []
    # Compute the sum of weights in the chain
    if not self.__sumWeights:
      self.__computeSumWeights()
    # Generating random entries
    self.__message('Selecting %d random events.' % size)
    entries = []
    for counter in xrange(size):
      # Select random entries proportional to weights
      weight = random.uniform(0, self.__sumWeights[-1])
      entries.append(self.__search(weight, self.__sumWeights))
    # Sorting the entries (ROOT is optimized for serial access)
    entries.sort()
    # Selecting the events
    counter = 0
    for entry in entries:
      if counter % 1000 == 0 and counter != 0: 
        self.__message('Selected %d events.' % counter)  
      # Read the event from the chain
      event = self.read(entry, compress)
      # Remove the weight from the event
      if compress:
        event = event[2:]
      else:
        delattr(event, 'EventNumber')
        delattr(event, 'EventWeight')
      # Adding to the collection
      collection.append(event)
      counter = counter + 1
    # Shuffle the final collection
    random.shuffle(collection)
    return collection
  
 
  ## Create and save a list of random events
  def saveRandomSampling(self, filename, size):
    collection = self.randomSampling(size, True)
    file = open(filename, 'w')
    file.write('/F:'.join(self.__variables[2:])+'\n')
    for event in collection:
      event = [str(data) for data in event]
      file.write(' '.join(event)+'\n')
    file.close()

  
  ## Auxiliary function for log
  def __message(self, msg):
    print '%s: %s' % (self.__class__.__name__, msg)
 

  ## Auxiliary function for setting up active branches
  def __setActiveBranches(self):
    self.__chain.SetBranchStatus('*', False)
    for variable in self.__variables:
      self.__chain.SetBranchStatus(variable, True)


  ## Auxiliary function for adding event weights
  def __computeSumWeights(self):
    # Setting sum of weight holder
    self.__sumWeights = []
    # Activating only event weight branch
    self.__chain.SetBranchStatus('*', False)
    self.__chain.SetBranchStatus('EventWeight', True)
    self.__chain.AddBranchToCache('EventWeight')
    # Loop over the chain
    entries = self.__chain.GetEntries()
    self.__message('Computing weight sums for %d events.' % entries)    
    for entry in xrange(entries):
      # Print number of event processed
      if entry % 5000 == 0 and entry != 0: 
        self.__message('Process %d events.' % entry)  
      # Set the chain entry
        self.__chain.GetEntry(entry)
      # Read the event weight
      if entry == 0:
        self.__sumWeights.append(self.__chain.EventWeight)
      else:
        self.__sumWeights.append(self.__sumWeights[-1] + self.__chain.EventWeight)
    self.__totalWeight = self.__sumWeights[-1]
    self.__message('Total yield %0.3f' % self.__totalWeight)
    self.__setActiveBranches()

      
  ## Auxiliary function for binary search events
  def __search(self, item, items):
    # First and last indexes in the list
    first = 0
    last = len(items) - 1
    found = False
    # Loop over binary search
    while (first <= last) and not found:
      middle = (first + last)/2
      if item < items[middle]:
        last = middle - 1
      elif item > items[middle]:
        first = middle + 1
      else:
        found = True
      if first > last:
        middle = first
        found = True
      if found: return middle
    # If item is not found
    return -1
 
