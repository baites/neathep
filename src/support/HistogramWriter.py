# TopovarWriter 
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Wrapper python class to write histograms. 


from ROOT import TFile, TH1F


## Custom exception for topovar reader
class HistogramWriterError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return repr(self.value)


## Create a topovar tree
class HistogramWriter(object):

  ## Constructor 
  def __init__(self, filename, mode = 'recreate'):
    self.__file = TFile(filename, mode)    
    self.__histograms = {}


  ## Destructor
  def __del__(self):
    if self.__file:
      self.__file.Write()


  ## Booking 
  def book(self, name, nbins, xmin, xmax):
    if name in self.__histograms:
      raise HistogramWriterError('Duplicated histograms booking for name %s.' % name)
    self.__histograms[name] = TH1F(name, name, nbins, xmin, xmax)
    self.__histograms[name].Sumw2()
    
 
  ## Filling histogram
  def fill(self, value, weight, name = None):
    if len(self.__histograms) == 0:
      raise HistogramWriterError('Fill impossible, no histogram has been booked.')
    if name:
      if not name in self.__histograms:
        raise HistogramWriterError('No histograms booked with name %s.' % name)    
      self.__histograms[name].Fill(value, weight)
    else:
      for name in self.__histograms:
        self.__histograms[name].Fill(value, weight)
          