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

#import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

def logmsg(level, msg):
    syslog.syslog(level, 'SW_PlotGenerator: %s' % msg)

def logdbg(msg):
    logmsg(syslog.LOG_DEBUG, msg)

def loginf(msg):
    logmsg(syslog.LOG_INFO, msg)

def logerr(msg):
    logmsg(syslog.LOG_ERR, 'ERROR: %s' % msg)

DEFAULT_CONF = {"AltTargetDir" : "/home/weewx/public_html/Testing/",
                "UseAltTargetDir" : True,
                "make_large_images" : True,
                "large_image_width" : 1200,
                "large_image_height" : 800}


class SW_PlotGenerator(weewx.reportengine.ReportGenerator):
    """
    This genorates plots in weewx. It is a drop in replacement for ImageGenerator. (Or it will be...)
    """

    def run(self):
        """
        This is called by weewx to make the plots
        """
        loginf(" run")
        self.GetConf()
        self.AddDefaultConf()
        self.MakePlots()



    
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
       
        # Super might provide 'HTML_ROOT'
        loginf("WEEWX_ROOT %s" %self.config_dict['WEEWX_ROOT'],)
        loginf("HTML_ROOT %s" %self.config_dict["StdReport"]['HTML_ROOT'])
        self.ImagesDir = os.path.join(self.config_dict['WEEWX_ROOT'],self.config_dict["StdReport"]['HTML_ROOT'])
        loginf("self.ImagesDir %s" %self.ImagesDir)
       
        
        loginf("GetConf Done")
        
    def AddDefaultConf(self):
        """
        This compairs the ImageGeneratorDict to defa
        """
        for key in DEFAULT_CONF:
            if not (key in self.ImageGeneratorDict):
                loginf("%s not in self.ImageGeneratorDict using DEFAULT_CONF" %key)
                self.ImageGeneratorDict[key] = DEFAULT_CONF[key]
        
        if self.ImageGeneratorDict.get("UseAltTargetDir"):
            self.ImagesDir =  self.ImageGeneratorDict.get("AltTargetDir")
            # TODO double check real dir etc
        
        
    def SetupPlot(self):
        loginf(" StartPlotting")
        figHolder, axHolder = plt.subplots()
        self.fig = figHolder
        self.ax = axHolder
    
    def MakePlots(self):
        """
        This takes the conf data produced by GetConf and loops over each plot to be made. The loop calls the correct subrotine for each plot. 
        
        Following https://matplotlib.org/gallery/api/agg_oo_sgskip.html#sphx-glr-gallery-api-agg-oo-sgskip-py
        """
        loginf(" MakePlots")
        # Loop over each time scale set and then over each plot in that timescale
        for TimeScaleOfPlot in self.ImageGeneratorDict.sections :
            for PlotTitle in self.ImageGeneratorDict[TimeScaleOfPlot].sections :
                loginf("Plotting %s : %s" %(TimeScaleOfPlot,PlotTitle))
                
                # Add the default settings at the top of ImageGenerator to this specific plot's dictionary
                plot_options = weeutil.weeutil.accumulateLeaves(self.ImageGeneratorDict[TimeScaleOfPlot][PlotTitle])
                
                # Call the approprate subroutine for the plot_type
                try:
                    GenFunction = getattr(self, 'Gen_' + plot_options.get("plot_type") + '_Plot')
                except (AttributeError) as e:
                    if plot_options.get("plot_type") is None:
                        loginf("AttributeError - MakePlots - No plot_type specified - There should be a default in [ImageGenerator]")
                    loginf("AttributeError - MakePlots - Cannot find function to handle, plot_type: %s" %plot_options.get("plot_type"))
                    logerr("AttributeError - MakePlots - Cannot find function to handle, plot_type: %s" %plot_options.get("plot_type"))
                    loginf(traceback.format_exc())
                    loginf(e)
                
                # TODO add error handeling
                # seporated from getattr call to avoid catching exceptions in the function itself
                GenFunction(plot_options,PlotTitle,TimeScaleOfPlot)
                
        loginf(" MakePlots fins")
        
        
    def Gen_line_Plot(self, plot_options,PlotTitle,TimeScaleOfPlot):
        """
        This creats a line plot_type. (One of three types supported in ImageGenerator)
        """
        loginf(" Gen_line_Plot")
        
        loginf("Gen_line_Plot: Build Plot")
        fig = Figure()
        FigureCanvas(fig)
        # We are making a single subplot
        ax = fig.add_subplot(111)
        
        #home = os.path.expanduser("~")
        FilePath = self.ImagesDir + PlotTitle + '.png'
        if not os.path.isdir(self.ImagesDir):
            loginf("Path Fail %s" %self.ImagesDir)
        loginf("Saving to %s" %FilePath)
        


