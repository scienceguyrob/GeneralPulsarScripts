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

class PlotAitoff_Pulsar:
    """
    For each entry in the ATNF pulsar catalog file, extracts the source
    coordinates, and plots the known sources into an aitoff plot (according
    to some logic). Example of expected input file:

    #,NAME,Gl(deg),Gb(deg),P0(s),P1,F0(Hz),DM
    1,J0006+1834,108.172,-42.985,0.693748,2.10e-15,1.441446,12.00
    2,J0007+7303,119.660,10.463,0.315873,3.60e-13,3.165827,*
    3,B0011+47,116.497,-14.631,1.240699,5.64e-16,0.805997,30.85
    4,J0023+0923,111.383,-52.849,0.003050,*,327.868852,14.30
    5,B0021-72C,305.923,-44.892,0.005757,-4.98e-20,173.708219,24.60
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

        # ****************************************
        #        File parsing section
        # ****************************************

        # If the catalog file is found...
        if(os.path.isfile(self.atnfCatalogPath)):

            # Read pulsar catalog file, extract useful variables
            self.catalogueFile = open(self.atnfCatalogPath,'r') # Read only access

            # Variables we are looking for:
            # Gl (deg)
            # Gb (deg)
            # PO Barycentric period of the pulsar (s)
            # P1 Period derivative
            # F0 Barycentric rotation frequency (Hz)
            # DM Dispersion measure (cm-3 pc)

            ATNF_GLS           = []
            ATNF_GBS           = []
            ATNF_PERIODS       = []
            ATNF_PERIODS_DERIV = []
            ATNF_FREQS         = []
            ATNF_DMS           = []

            ATNF_GLS_MSP     = []
            ATNF_GBS_MSP     = []
            ATNF_PERIODS_MSP = []
            ATNF_FREQS_MSP   = []
            ATNF_DMS_MSP     = []

            normalPulsarsMissingParameters = 0
            mspsMissingParameters = 0

            # For each line in the file...
            for line in self.catalogueFile.readlines():

                GL = "0"
                GB = "0"
                P0 = "0"
                P1 = "0"
                F0 = "0"
                DM = "0"

                components = line.rstrip('\n').split(",")

                if ( line.startswith("#,")):
                    # Ingore header
                    pass
                else:

                    # Example input data:
                    #
                    #   #,NAME,Gl(deg),Gb(deg),P0(s),P1,F0(Hz),DM
                    # 1,J0006+1834,108.172,-42.985,0.693748,2.10e-15,1.441446,12.00
                    # 2,J0007+7303,119.660,10.463,0.315873,3.60e-13,3.165827,*
                    # 3,B0011+47,116.497,-14.631,1.240699,5.64e-16,0.805997,30.85
                    # 4,J0023+0923,111.383,-52.849,0.003050,*,327.868852,14.30
                    # 5,B0021-72C,305.923,-44.892,0.005757,-4.98e-20,173.708219,24.60
                    #
                    #   Which when each line is split produces string arrays:
                    #
                    #   [ "1" , "J0006+1834" , "108.172" , "-42.985" , "0.693748" , "2.10e-15" , "1.441446"   , "12.00" ]
                    #   [ "2" , "J0007+7303" , "119.660" , "10.463"  , "0.315873" , "3.60e-13" , "3.165827"   , "*"     ]
                    #   [ "3" , "B0011+47"   , "116.497" , "-14.631" , "1.240699" , "5.64e-16" , "0.805997"   , "30.85" ]
                    #   [ "4" , "J0023+0923" , "111.383" , "-52.849" , "0.003050" , "*" , "327.868852" , "14.30" ]
                    #   [ "5" , "B0021-72C"  , "305.923" , "-44.892" , "0.005757" , "-4.98e-20" , "173.708219" , "24.60" ]
                    #
                    #   So the data we are looking for is at index (assuming zero
                    #   indexing) positions 2, 3, 4, 5, 6, 7.

                    # Check that an asterisk is not in place of an expected numerical value.
                    # This happens when there is a missing entry in the catalog.
                    if("*" not in components[2]):
                        GL = components[2].strip()

                    if("*" not in components[3]):
                        GB = components[3].strip()

                    if("*" not in components[4]):
                        P0 = components[4].strip()

                    if("*" not in components[5]):
                        P1 = components[5].strip()

                    if("*" not in components[6]):
                        F0 = components[6].strip()

                    if("*" not in components[7]):
                        DM = components[7].strip()

                    # Don't include pulsars with missing parameters...
                    if(float(P0) != 0 and float(F0) != 0 and float(DM) > 0 and float(P1) != 0):

                        if( (float(P0)*1000) < 30 and float(P1) < 10e-16 ):
                            # Catalog GL values go from 0 - 360.
                            if(float(GL) > 180):
                                ATNF_GLS_MSP.append(m.radians(float(GL)-360))
                            else:
                                ATNF_GLS_MSP.append(m.radians(float(GL)))

                            ATNF_GBS_MSP.append(m.radians(float(GB)))
                            ATNF_PERIODS_MSP.append(float(P0))
                            ATNF_FREQS_MSP.append(float(F0))
                            ATNF_DMS_MSP.append(float(DM))
                        else:

                             # Catalog GL values go from 0 - 360.
                            if(float(GL) > 180):
                                ATNF_GLS.append(m.radians(float(GL)-360))
                            else:
                                ATNF_GLS.append(m.radians(float(GL)))

                            ATNF_GBS.append(m.radians(float(GB)))
                            ATNF_PERIODS.append(float(P0))
                            ATNF_FREQS.append(float(F0))
                            ATNF_DMS.append(float(DM))

                    # If all parameters are available except for period derivative...
                    elif (float(P0) != 0 and float(F0) != 0 and float(DM) > 0):
                        # Catalog GL values go from 0 - 360.
                        if(float(GL) > 180):
                            ATNF_GLS.append(m.radians(float(GL)-360))
                        else:
                            ATNF_GLS.append(m.radians(float(GL)))

                        ATNF_GBS.append(m.radians(float(GB)))
                        ATNF_PERIODS.append(float(P0))
                        ATNF_FREQS.append(float(F0))
                        ATNF_DMS.append(float(DM))
                    else:

                        normalPulsarsMissingParameters+=1

            self.catalogueFile.close()

            # Print some details of the data collected...
            print "\n\t+----- MSP ATNF DATA -----+"

            print "\tGLs                : ", len(ATNF_GLS_MSP)    , " Mean: ", mean(ATNF_GLS_MSP) , \
                " Min: ", min(ATNF_GLS_MSP) , " Max: ", max(ATNF_GLS_MSP) , \
                " Zero elements: ", len(ATNF_GLS_MSP) - count_nonzero(ATNF_GLS_MSP)

            print "\tGBs                : ", len(ATNF_GBS_MSP)    , " Mean: ", mean(ATNF_GBS_MSP) , \
                " Min: ", min(ATNF_GBS_MSP) , " Max: ", max(ATNF_GBS_MSP) , \
                " Zero elements: ", len(ATNF_GBS_MSP) - count_nonzero(ATNF_GBS_MSP)

            print "\tPeriods parsed     : ", len(ATNF_PERIODS_MSP) , " Mean: ", mean(ATNF_PERIODS_MSP) , \
                " Min: ", min(ATNF_PERIODS_MSP) , " Max: ", max(ATNF_PERIODS_MSP) , \
                " Zero elements: ", len(ATNF_PERIODS_MSP) - count_nonzero(ATNF_PERIODS_MSP)

            print "\tFrequencies parsed : ", len(ATNF_FREQS_MSP)   , " Mean: ", mean(ATNF_FREQS_MSP) , \
                " Min: ", min(ATNF_FREQS_MSP) , " Max: ", max(ATNF_FREQS_MSP) ,\
                " Zero elements: ", len(ATNF_FREQS_MSP) - count_nonzero(ATNF_FREQS_MSP)

            print "\tDMs parsed         : ", len(ATNF_DMS_MSP)     , " Mean: ", mean(ATNF_DMS_MSP) , \
                " Min: ", min(ATNF_DMS_MSP) , " Max: ", max(ATNF_DMS_MSP) , \
                " Zero elements: ", len(ATNF_DMS_MSP) - count_nonzero(ATNF_DMS_MSP)

            print "\n\tPulsars missing parameters (not included): ", normalPulsarsMissingParameters

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

            print "\t\nProducing plot..."

            # OK, now produce the plot...
            host = subplot(111, projection="aitoff")
            #host = subplot(111, projection="hammer")
            grid(True)

            pulsar_bl, pulsarb = [ATNF_GLS, ATNF_GBS]
            pulsar_msp_bl, pulsar_msp_b = [ATNF_GLS_MSP, ATNF_GBS_MSP]
            pulsar_msp_bl, pulsar_msp_b = [ATNF_GLS_MSP, ATNF_GBS_MSP]

            # Hard coded FRB locations, according to GL and GB.
            frbl =  [m.radians(-3.4), m.radians(-59.4), m.radians(-113.6), m.radians(50.57), m.radians(-4.14),\
                          m.radians(80.99), m.radians(49.28), m.radians(-51.78), m.radians(7.45), m.radians(-104.4),\
                          m.radians(-35.2), m.radians(-99.5), m.radians(50.8)]

            frbb = [m.radians(-20.02), m.radians(-41.8),m.radians(-60.02), m.radians(-54.85), m.radians(-41.75),\
                    m.radians(-59.02), m.radians(-66.2),m.radians(-26.2), m.radians(27.42), m.radians(30.66),\
                    m.radians(54.74),m.radians(-21.9), m.radians(-54.6)]


            pulsarplot = host.scatter(pulsar_bl,pulsarb, c='blue', marker='.', s=5)
            host.scatter(pulsar_msp_bl,pulsar_msp_b, c='red', marker='.', s=50)
            host.scatter(frbl,frbb, c='yellow', marker='*', s=500)

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
    PlotAitoff_Pulsar().main()
