"""
    **************************************************************************
    |                                                                        |
    |                       Parse CSV File Version 1.0                       |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    |                                                                        |
    **************************************************************************
    | Author: Rob Lyon                                                       |
    | Email : robert.lyon@manchester.ac.uk                                   |
    | web   : www.scienceguyrob.com                                          |
    **************************************************************************
    | Required Command Line Arguments:                                       |
    |                                                                        |
    | -a (string) full path to a parsed ATNF pulsar catalog database file.   |
    |                                                                        |
    **************************************************************************
    | Optional Command Line Arguments:                                       |
    |                                                                        |
    | -v (boolean) verbose debugging flag.                                   |
    |                                                                        |
    **************************************************************************
    | License:                                                               |
    |                                                                        |
    | Code made available under the GPLv3 (GNU General Public License), that |
    | allows you to copy, modify and redistribute the code as you see fit    |
    | (http://www.gnu.org/copyleft/gpl.html). Though a mention to the        |
    | original author using the citation above in derivative works, would be |
    | very much appreciated.                                                 |
    **************************************************************************
"""

# Command Line processing Imports:
from optparse import OptionParser

import os, sys

# Numpy Imports:
from numpy import ceil
from numpy import log
from numpy import mean
from numpy import random
from numpy import median

import numpy as np

import matplotlib.pyplot as plt


# Scipy Imports:
from scipy import std
from scipy import stats
from scipy import arange

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class PlotCSVData:
    """

    """

    # ******************************
    #
    # MAIN METHOD AND ENTRY POINT.
    #
    # ******************************

    def main(self,argv=None):
        """
        Main entry point for the Application. Processes command line
        input and begins creating the features.

        """

        # ****************************************
        #         Execution information
        # ****************************************

        print(__doc__)

        # ****************************************
        #    Command line argument processing
        # ****************************************

        # Python 2.4 argument processing.
        parser = OptionParser()

        # REQUIRED ARGUMENTS
        parser.add_option("-a", action="store", dest="csvPath",help='Path to a csv file.',default="")

        # OPTIONAL ARGUMENTS
        parser.add_option("-v", action="store_true", dest="verbose",help='Verbose debugging flag (optional).',default=False)

        (args,options) = parser.parse_args()# @UnusedVariable : Tells Eclipse IDE to ignore warning.

        # Update variables with command line parameters.
        self.verbose        = args.verbose
        self.csvPath = args.csvPath

        # ****************************************
        #   Print command line arguments & Run
        # ****************************************

        print "\n\t**************************"
        print "\t| Command Line Arguments |"
        print "\t**************************"
        print "\tDebug:",self.verbose
        print "\tParsed CSV file path:",self.csvPath

        # Check arguments for validity...
        if(os.path.isfile(self.csvPath) == False):
            print "\n\tYou must supply a valid csv file via the -a flag."
            sys.exit()

        # Now we know the input files exist...

        # Read parsed pulsar catalog file, extract useful variables:
        # Period, Frequency, DM, pulse width
        self.csvFile = open(self.csvPath,'r') # Read only access

        # ****************************************
        #        File parsing section
        # ****************************************

        # variables for data
        NAMES         = []
        GLS           = []
        GBS           = []
        P0            = []
        P1            = []
        F0            = []
        DM            = []
        BINARY        = []
        BINARY_PERIOD = []
        SemiMajor     = []
        BINCOMP       = []
        DIST          = []
        DIST_DM       = []
        AGE           = []
        EDOT          = []
        PMTOT         = []

        for line in self.csvFile.readlines():

            components = line.replace("*","NaN").rstrip('\n').split(",")

            if ( line.startswith("#,NAME")):
                # Ingore header
                pass

            else:

                NAMES.append(components[1])
                GLS.append(float(components[2]))
                GBS.append(float(components[3]))
                P0.append(float(components[4]))
                P1.append(float(components[5]))
                F0.append(float(components[6]))
                DM.append(float(components[7]))
                BINARY.append(components[8])
                BINARY_PERIOD.append(components[9])
                SemiMajor.append(float(components[10]))
                BINCOMP.append(components[11])
                DIST.append(float(components[12]))
                DIST_DM.append(float(components[13]))
                AGE.append(float(components[14]))
                EDOT.append(float(components[15]))
                PMTOT.append(float(components[16]))

        self.csvFile.close()

        powAge = [0.005192]
        powEDOT = [1.33E-020]
        print "\t1.1.1 Creating histogram for period samples..."
        #plt.hist(AGE, bins=self.freedmanDiaconisRule(AGE), color='w')
        plt.scatter(P0, P1)
        plt.yscale('log')
        plt.xscale('log')
        plt.ylim(10e-23, 10e-9)
        plt.xlim(10e-4, 10e1)
        plt.title("Period vs Period derivative")
        plt.xlabel("Period (s)")
        plt.ylabel("Period Derivative (s s^-1)")
        plt.scatter(powAge, powEDOT,color='R')

        plt.plot([10e-3, 10e-8], [10e0, 10e-8], 'r--', lw=8)
        plt.show()
        print "\n\tDone."
        print "\t**************************************************************************" # Used only for formatting purposes.

    # ****************************************************************************************************

    def appendToFile(self,path,text):
        """
        Appends the provided text to the file at the specified path.

        Parameters:
        path    -    the path to the file to append text to.
        text    -    the text to append to the file.

        Returns:
        N/A
        """

        destinationFile = open(path,'a')
        destinationFile.write(str(text))
        destinationFile.close()

    # ******************************************************************************************

    def clearFile(self, path):
        """
        Clears the file at the specified path.

        Parameters:
        path    -    the path to the file to append text to.

        Returns:
        N/A
        """
        open(path, 'w').close()

    # ****************************************************************************************************

    def freedmanDiaconisRule(self,data):
        """
        Calculate number of bins to use in histogram according to this rule.

        Parameters:
        data    -    a numpy.ndarray containing the data for which a histogram is to be computed.

        Returns:

        The 'optimal' number of bins for the histogram.
        """
        # interquartile range, Q3-Q1....
        iqr = stats.scoreatpercentile(data, 75) - stats.scoreatpercentile(data, 25)
        binwidth = 2 * iqr * pow(len(data), -0.3333333)

        if(binwidth<=0):
            binwidth=60

        # calculate n bins
        rnge = max(data) - min(data)
        nbins = ceil( rnge / binwidth )

        if(self.verbose):
            print "\t\tFreedman Diaconis Rule values for bins:"
            print "\t\t\tIQR: ",iqr
            print "\t\t\tBin Width: ",binwidth
            print "\t\t\tRange: ",rnge
            print "\t\t\tNumber of bins: ", nbins

        return int(nbins)

    # ****************************************************************************************************

if __name__ == '__main__':
    PlotCSVData().main()