#! /usr/bin/env python
# NeatTrainer 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Run the training for each channel and for each 
#   combination of neat parameters

import sys

# Enabling root in batch mode
sys.argv.append('-b')

import commands, shutil, string

from neat.config import Config as NeatParameters

from Common import *
from Processor import *
from Util import *

import Neat
import Training


## Class the implements the training
class NeatTrainer(Processor):


  ## Constructor
  def __init__(self):
    # Call the constructor from parent class
    super(NeatTrainer,self).__init__()    
    # Job counter
    self.__counter = {}
    # Initializing allowed processor parameters
    self.defineParameter('input','Provides the input directory with neat variable selection.')
    self.defineParameter('output','Provides the output directory for training neat.')
    self.defineParameter('host','Host where the jobs are executed (default is local).')
    

  # Redefining start
  def start(self):
    # Running processor start
    super(NeatTrainer, self).start()
    # Overwrite the nproc parameter to 1 (no multiprocessing when submitting jobs)
    if self.getParameter('host', 'local') != 'local':
      self.setParameter('nproc', '1')
    # Read all the possible neat parameters
    self.__setNeatParameters(Neat)
    # Print the number of jobs to be produce
    self.message('A total of %d jobs will be run by the procesor, user have 5 second to cancel.' % self.getLoopSize())
    time.sleep(5)


  ## Process each channel
  def process(self, set):

    # Check the channel and update the counter
    channel = channelName(set)
    if channel not in self.__counter:
      self.__counter[channel] = 1
    else:
      self.__counter[channel] = self.__counter[channel] + 1

    self.message('Processing channel %s training %d' % (channel, self.__counter[channel]))

    # Setting the indir directory
    indir = '%s/scratch/%s/%s' % (
      Common.NeatDirectory, self.getParameter('input'), channel
    )

    # Creating output directory
    outdir = '%s/scratch/%s/Trainings/%s/Training%05d' % (
      Common.NeatDirectory, self.getParameter('output'), channel, self.__counter[channel]
    )

    # Check for output directory
    if not os.path.exists(outdir):
      os.makedirs(outdir)

    # Copy selected variables for running neat
    shutil.copyfile(
      '%s/%s' % (indir, Common.Selectvars), 
      '%s/%s' % (outdir, Common.Inputvars)
    )
      
    # Create neat configuration file from the template
    file = open ('%s/configs/Neat.template' % Common.NeatDirectory)
    template = string.Template(file.read())
    file.close()
    file = open ('%s/neat.config' % outdir, 'w')
    file.write(template.safe_substitute(set))
    file.close()

    # Run training
    set['directory'] = outdir
    set['number_generations'] = Common.NeatNumberGenerations
    host = self.getParameter('host','local')
    if host == 'local':
      Training.Evaluate(set)
    else:
      self.submitTraining(host, set)

  
  ## Prepare submission script and submit jobs to he clusters
  def submitTraining(self, host, set):
    self.message('Submitting training jobs to %s host.' % host)
    # Setup neat directory
    set['NeatDirectory'] = Common.NeatDirectory  
    # Create a script file to run the job
    file = open ('%s/support/wrappers/RunNeat.wrapper' % Common.NeatDirectory)
    template = string.Template(file.read())
    file.close()
    file = open ('%s/runneat.csh' % set['directory'], 'w')
    file.write(template.safe_substitute(set))
    file.close()
    if host == 'clued0':
      os.system('cd %s; cluesow -l cput=50:00:00 -l mem=1024mb runneat.csh' % set['directory'])
    elif host == 'cabsrv1':
      os.system('cd %s; qsub -koe -me -M $USER@fnal.gov -l nodes=1 -q sam_lo@d0cabsrv1 runneat.csh' % set['directory'])
    elif host == 'cabsrv2':
      os.system('cd %s; qsub -koe -me -M $USER@fnal.gov -l nodes=1 -q medium@d0cabsrv2 runneat.csh' % set['directory'])
    else:
      raise ProcessorError('Unkown host %s (possible options are clued0, cab).' % host)


  ## Set all the neat parameters as loops
  def __setNeatParameters(self, neat):
    for parameter in dir(neat):
      if not parameter.startswith('__'):
        try:
          getattr(NeatParameters, parameter)
        except AttributeError:
          raise ProcessorError('Unknown neat parameter %s.' % parameter)
        self.addLoop(parameter, getattr(neat, parameter))
    self.addLoop('try', range(1,Common.NeatNumberTries+1))

 
# Execute the interface
NeatTrainer().loop()
