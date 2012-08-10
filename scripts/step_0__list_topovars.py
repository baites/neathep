#! /usr/bin/env python
# TopovarLists 
#
# Developers:
#   Victor Eduardo Bazterra 2012 (UIC)
#   Phillip Eller 2010 (ETH) 
#
# Descrition:
#   Read the collection of topovars of each channel

import sys

# Enabling root in batch mode
sys.argv.append('-b')

import commands, shutil

from Processor import *
from Util import *

from ROOT import TFile

## Class the implements the interface
class TopovarLists(Processor):


  ## Constructor
  def __init__(self):
    # Call the constructor from parent class
    super(TopovarLists,self).__init__()
    # Initializing allowed processor parameters
    self.defineParameter('output', 'Provides the output directory for variable lists.')
    

  ## Process each channel
  def process(self, set):

    channel = channelName(set)    
    self.message('Processing channel %s' % channel)

    # Creating output directory
    outdir = '%s/scratch/%s/%s' % (
      Common.NeatDirectory, self.getParameter('output'), channelName(set)
    )

    # Check for output directory
    if not os.path.exists(outdir):
      os.makedirs(outdir)
 
    # Set file name of the data sample
    infile = '%s/%s/%s.root' % (
        Common.SampleLocation, Common.YieldSample, channelName(set, Common.Data)
    )

    # Set output file name 
    outfile = '%s/%s' % (
        outdir, Common.Selectvars
    )

    # Open data file and read the tree
    infile = TFile(infile)
    tree = infile.Get(Common.Inputtree)

    # Open a file to write the topvars
    outfile = open(outfile, 'w')
    
    # Write the list of variables that are not blacklisted
    for branch in tree.GetListOfBranches():
      blacklisted = False
      for key in Common.TopovarBlackList:
        if branch.GetName().find(key) != -1:
            blacklisted = True
            break
      if not blacklisted:
        outfile.write('%s\n' % branch.GetName())
          
    
# Execute the interface
TopovarLists().loop()
