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

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class ParseCSVFile:
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
        self.atnfFile = open(self.atnfParsedPath,'r') # Read only access
        self.outputFile = self.atnfParsedPath.replace(".csv","_parsed.csv")

        self.clearFile(self.outputFile)

        # ****************************************
        #        File parsing section
        # ****************************************


        for line in self.atnfFile.readlines():

            components = line.rstrip('\n').split(",")

            if ( line.startswith("#,NAME")):
                # Ingore header
                pass

            else:
                pass



        self.csvFile.close()

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

if __name__ == '__main__':
    ParseCSVFile().main()