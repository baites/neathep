
from exceptions import Exception

# Access to global objects
import ROOT
# Enabling plain style
ROOT.gROOT.SetStyle("Plain")
# Removing the statbox
ROOT.gStyle.SetOptStat(000000000)
# Removing histogram titles
ROOT.gStyle.SetOptTitle(0)

# Dummy class for xcheck configuration
class XCheckNtags: pass
class XCheckNjets: pass
class CombinedXCheckNtags: pass
class CombinedXCheckNjets: pass


## Custom exception for processor
class UtilError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return self.value


# Auxiliary function for reading tmva output
def searchInFile(file, key):
  string = file.readline()
  while string and string.find(key) == -1:
    string = file.readline()
  if not string:
    raise UtilError('Corrupted tmva output file.')


# Reading tmva variables and their importance
def ReadRuleFitImportance(filename):
  file = open(filename)
  searchInFile(file, 'Training finished')
  searchInFile(file, 'Importance')
  file.readline()
  line = file.readline()
  table = []
  while line.find('-----') == -1:
    fields = line.split(':')
    name = fields[2]
    importance = float(fields[3])
    table.append((name[1:], importance))
    line = file.readline()
  file.close()
  return table


# Improving pickle for member functions
# From http://bytes.com/topic/python/answers/552476-why-cant-you-pickle-instancemethods
def _pickle_method(method):
  func_name = method.im_func.__name__
  obj = method.im_self
  cls = method.im_class
  return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
  for cls in cls.mro():
    try:
      func = cls.__dict__[func_name]
    except KeyError:
      pass
    else:
      break
  return func.__get__(obj, cls)

import copy_reg, types
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)

