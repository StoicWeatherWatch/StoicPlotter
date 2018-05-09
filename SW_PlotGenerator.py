# Copyright (C) 2018 - All Rights Reserved
# Stoic Plot Generator
# SW_PlotGenerator
# Version 0.0.1
# 2018-04-24

# Each input is a key value pair from skin.conf. The key is a function name which is called with the value. 
# using the object oriented api.
# https://matplotlib.org/tutorials/introductory/lifecycle.html


from __future__ import with_statement
import time
import datetime
import syslog
import traceback
import os.path

#import weeplot.genplot
import weeplot.utilities
import weeutil.weeutil
import weewx.reportengine
import weewx.units
from weeutil.weeutil import to_bool, to_int, to_float
from weewx.units import ValueTuple

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def logmsg(level, msg):
    syslog.syslog(level, 'SW_PlotGenerator: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, 'ERROR: %s' % msg)


class SW_PlotGenerator(weewx.reportengine.ReportGenerator):
    """
    This genorates plots in weewx. It is a drop in replacement for ImageGenerator.
    """

    def run(self):
        """
        This is called by weewx to make the plots
        """
        loginf(" run")
        self.GetConf()
        self.StartPlotting()
        self.Gen_line_Plot()

    
    def GetConf(self):
        loginf(" GetConf")
        self.ImageGeneratorDict = self.skin_dict['ImageGenerator']
        self.PlotTitlesDict = self.skin_dict.get('Labels', {}).get('Generic', {})
        self.UnitFormatter  = weewx.units.Formatter.fromSkinDict(self.skin_dict)
        self.UnitConverter  = weewx.units.Converter.fromSkinDict(self.skin_dict)
        # determine how much logging is desired
        # TODO Limit logging when  self.LogSuccess is False
        self.LogSuccess = to_bool(self.ImageGeneratorDict.get('log_success', True))
        # ensure that we are in a consistent right location
        os.chdir(os.path.join(self.config_dict['WEEWX_ROOT'],
                              self.skin_dict['SKIN_ROOT'],
                              self.skin_dict['skin']))
        
        #loginf("Using dri %s" %os.path.join(self.config_dict['WEEWX_ROOT'],
        #                      self.skin_dict['SKIN_ROOT'],
       #                       self.skin_dict['skin']))
        
        loginf("GetConf Done")
        
    def StartPlotting(self):
        loginf(" StartPlotting")
        figHolder, axHolder = plt.subplots()
        self.fig = figHolder
        self.ax = axHolder
        
        
        
    def Gen_line_Plot(self):
        """
        This creats a line plot_type. (One of three types supported in ImageGenerator)
        """
        loginf(" Gen_line_Plot")
        home = os.path.expanduser("~")
        FilePath = home+'/New.png'
        loginf("Saving to %s" %FilePath)
        
        self.ax.plot([1,2,3,4], [1,4,9,16])
        #plt.axis([0, 6, 0, 20])
        self.fig.savefig(FilePath, dpi=None, facecolor='w', edgecolor='b',orientation='landscape', papertype=None, format=None,transparent=False, bbox_inches='tight', pad_inches=None,frameon=None)

    
    
    
    def Gen_bar_Plot(self):
        """
        This creats a bar plot_type. (One of three types supported in ImageGenerator)
        """
        pass
    
    def Gen_vector_Plot(self):
        """
        This creats a vector plot_type. (One of three types supported in ImageGenerator)
        """
        pass
    
    def Gen_dot_Plot(self):
        """
        This creats a dot plot_type. This does not connect the dots as in a line plot. Usefull for wind direction.
        """
        pass
    
    def Gen_windSplit_Plot(self):
        """
        This creats a windSplit plot_type. This is a line plot for wind speed above a dot plot of wind direction.
        """
        pass
    
    def Gen_lineTempDualLabel_Plot(self):
        """
        This creats a lineTempDualLabel plot_type. This is a line plot for tempriture with the standard unit on the left and 
        the opposit unit on the right (F or C).
        """
        pass
    
    def Gen_lineMultiUnit_Plot(self):
        """
        This creats a lineMultiUnit plot_type. This is a line plot with two different data types. The first data type will be given on the left axis 
        and the second type will be on the right. Usufuall for plotting relative humidity and dewpoint on the same plot.
        """
        pass
