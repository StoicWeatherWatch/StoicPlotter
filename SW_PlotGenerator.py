# Copyright (C) 2018 - All Rights Reserved
# Stoic Plot Generator
# SW_PlotGenerator
# Version 0.0.1
# 2018-04-24


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

    def run(self):
        """
        This is called by weewx to make the plots
        """

