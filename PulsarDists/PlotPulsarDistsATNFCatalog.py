"""
    **************************************************************************
    |                                                                        |
    |              Plot Pulsar Distributions (ATNF) Version 1.0              |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Generates pulsar candidate generation parameters, including period,    |
    | DM, pulse width, and duty cycle. These parameters are written to an    |
    | output file in CSV format (one set of parameters per line) for input   |
    | into other tools.                                                      |
    |                                                                        |
    **************************************************************************
    | Author: Rob Lyon                                                       |
    | Email : robert.lyon@manchester.ac.uk                                   |
    | web   : www.scienceguyrob.com                                          |
    **************************************************************************
    | Required Command Line Arguments:                                       |
    |                                                                        |
    | -a (string) full path to a ATNF pulsar catalog database file.          |
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
from numpy import percentile
from numpy import mean
from numpy import random
from numpy import median
from numpy import count_nonzero

# Scipy Imports:
from scipy import std
from scipy import stats
from scipy import arange


# Other imports
import matplotlib.pyplot as plt

# For coordinate transformations.
import ephem
from astropy.coordinates import SkyCoord

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class PlotPulsarDistsATNFCatalog:
    """
    For each entry in the ATNF pulsar catalog file, this script parses the
    data in the file, and plots their distributions.

    Not all entries in the ATNF catalog have a DM,
    period, W10 or W50 value. Missing values which cannot be computed are
    represented by a zero value in the output file. If a catalog entry has
    a period, but no frequency listed, the frequency is computed using:

    frequency = 1 / Period

    and likewise if the frequency is known but the period isn't,

    period = 1 / Frequency.

    Example input (extract from catalog file, top two entries):

    #CATALOGUE 1.54
    #
    # DO NOT EDIT THIS FILE!
    # Contact Dick Manchester or George Hobbs if in doubt.
    #
    PSRJ     J0006+1834                    cnt96
    RAJ      00:06:04.8               2    cn95
    DECJ     +18:34:59                4    cn95
    P0       0.69374767047            14   cn95
    P1       2.097E-15                12   cn95
    PEPOCH   49079.5                       cn95
    DM       12.0                     6    cn95
    S400     0.2                           cn95
    W50      82                            cn95
    W10      195                           cn95
    DIST_DM  0.70                          tc93
    DIST_DM1 0.68                          cl02
    SURVEY   ar4
    @-----------------------------------------------------------------
    PSRJ     J0007+7303                    aaa+09c
    RAJ      00:07:01.7               2    awd+12
    DECJ     +73:03:07.4              8    awd+12
    F0       3.165827392              3    awd+12
    F1       -3.6120E-12              5    awd+12
    F2       4.1E-23                  7    awd+12
    F3       5.4E-30                  9    awd+12
    PEPOCH   54952                         awd+12
    NGLT     1
    DIST_AMN 1.1                           plmg93
    DIST_AMX 1.7                           plmg93
    TYPE     NRAD
    ASSOC    GRS:2FGL_J0007.0+7303[naa+12],XRS:RX_J0007.0+7303[cdm+10],SNR:CTA1[hgc+04]
    SURVEY   FermiBlind
    @-----------------------------------------------------------------
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
        parser.add_option("-a", action="store", dest="atnfPath",help='Path to a pulsar catalog parsed file.',default="")

        # OPTIONAL ARGUMENTS
        parser.add_option("-v", action="store_true", dest="verbose",help='Verbose debugging flag (optional).',default=False)

        (args,options) = parser.parse_args()# @UnusedVariable : Tells Eclipse IDE to ignore warning.

        # Update variables with command line parameters.
        self.verbose        = args.verbose
        self.atnfParsedPath = args.atnfPath

        # ****************************************
        #   Print command line arguments & Run
        # ****************************************

        print "\n\t**************************"
        print "\t| Command Line Arguments |"
        print "\t**************************"
        print "\tDebug:",self.verbose
        print "\tParsed Pulsar catalog file path:",self.atnfParsedPath

        # Check arguments for validity...
        if(os.path.isfile(self.atnfParsedPath) == False):
            print "\n\tYou must supply a valid parsed ATNF file via the -a flag."
            sys.exit()

        # Now we know the input files exist...

        # Read parsed pulsar catalog file, extract useful variables:
        # Period, Frequency, DM, pulse width
        self.catalogFile = open(self.atnfParsedPath,'r') # Read only access

        # ****************************************
        #          File parsing section
        # ****************************************


        # Variable stores...
        ATNF_PERIODS  = []
        ATNF_FREQS    = []
        ATNF_DMS      = []
        ATNF_W10S     = []
        ATNF_W50S     = []


        # Row variables...
        Name = "Unknown"
        RA   = "00:00:00"
        DEC  = "00:00:00"
        EL   = "0"
        EB   = "0"
        P0   = "0"
        F0   = "0"
        DM   = "0"
        W10  = "0"
        W50  = "0"

        # For each line in the file...
        for line in self.catalogFile.readlines():
            if ( line[0] == '#'):
                pass
                    # Ignore these lines.
            elif ( line[0] == '@'):
                # This signals the end of the current source
                # int the catalog file, so simply add the details
                # collected to the output file.

                # Compute period and frequency if not listed in catalog file.
                if ( P0 == "0" and F0 != "0"):
                    P0 = str( 1.0 / (float(F0)) )

                if ( F0 == "0" and P0 != "0"):
                    F0 = str( 1.0 / (float(P0)) )

                # Check coordinates are valid, or convert them to make
                # them valid. Also does equatorial to galactic conversion.
                RA,DEC, GL,GB = self.checkCoords(RA,DEC,EL,EB)

                if(P0 != "0"):
                    ATNF_PERIODS.append(float(P0))

                if(F0 != "0"):
                    ATNF_FREQS.append(float(F0))

                if(DM != "0"):
                    ATNF_DMS.append(float(DM))

                if(W10 != "0"):
                    ATNF_W10S.append(float(W10))

                if(W50 != "0"):
                    ATNF_W50S.append(float(W50))

                # Reset variables. This is useful as not all entries in the catalog
                # have the values we're looking for (e.g. W10 or W50 are often empty).
                Name = "Unknown"
                RA   = "00:00:00"
                DEC  = "00:00:00"
                EL   = "0"
                EB   = "0"
                P0   = "0"
                F0   = "0"
                DM   = "0"
                W10  = "0"
                W50  = "0"
                DM_DIST   = "0"
                DM_DIST_1 = "0"

            elif ( len(line) > 2 ):
                pass
                # If the line doesn't begin with '#' or '@' and isn't
                # an empty line, then process it.

                if ( line.startswith("PSRJ")):
                    Name = self.extractRAAndDec(line)
                #elif ( line.startswith("RAJ")):
                #    RA = self.extractRAAndDec(line)
                #elif ( line.startswith("DECJ")):
                #    DEC = self.extractRAAndDec(line)
                #elif ( line.startswith("ELONG")):
                #    EL = self.extractFromCatalogFile(line)
                #elif ( line.startswith("ELAT")):
                #    EB = self.extractFromCatalogFile(line)
                elif ( line.startswith("P0")):
                    P0 = self.extractFromCatalogFile(line)
                elif ( line.startswith("F0")):
                    F0 = self.extractFromCatalogFile(line)
                elif ( line.startswith("DM") and "DMEPOCH" not in line and "DIST" not in line):
                    DM = self.extractFromCatalogFile(line)
                #elif ( line.startswith("DIST_DM") and "DMEPOCH" not in line and "1" not in line):
                #    DM_DIST = self.extractFromCatalogFile(line)
                #elif ( line.startswith("DIST_DM1") and "DMEPOCH" not in line):
                #    DM_DIST_1 = self.extractFromCatalogFile(line)
                elif ( line.startswith("W10")):
                    W10 = self.extractFromCatalogFile(line)
                elif ( line.startswith("W50")):
                    W50 = self.extractFromCatalogFile(line)
            else:
                pass # else ignore

        self.catalogFile.close()

        # ****************************************
        #       Print stats of data collected
        # ****************************************

        # Print some details of the data collected...
        print "\n\t+----- ATNF DATA -----+"
        print "\tPeriods parsed     : ", len(ATNF_PERIODS) , " Mean: ", mean(ATNF_PERIODS) , \
            " Min: ", min(ATNF_PERIODS) , " Max: ", max(ATNF_PERIODS) , \
            " Zero elements: ", len(ATNF_PERIODS) - count_nonzero(ATNF_PERIODS)

        print "\tFrequencies parsed : ", len(ATNF_FREQS)   , " Mean: ", mean(ATNF_FREQS) , \
            " Min: ", min(ATNF_FREQS) , " Max: ", max(ATNF_FREQS) ,\
            " Zero elements: ", len(ATNF_FREQS) - count_nonzero(ATNF_FREQS)

        print "\tDMs parsed         : ", len(ATNF_DMS)     , " Mean: ", mean(ATNF_DMS) , \
            " Min: ", min(ATNF_DMS) , " Max: ", max(ATNF_DMS) , \
            " Zero elements: ", len(ATNF_DMS) - count_nonzero(ATNF_DMS)

        print "\t10% Widths parsed  : ", len(ATNF_W10S)    , " Mean: ", mean(ATNF_W10S) , \
            " Min: ", min(ATNF_W10S) , " Max: ", max(ATNF_W10S) , \
            " Zero elements: ", len(ATNF_W10S) - count_nonzero(ATNF_W10S)

        print "\t50% Widths parsed  : ", len(ATNF_W50S)    , " Mean: ", mean(ATNF_W50S) , \
            " Min: ", min(ATNF_W50S) , " Max: ", max(ATNF_W50S) , \
            " Zero elements: ", len(ATNF_W50S) - count_nonzero(ATNF_W50S)

        # ****************************************
        #
        #
        #
        #            Generating plots
        #
        #
        #
        # ****************************************

        # Now create the plots.

        print "\n\t+----- Fitting Distributions -----+"

        # ****************************************
        #              Pulse Widths
        # ****************************************

        print "\n\n\t4.1. Plotting Histogram of ATNF pulse widths"

        # Plot histogram to show randomly generated width data points,
        # if verbose logging enabled...

        print "\t4.1.1. Creating histogram for pulse width samples..."
        ATNF_Widths_Histogram = plt.hist(ATNF_W10S, bins=self.freedmanDiaconisRule(ATNF_W10S), color='b',label='Pulse widths 10%')
        plt.title("Histogram of Observed Pulse Widths in ATNF Catalog")
        plt.xlabel("Pulse Width (ms)")
        plt.ylabel("Frequency")
        plt.legend(loc='upper right')
        plt.show()

        print "\n\tDone."
        print "\t**************************************************************************" # Used only for formatting purposes.

    # ****************************************************************************************************

    # ****************************************************************************************************

    def checkCoords(self,RA,DEC,EL,EB):
        """
        Checks that RA, DEC, GL and GB coordinates are correct.
        Some ATNF entries have no RAJ or DECJ listed, only Equatorial
        longitude and latitude. Likewise some candidates have RAJ and DECJ
        listed but not galactic coordinates.

        This function then computes RAJ and DECJ given ELong or ELat, and
        also computes galactic longitude and latitude.

        Parameters:
        line    -    the line to extract data from.

        Returns:
            the RAJ, DECJ, GL, GB cooridinates of a ATNF catalog entry.

        """

        if("00:00:00" in RA and "00:00:00" in DEC):
            # No RA and DEC provided. Try to create from EL and EB
            if(EL == "0" and EB == "0"):
                return [RA,DEC,EL,EB] #  Here just return the inputs, since we can't convert...
            else:

                # Use pyephem to convert from ecliptic to Equatorial coordinates...
                ec = ephem.Ecliptic(EL,EB,epoch='2000')
                RA = str(ec.to_radec()[0])
                DEC = str(ec.to_radec()[1])

                # Since we can't just convert from RA and DEC to GL and GB in pyephem,
                # we instead use astropy to do the job. This requires that we first do
                # some daft parsing of the string into pieces, then reform it in to the
                # format required by astropy...
                RA_COMPS = RA.split(":")
                DEC_COMPS = DEC.split(":")
                # Now reform the text into astropy format...
                coordinateString = RA_COMPS[0] +"h"+ RA_COMPS[1] + "m" +RA_COMPS[2] + "s " + DEC_COMPS[0] +"d"+ DEC_COMPS[1] + "m" +DEC_COMPS[2] + "s"
                # Now get galactic coordinates.
                GL, GB = str(SkyCoord(coordinateString).galactic.to_string()).split()

                return [RA,DEC,GL,GB]

        if(EL == "0" and EB == "0"):
            # No EL and EB provided.
            if("00:00:00" in RA and "00:00:00" in DEC):
                return [RA,DEC,EL,EB] #  Here just return the inputs, since we can't convert...
            else:
                # Since we can't just convert from RA and DEC to GL and GB in pyephem,
                # we instead use astropy to do the job. This requires that we first do
                # some daft parsing of the string into pieces, then reform it in to the
                # format required by astropy...
                RA_COMPS = self.checkFormatEquatorialCoordinate(RA).split(":")
                DEC_COMPS = self.checkFormatEquatorialCoordinate(DEC).split(":")
                # Now reform the text into astropy format...
                coordinateString = RA_COMPS[0] +"h"+ RA_COMPS[1] + "m" +RA_COMPS[2] + "s " + DEC_COMPS[0] +"d"+ DEC_COMPS[1] + "m" +DEC_COMPS[2] + "s"
                # Now get galactic coordinates.
                GL, GB = str(SkyCoord(coordinateString).galactic.to_string()).split()

                return [RA,DEC,GL,GB]

        return [RA,DEC,EL,EB]

    # ****************************************************************************************************

    def checkFormatEquatorialCoordinate(self,coord):
        """
        Checks an equatorial coordinate component (RA or DEC) is
        correctly formed as a string, i.e. has the format:

        HH:MM:SS or DD:MM:SS
        :param coord:
            the coordinate the check.
        :return:
            the correctly formatted string.
        """
        components=coord.split(":")
        length = len(components)
        formatedCoord = ""
        if(length<3):
            if(length==1):
                formatedCoord=coord+":00:00"
            elif(length==2):
                formatedCoord=coord+":00"
        else:
            formatedCoord = coord

        return formatedCoord

    # ****************************************************************************************************

    def extractRAAndDec(self,line):
        """
        Extracts RA and DEC values from a line of text.

        Expects lines of the form:

        PSRJ     J0006+1834                    cnt96
        RAJ      00:06:04.8               2    cn95
        RAJ      03:48:43.639000          4    afw+13
        DECJ     +04:32:11.4580           2    afw+13

        Parameters:
        line    -    the line to extract data from.

        Returns:
            the string representation of the value stored in the line. For
            the strings shown above, the function would return:

            "J0006+1834"
            "00:06:04.8"
            "03:48:43.639000"
            "+04:32:11.4580"

        """

        # Split string on whitespace. This should return an array of strings (see the
        # more detailed description below).
        components = line.split()

        # If after splitting on whitespace the array has a length greater than zero (has data)...
        if(len(components) > 1):

            return components[1].strip()
        else:
            # For some reason there are no string components, so return 0
            return "00:00:00"

    # ****************************************************************************************************

    def extractFromCatalogFile(self,line):
        """
        Extracts RA and DEC values from a line of text.

        Expects lines of the form:

        P0       0.69374767047            14   cn95
        P1       2.097E-15                12   cn95
        DM       12.0                     6    cn95
        W50      82                            cn95

        Parameters:
        line    -    the line to extract data from.

        Returns:
            the string representation of the value stored in the line. For
            the strings shown above, the function would return:

            "0.69374767047"
            "2.097E-15"
            "12.0"
            "82"

        """

        # Split string on whitespace. This should return an array of strings (see the
        # more detailed description below).
        components = line.split()

        # If after splitting on whitespace the array has a length greater than zero (has data)...
        if(len(components) > 0):
            return components[1].strip()
        else:
            # For some reason there are no string components, so return 0
            return "0"

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

    # ******************************************************************************************

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
    PlotPulsarDistsATNFCatalog().main()