# TODO handle windvec which comes in as a complex
        
        
        
        
        # Loop over each measurment to share the axis
        for MeasurmentName in self.ImageGeneratorDict[TimeScaleOfPlot][PlotTitle].sections:
            # First make a dictinary of all settings for this meansurment
            MeasurmentPlotOptions = weeutil.weeutil.accumulateLeaves(self.ImageGeneratorDict[TimeScaleOfPlot][PlotTitle][MeasurmentName])
            
            # Next see if the MeasurmentName is the same as the database variable or is 'data_type' set seporately in skin.conf
            MeasurmentNameDB = MeasurmentPlotOptions.get('data_type', MeasurmentName)
            
            # Look for aggregation type:
            aggregate_type = MeasurmentPlotOptions.get('aggregate_type')
            if aggregate_type in (None, '', 'None', 'none'):
                # No aggregation specified.
                aggregate_type = None
                aggregate_interval = None
            else :
                try:
                # Aggregation specified. Get the interval.
                    aggregate_interval = MeasurmentPlotOptions.as_int('aggregate_interval')
                except KeyError:
                    loginf("Gen_line_Plot: aggregate interval required for aggregate type %s" % aggregate_type)
                    loginf("Gen_line_Plot: line type %s skipped" % MeasurmentName)
                    return 

            
            # Setup for DB access and figur out the time axis
            binding = MeasurmentPlotOptions.get('data_binding')
            if binding is not None:
                loginf("Gen_line_Plot: binding %s " % binding)
            # TODO Handle None
            
            # Super provides db_binder
            archive = self.db_binder.get_manager(binding)
            
            # What time rage are we interested in
            # self.gen_ts from super
            plotgen_ts = self.gen_ts
            if not plotgen_ts:
                plotgen_ts = archive.lastGoodStamp()
                if not plotgen_ts:
                    plotgen_ts = time.time()
                    
            (minstamp, maxstamp, timeinc) = weeplot.utilities.scaletime(plotgen_ts - int(plot_options.get('time_length', 86400)), plotgen_ts)
            
            # Get the data from DB
            (start_vec_t, stop_vec_t, data_vec_t) = archive.getSqlVectors((minstamp, maxstamp), MeasurmentNameDB, aggregate_type=aggregate_type,aggregate_interval=aggregate_interval)
            
            # Deal with line 157, and later, from imagegenerator
            
            loginf(type(data_vec_t[1]))
            loginf(data_vec_t[1])
            loginf(type(data_vec_t[2]))
            loginf(data_vec_t[2])
            
            # Data goes in the plot
            ax.plot(start_vec_t[0], data_vec_t[0])
            

        #loginf(type(start_vec_t))
        #<class 'weewx.units.ValueTuple'>
        #loginf(type(start_vec_t[0]))
        #<type 'list'>
        #loginf(''.join(str(e) for e in start_vec_t[0]))
        #Mess of unix times
        
        #loginf(type(data_vec_t))
        #<class 'weewx.units.ValueTuple'>
        #loginf(type(data_vec_t[0]))
        #<type 'list'>
        #loginf(''.join(str(e) for e in data_vec_t[0]))
        # mess of temps
        

        
        
        
        
        #plt.axis([0, 6, 0, 20])
        fig.savefig(FilePath, dpi=None, facecolor='w', edgecolor='b',orientation='landscape', papertype=None, format=None,transparent=False, bbox_inches='tight', pad_inches=None,frameon=None)

    
    
    
    def Gen_bar_Plot(self, plot_options,PlotTitle,TimeScaleOfPlot):
        """
        This creats a bar plot_type. (One of three types supported in ImageGenerator)
        """
        pass
    
    def Gen_vector_Plot(self, plot_options,PlotTitle,TimeScaleOfPlot):
        """
        This creats a vector plot_type. (One of three types supported in ImageGenerator)
        """
        pass
    
    def Gen_dot_Plot(self, plot_options,PlotTitle,TimeScaleOfPlot):
        """
        This creats a dot plot_type. This does not connect the dots as in a line plot. Usefull for wind direction.
        """
        pass
    
    def Gen_windSplit_Plot(self, plot_options,PlotTitle,TimeScaleOfPlot):
        """
        This creats a windSplit plot_type. This is a line plot for wind speed above a dot plot of wind direction.
        """
        pass
    
    def Gen_lineTempDualLabel_Plot(self, plot_options,PlotTitle,TimeScaleOfPlot):
        """
        This creats a lineTempDualLabel plot_type. This is a line plot for tempriture with the standard unit on the left and 
        the opposit unit on the right (F or C).
        """
        pass
    
    def Gen_lineMultiUnit_Plot(self, plot_options,PlotTitle,TimeScaleOfPlot):
        """
        This creats a lineMultiUnit plot_type. This is a line plot with two different data types. The first data type will be given on the left axis 
        and the second type will be on the right. Usufuall for plotting relative humidity and dewpoint on the same plot.
        """
        pass
