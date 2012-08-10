# Base class to create a processor. 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   A processor will iterate over all the channels
#   applying the function process.

import copy, os, sys, time

from multiprocessing import Pool

import Common

## Custom exception for processor
class ProcessorError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    postfix = 'Use --info for more information.'
    self.value = '%s\n%s' % (self.value, postfix)
    return self.value


## Minimum interface to create processors
class Processor(object):


  ## Constructor
  def __init__(self):

    # Basic setup 
    self.__loopsets = []    
    self.__parameters = {}
    self.__parameterInfos = []
    # Define info parameter
    self.defineParameter('info', 'Print options.')
    self.defineParameter('nproc', 'Number of worker processors (default 1).')


  ## Set a list of options to be looped 
  def addLoop(self, key, values):
    if type(values) != list:
      values = [values]
    if len(values) > 0:
      self.__loopsets = combinedSets(self.__loopsets, { key:values })

 
  ## Get the loop size
  def getLoopSize(self): 
    return len(self.__loopsets)

 
  ## Set a Processor parameter
  def setParameter(self, key, value):
    for info in self.__parameterInfos:
      if key == info[0]:
        self.__parameters[key] = value
        return
    raise ProcessorError('The parameter %s is not defined.' % key)
    

  ## Set parameter info
  def defineParameter(self, key, info):
    self.__parameterInfos.append([key, info])


  ## Get a Processor parameter
  def getParameter(self, key, default=None):
    if key not in self.__parameters:
      if default != None: 
        return default
      raise ProcessorError('Missing parameter \"%s\"' % key)
    return self.__parameters[key]
    
  
  ## Check if parameter exists
  def isParameter(self, key):
    return key in self.__parameters


  ## Process wrapper to catch KeyboardInterrupt 
  def wrapper(self, set):
    try:
      sys.stdout = open('%s/logs/%s-%s.log' % (Common.NeatDirectory, self.__class__.__name__, os.getpid()), 'a', 5)
      sys.stderr = sys.stdout
      self.process(set)
      sys.stdout.flush()
    except KeyboardInterrupt:
      self.message('Terminating by user request.')
      return
      

  ## Function call before starting looping
  def start(self):
    # Adding process loops
    self.addLoop('prefix', Common.Prefixes)
    self.addLoop('channel', Common.Channels)
    self.addLoop('postfix', Common.Postfixes) 

  ## Function call at the end of processing
  def end(self):
    pass

  ## Loop over all the loopsets
  def loop(self, argv = sys.argv):
    # Parse arguments
    self.parse(argv)
    # Check for help option
    if self.isParameter('info'):
      self.info()
      return
    # Call start function
    self.start()
    # Number of processors
    nproc = int(self.getParameter('nproc', '1')) 
    # Run in multiprocessing is requested
    if nproc > 1:
      # Creates the log directory is needed
      if not os.path.exists('%s/logs' % Common.NeatDirectory):
        os.makedirs('%s/logs' % Common.NeatDirectory)
      # Create a pool of workers
      pool = Pool(processes = nproc)
      try:
        # Loop over the channels  
        for set in self.__loopsets:
          pool.apply_async(self.wrapper, (set,))
          time.sleep(1)
        pool.close(); pool.join()
      except KeyboardInterrupt:
        pool.terminate(); pool.join()
    else:
      # Run the process with multiprocessing
      for set in self.__loopsets:      
        self.process(set)
    # Call end function
    self.end()

      
  ## Generic message from the processor 
  def message(self, msg):
    print '%s: %s' % (self.__class__.__name__, msg) 

  
  ## Message for providing information
  def info(self):
    print '%s options are :' % self.__class__.__name__
    for info in self.__parameterInfos:
      print '  --%s: %s' % (info[0], info[1])


  def parse(self, argv):
    # Add the parameters from argv
    for arg in argv[1:]:
      # Check for illegal arguments
      if not arg.startswith('--'):
        # Only tolerated argument is root batch mode
        if arg == '-b': continue
        raise ProcessorError("Wrong parameter format it should be --{key}={value}")
      if arg.find('=') == -1:
        self.setParameter(arg[2:],True)
      else:
        arg = arg.split('=')
        self.setParameter(arg[0][2:],arg[1])


## Create a combinatorial dictionary
def combinedSets(leftSet, rightSet):
  combination = []
  if len(leftSet) == 0:
    for rightkey, rightvalue in rightSet.iteritems():
      for relement in rightvalue:
        combination.append({ rightkey:relement })    
  else:
    for leftElement in leftSet:
      for rightkey, rightvalue in rightSet.iteritems():
        for relement in rightvalue:
          element = copy.deepcopy(leftElement)
          element.update({ rightkey:relement })
          combination.append(element)
  return combination
          
