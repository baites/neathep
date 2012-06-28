# TopovarWriter 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Wrapper python class to create topovar root files. 

import array, copy, math, os, random, sys

from ROOT import TFile, TTree


## Dummy object hold an event
class Event: pass


## Custom exception for topovar reader
class TopovarWriterError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


## Create a topovar tree
class TopovarWriter(object):


  ## Constructor 
  def __init__(self, outfile, variables = [], infile = None):
    # Default values
    self.__intree = None
    self.__outtree = None
    self.__holder = {}
    self.__variables = copy.copy(variables)
    self.__outfile = TFile(outfile, 'recreate')
    # Clone a tree if a infile name is passed
    if infile:
      self.__infile = TFile(infile)
      self.__intree = self.__infile.Get('TopologicalVariables')
      self.__setActiveBranches()
      # Swiching to output file
      self.__outfile.cd()
      self.__outtree = self.__intree.CloneTree(0)
    else:
      # Swiching to output file
      self.__outfile.cd()
      self.__outtree = TTree('TopologicalVariables','TopologicalVariables')


  ## Destructor
  def __del__(self):
    if self.__infile:
      self.__infile.Close()
    if self.__outfile:
      self.__outfile.Close()


  ## Return list of variables
  def getVariables(self):
    return self.__variables


  ## Return list of variables to be added
  def getAddedVariables(self):
    return self.__holder.keys()


  ## Get size of the intree
  def getInTreeEntries(self):
    if not self.__intree:
      raise TopovarWriterError('No input tree exist.')
    return self.__intree.GetEntries()


  ## Get size of the outtree
  def getOutTreeEntries(self):
    return self.__outtree.GetEntries()


  ## Read a even in the chain  
  def read(self, entry, compress = False, variables = None):
    # Set variable list (by default uses the initial variable list)
    # This allow to select a subset of the initial variable list
    if not variables:
      variables = self.__variables
    else:
      variables = copy.deepcopy(variables)
      variables.insert(0,'EventNumber')
      variables.insert(1,'EventWeight')
    # Check for the intree exist
    if not self.__intree:
      raise TopovarWriterError('No input tree exist.')
    # Check if the entry is in the chain
    if entry < 0 or entry >= self.__intree.GetEntries():
      raise TopovarWriterError('Entry out of range of the in tree.')
    # Set the chain entry
    self.__intree.GetEntry(entry)
    # Check for compress format
    if compress:
      # Compact format return a list of variables
      event = []
      for variable in variables:
        event.append(getattr(self.__intree, variable))
      return event
    else:
      # No compact format return event object
      event = Event()
      for variable in variables:
        # Variable value is process first (Normalization, etc..)
        setattr(event, variable, getattr(self.__intree, variable))
      return event

    
  ## Add a new topovar to the tree
  def addVariable(self, variable, type, default = -999):
    # Check for pre-existent variables
    update = False
    if variable in self.__variables:
      self.__message('Updating a pre-existent variable.')
      update = True
    # Adding variable to the tree (only int and float are supported)
    if type == 'int':
      self.__holder[variable] = array.array('i', [default])
      if not update:
        self.__outtree.Branch(variable, self.__holder[variable], '%s/I' % variable)
      else:
        self.__outtree.SetBranchAddress(variable, self.__holder[variable])
    elif type == 'double':
      self.__holder[variable] = array.array('d', [default])
      if not update:
        self.__outtree.Branch(variable, self.__holder[variable], '%s/D' % variable)
      else:
        self.__outtree.SetBranchAddress(variable, self.__holder[variable])
    else:
      raise TopovarWriterError('Unsupported type, topovar can only be int or double.') 


  ## Fill the tree
  def fill(self, *args, **kwargs):
    # Reading of the values
    values = {}
    if len(args) > 1:
      raise TopovarWriterError('Too many positional arguments.')
    if args:
      values.update(args[0])
    values.update(kwargs)
    # Setup all the variable values
    for key in values:
      # Check if the variable was added
      if not key in self.__holder:
        raise TopovarWriterError('The variable %s was not added to the tree.' % key)
      self.__holder[key][0] = values[key]
    # Fill the tree
    self.__outtree.Fill()

  def __setActiveBranches(self):
    # Set only selected variables
    if len(self.__variables) != 0:
      self.__variables.insert(0, 'EventNumber')
      self.__variables.insert(1, 'EventWeight')     
      self.__intree.SetBranchStatus('*', False)
      for variable in self.__variables:
        self.__intree.SetBranchStatus(variable, True)
    else:
    # Set all the variables
      self.__intree.SetBranchStatus('*', True)
      branches = self.__intree.GetListOfBranches()
      for i in xrange(branches.GetEntries()):
        self.__variables.append(branches[i].GetName())


  ## Write the tree to the file
  def write(self):
    self.__outtree.Write()

  
  ## Auxiliary function for log
  def __message(self, msg):
    print '%s: %s' % (self.__class__.__name__, msg)
  
