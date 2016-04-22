"""
    **************************************************************************
    |                                                                        |
    |                        EPN to ASC Version 1.0                          |
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
    | -e (string) full path to the directory to the EPN files.               |
    |                                                                        |
    | -a (string) full path to the directory to store ACN files in.          |
    |                                                                        |
    | -f (int)    frequency in MHz of EPN files to use.                      |
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

import fnmatch, os, sys

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class EpnToAsc:
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
        parser.add_option("-e", action="store", dest="epnPath",help='Path to a directory containing EPN files.',default="")
        parser.add_option("-a", action="store", dest="outputPath",help='Path to a directory to write asc files to.',default="")
        parser.add_option("-f", type="int", dest="frequency",help='The target frequency of EPN files to use.',default=1400)

        # OPTIONAL ARGUMENTS
        parser.add_option("-v", action="store_true", dest="verbose",help='Verbose debugging flag (optional).',default=False)

        (args,options) = parser.parse_args()# @UnusedVariable : Tells Eclipse IDE to ignore warning.

        # Update variables with command line parameters.
        self.verbose    = args.verbose
        self.epnPath    = args.epnPath
        self.outputDir  = args.outputPath
        self.frequency  = args.frequency

        # ****************************************
        #   Print command line arguments & Run
        # ****************************************

        print "\n\t**************************"
        print "\t| Command Line Arguments |"
        print "\t**************************"
        print "\tDebug:",self.verbose
        print "\tEPN file input directory:",self.epnPath
        print "\tASC file output directory:",self.outputDir
        print "\tTarget frequency of EPN files:",self.frequency

        # First check user has supplied an EPN input director path ...
        if(not self.outputDir):
            print "\n\tYou must supply a valid EPN input directory file via the -e flag."
            sys.exit()
        else:
            # User has passed in an input directory, now we need to check that
            # it is valid.
            if(os.path.exists(self.epnPath) == False):
                print "\n\tSupplied EPN input directory invalid!"
                sys.exit()

        # Now the user may have supplied an output directory path, but it may
        # not be valid. So first try to create the directory, if it doesn't
        # already exist. If the create fails, the directory path must be invalid,
        # so exit the application.
        if(os.path.exists(self.outputDir) == False):
            try:
                os.makedirs(self.outputDir)
            except OSError as exception:
                print "\n\tException encountered trying to create ACN file output directory - Exiting!"
                sys.exit()

        # If the directory creation call above did not fail, the output directory
        # should now exist. Check that this is the case...
        if(os.path.isdir(self.outputDir) == False):
            print "\n\tACN file output directory invalid - Exiting!"
            sys.exit()

        if(self.frequency < 0):
            print "\n\tSupplied frequency value invalid - Exiting!"
            sys.exit()

        # Now we know the input files exist...

        # ****************************************
        #        File parsing section
        # ****************************************

        # Read parsed pulsar catalog file, extract useful variables:
        # Period, Frequency, DM, pulse width
        print "\tParsing files..."

        # Loop through the specified directory
        for root, subFolders, filenames in os.walk(self.epnPath):
            # for each file
            for filename in filenames:
                path = os.path.join(root, filename) # Gets full path to the candidate.

                if(".acn" in path):

                    if(self.verbose):
                        print "Processing:", path

                    self.readEPNFile(path,filename,self.outputDir)


        print "\n\tDone."
        print "\t**************************************************************************" # Used only for formatting purposes.

    # ****************************************************************************************************

    def readEPNFile(self,path,filename,outputDir):
        """

        :param path:
        :return:
        """

        print "\tProcessing: ", path
        data = []
        self.epnFile = open(path,'r') # Read only access

        # For each line in the file, split on whitespace...
        for line in self.epnFile.readlines():

            components = line.rstrip('\r').split()

            # If line non empty
            if ( len(line) > 0):
                # If there are more than 0 components after splitting on whitespace...
                if(len(components) > 0):
                    #print components

                    intensityValue = components[3]# Column 4
                    data.append(float(intensityValue))

        self.epnFile.close()

        newData = self.scale(data)

        newDataStr = str(newData[0])

        for d in newData[1:len(data)]:
            newDataStr+= "," + str(d)

        outputPath = outputDir + "/" + filename

        self.appendToFile(outputPath.replace(".acn",".asc"),newDataStr)

    # ******************************************************************************************

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

    def scale(self,data):
        """
        Scales the profile data for pfd files so that it is in the range 0-255.
        This is the same range used in the phcx files. So  by performing this scaling
        the features for both type of candidates are directly comparable. Before it was
        harder to determine if the features generated for pfd files were working correctly,
        since the phcx features are our only point of reference.

        Parameter:
        data    -    the data to scale to within the 0-255 range.

        Returns:
        A new array with the data scaled to within the range [0,255].
        """
        min_=min(data)
        max_=max(data)

        newMin=0;
        newMax=255

        newData=[]

        for n in range(len(data)):

            value=data[n]
            x = (newMin * (1-( (value-min_) /( max_-min_ )))) + (newMax * ( (value-min_) /( max_-min_ ) ))
            newData.append(x)

        return newData

    # ****************************************************************************************************

if __name__ == '__main__':
    EpnToAsc().main()