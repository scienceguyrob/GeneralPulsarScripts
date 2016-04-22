"""
    **************************************************************************
    |                                                                        |
    |                   PlotAitoff_Pulsar Version 1.0                        |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Creates an Aitoff projection plot, using entries from a file that      |
    | describes known pulsar sources (ATNF catalog data, in short csv        |
    | no-errors format, stored in a plain text file).                        |
    |                                                                        |
    **************************************************************************
    | Author: Rob Lyon                                                       |
    | Email : robert.lyon@manchester.ac.uk                                   |
    | web   : www.scienceguyrob.com                                          |
    **************************************************************************
    | Required Command Line Arguments:                                       |
    |                                                                        |
    | -p (string) full path to a ATNF pulsar catalog input file.             |
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

import numpy as np
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
from pylab import *
import matplotlib.pyplot as plt
import math as m

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class PlotAitoff_Pulsar_J2302_PLUS_4442:
    """
    For each entry in the ATNF pulsar catalog file, extracts the source
    coordinates, and plots the known sources into an aitoff plot (according
    to some logic). Example of expected input file:

    #,NAME,Gl (deg),Gb (deg),P0 (s),F0(Hz),DM
    1,J0006+1834,108.172,-42.985,0.693748,1.441446,12.00
    2,J0007+7303,119.660,10.463,0.315873,3.165827,*
    3,B0011+47,116.497,-14.631,1.240699,0.805997,30.85
    4,J0023+0923,111.383,-52.849,0.003050,327.868852,14.30
    5,B0021-72C,305.923,-44.892,0.005757,173.708219,24.60
    ...

    """

    # ******************************
    #
    # MAIN METHOD AND ENTRY POINT.
    #
    # ******************************

    def main(self,argv=None):
        """
        Main entry point for the Application.

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
        parser.add_option("-p", action="store", dest="atnfPath",help='Path to a pulsar catalog file.',default="")

        # OPTIONAL ARGUMENTS
        parser.add_option("-v", action="store_true", dest="verbose",help='Verbose debugging flag (optional).',default=False)

        (args,options) = parser.parse_args()# @UnusedVariable : Tells Eclipse IDE to ignore warning.

        # Update variables with command line parameters.
        self.verbose = args.verbose
        self.atnfCatalogPath = args.atnfPath

        # If the catalog file is found...
        if(os.path.isfile(self.atnfCatalogPath)):

            # Read pulsar catalog file, extract useful variables
            self.catalogueFile = open(self.atnfCatalogPath,'r') # Read only access

            # Variables we are looking for:
            # Gl (deg)
            # Gb (deg)
            # PO Barycentric period of the pulsar (s)
            # F0 Barycentric rotation frequency (Hz)
            # DM Dispersion measure (cm-3 pc)

            ATNF_GLS     = []
            ATNF_GBS     = []
            ATNF_PERIODS = []
            ATNF_FREQS   = []
            ATNF_DMS     = []

            # For each line in the file...
            for line in self.catalogueFile.readlines():

                GL = "0"
                GB = "0"
                P0 = "0"
                F0 = "0"
                DM = "0"

                components = line.rstrip('\n').split(",")

                if ( line.startswith("#,")):
                    # Ingore header
                    pass
                else:

                    # Example input data:
                    #
                    #   #,NAME,Gl (deg),Gb (deg),P0 (s),F0(Hz),DM
                    #   1,J0006+1834,108.172,-42.985,0.693748,1.441446,12.00
                    #   2,J0007+7303,119.660,10.463,0.315873,3.165827,*
                    #   3,B0011+47,116.497,-14.631,1.240699,0.805997,30.85
                    #   4,J0023+0923,111.383,-52.849,0.003050,327.868852,14.30
                    #   5,B0021-72C,305.923,-44.892,0.005757,173.708219,24.60
                    #
                    #   Which when each line is split produces string arrays:
                    #
                    #   [ "1" , "J0006+1834" , "108.172" , "-42.985" , "0.693748" , "1.441446"   , "12.00" ]
                    #   [ "2" , "J0007+7303" , "119.660" , "10.463"  , "0.315873" , "3.165827"   , "*"     ]
                    #   [ "3" , "B0011+47"   , "116.497" , "-14.631" , "1.240699" , "0.805997"   , "30.85" ]
                    #   [ "4" , "J0023+0923" , "111.383" , "-52.849" , "0.003050" , "327.868852" , "14.30" ]
                    #   [ "5" , "B0021-72C"  , "305.923" , "-44.892" , "0.005757" , "173.708219" , "24.60" ]
                    #
                    #   So the data we are looking for is at index (assuming zero
                    #   indexing) are at positions 2, 3, 4, 5, 6.

                    if("*" not in components[2]):
                        GL = components[2].strip()

                    if("*" not in components[3]):
                        GB = components[3].strip()

                    if("*" not in components[4]):
                        P0 = components[4].strip()

                    if("*" not in components[5]):
                        F0 = components[5].strip()

                    if("*" not in components[6]):
                        DM = components[6].strip()

                    # Don't inlcude pulsars with missing parameters...
                    if(float(P0) != 0 and float(F0) != 0 and float(DM) > 0 ):

                        # Catalog GL values go from 0 - 360.
                        if(float(GL) > 180):
                            ATNF_GLS.append(m.radians(float(GL)-360))
                        else:
                            ATNF_GLS.append(m.radians(float(GL)))

                        ATNF_GBS.append(m.radians(float(GB)))
                        ATNF_PERIODS.append(float(P0))
                        ATNF_FREQS.append(float(F0))
                        ATNF_DMS.append(float(DM))

            self.catalogueFile.close()

            # Print some details of the data collected...
            print "\n\t+----- ATNF DATA -----+"

            print "\tGLs                : ", len(ATNF_GLS)    , " Mean: ", mean(ATNF_GLS) , \
                " Min: ", min(ATNF_GLS) , " Max: ", max(ATNF_GLS) , \
                " Zero elements: ", len(ATNF_GLS) - count_nonzero(ATNF_GLS)

            print "\tGBs                : ", len(ATNF_GBS)    , " Mean: ", mean(ATNF_GBS) , \
                " Min: ", min(ATNF_GBS) , " Max: ", max(ATNF_GBS) , \
                " Zero elements: ", len(ATNF_GBS) - count_nonzero(ATNF_GBS)

            print "\tPeriods parsed     : ", len(ATNF_PERIODS) , " Mean: ", mean(ATNF_PERIODS) , \
                " Min: ", min(ATNF_PERIODS) , " Max: ", max(ATNF_PERIODS) , \
                " Zero elements: ", len(ATNF_PERIODS) - count_nonzero(ATNF_PERIODS)

            print "\tFrequencies parsed : ", len(ATNF_FREQS)   , " Mean: ", mean(ATNF_FREQS) , \
                " Min: ", min(ATNF_FREQS) , " Max: ", max(ATNF_FREQS) ,\
                " Zero elements: ", len(ATNF_FREQS) - count_nonzero(ATNF_FREQS)

            print "\tDMs parsed         : ", len(ATNF_DMS)     , " Mean: ", mean(ATNF_DMS) , \
                " Min: ", min(ATNF_DMS) , " Max: ", max(ATNF_DMS) , \
                " Zero elements: ", len(ATNF_DMS) - count_nonzero(ATNF_DMS)

            print "\tProducing plot..."

            # OK, now produce the plot...
            host = subplot(111, projection="aitoff")
            #host = subplot(111, projection="hammer")
            grid(True)

            pulsar_bl, pulsarb = [ATNF_GLS, ATNF_GBS]
            pulsarplot = host.scatter(pulsar_bl,pulsarb, c='blue', marker='.', s=1)

            # Now plot the pulsar of the week!!
            # J2302+4442 GL (deg): 103.395 GB (deg):-14.005

            bl = m.radians(103.395)
            b  = m.radians(-14.005)

            host.scatter(bl,b, c='red', marker='.', s=150)

            plt.draw()
            plt.show()

        else:
            print "Catalog file not found at: ", self.atnfCatalogPath

        # ****************************************
        #   Print command line arguments & Run
        # ****************************************

        print "\n\t**************************"
        print "\t| Command Line Arguments |"
        print "\t**************************"
        print "\tDebug:",self.verbose
        print "\tPulsar catalog file path:",self.atnfCatalogPath

        print "\tDone."

        # Used only for formatting purposes.
        print "\t**************************************************************************"

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

if __name__ == '__main__':
    PlotAitoff_Pulsar_J2302_PLUS_4442().main()
