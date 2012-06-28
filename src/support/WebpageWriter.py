# WebpageWriter
#
# Developers:
#   Victor Eduardo Bazterra 2010 (UIC)
#   Phillip Eller 2010 (ETH) 
#   Christfried Focke 2010 (ETH) 
#
# Descrition:
#   Writer html pages for control and profile plots

import Common


## Custom exception for processor
class WebpageWriterError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return self.value


## Writer html pages for control and profile plots
class WebpageWriter:

  ## Constructor
  def __init__(self, title, type, options={}):
    self.__buffer = ''
    self.__title = title
    self.__options = options
    allow = ['discriminators','profiles','limits','expected_limits']
    if type in allow:
      self.__type = type
    else:
      raise WebpageWriterError('Unknown webpage type.')


  ## Helper function
  def __write(self, string):
    self.__buffer = self.__buffer + string + '\n'
    
  
  # Page implementation
  def __page(self):
    self.__write('<html>')
    self.__header()
    self.__body()
    self.__write('<html>')


  ## Header implementation
  def __header(self):
    self.__write('<head>')
    self.__write('<title>%s</title>' % self.__title)
    self.__write('<link rel="stylesheet" type="text/css" href="http://www-d0.fnal.gov/Run2Physics/top/public/fall06/singletop/style.css">')
    self.__write('</head>')
    

  ## Body implementation
  def __body(self):
    self.__write('<body>')
    self.__write('<h1 align=center>%s</h1>' % self.__title)
    self.__write('<p align=center>')
    self.__table()
    self.__write('</p></body>')


  ## Table implementation    
  def __table(self):

    RecoVersions = Common.RecoVersions
    if type(RecoVersions) != list:
      RecoVersions = [Common.RecoVersions]

    Leptons = Common.Leptons
    if type(Leptons) != list:
      Leptons = [Common.Leptons]

    Ntags = Common.Ntags
    if type(Ntags) != list:
      Ntags = [Common.Ntags]

    Njets = Common.Njets
    if type(Njets) != list:
      Njets = [Common.Njets]

    Binning = Common.Binning
    if type(Binning) != list:
      Binning = [Common.Binning]
      
    if self.__type.endswith('limits'):
      Binning = Common.XSectionBinnings
      if type(Binning) != list:
        Binning = [Common.XSectionBinnings]

            
    for bin in Binning:
      # Bin title
      self.__write('<hr width=90\><p><h2>%s bins</h2></p>' % bin)
      # Create a table per reco and lepton channel
      for reco in RecoVersions:
        for lepton in Leptons:

          # Table title
          self.__write('<p><h2>Reco %s - %s - %s bins</h2></p>' % (reco, lepton, bin))
          self.__write('<p><table border=1 style="border-collapse: collapse; border: solid;">')
          self.__write('<tr>')
          self.__write('<th width=160>N_tags</th>')
          for njet in Njets:
            self.__write('<th width=160>%s</th>' % njet)
          self.__write('</tr>')

          for ntag in Ntags:
            self.__write('<tr align=center>')
            self.__write('<td><b>%s</b></td>' % ntag)

            for njet in Njets:
              file = ''

              if self.__type == 'discriminators':
                file = '%s_%s_%s_%s_%s' % (reco, lepton, ntag, njet, bin)
              elif self.__type == 'profiles':
                file = 'profiles_%s_%s_%s_%s_%s' % (reco, lepton, ntag, njet, bin)
              elif self.__type.endswith('limits'):
                dirname = ''
                if self.__type == 'expected_limits':
                  dirname = 'expected_limit_%s_%s_%s_%s_%s_%s_%s' % (
                    self.__options['signal'], reco, lepton, ntag, njet, bin, self.__options['systematic']
                  )
                  filename = 'expected_limit_%s_%s_%s_%s' % (
                    self.__options['signal'], reco, lepton, ntag
                  )
                else:
                  dirname = 'limit_%s_%s_%s_%s_%s_%s_%s' % (
                    self.__options['signal'], reco, lepton, ntag, njet, bin, self.__options['systematic']
                  )
                  filename = 'limit_%s_%s_%s_%s' % (
                    self.__options['signal'], reco, lepton, ntag
                  )
                file = '%s/%s' % (dirname, filename)
                
              self.__write('<td><a href="%s.eps"><img src="%s.png" width=310></a>' % (file, file))
            self.__write('</tr>')
          self.__write('</table></p>')


  ## Write the page in a file
  def write(self, filename):
    self.__page()
    file = open(filename, 'w')
    file.write(self.__buffer)
    file.close()
 