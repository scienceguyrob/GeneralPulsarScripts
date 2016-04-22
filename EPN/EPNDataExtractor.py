"""
    **************************************************************************
    |                                                                        |
    |             EPN Database Profile Extractor Version 1.0                 |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Extracts pulse profiles stored in the EPN database, and writes them    |
    | to a plain text output file.                                           |
    |                                                                        |
    **************************************************************************
    | Author: Rob Lyon                                                       |
    | Email : robert.lyon@manchester.ac.uk                                   |
    | web   : www.scienceguyrob.com                                          |
    **************************************************************************
    | Required Command Line Arguments:                                       |
    |                                                                        |
    | -d (string) url of the EPN database.                                   |
    |                                                                        |
    | -w (string) full path to a the output file to create.                  |
    |                                                                        |
    | --dir (string) full path to a directory used to store downloaded       |
    |                profile data.                                           |
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

import urllib2

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class EPNDataExtractor:
    """
    Attempts to extract the pulse profiles of pulsars stored
    in the EPN database.

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
        parser.add_option("-d", action="store", dest="url",help='URL which points the EPN database.',default="")
        parser.add_option("-w", action="store", dest="outputPath",help='Path to write outputs to.'  ,default="")
        parser.add_option("--dir", action="store", dest="outputDir",help='Directory to store downloaded files to.'  ,default="")

        # OPTIONAL ARGUMENTS
        parser.add_option("-v", action="store_true", dest="verbose",help='Verbose debugging flag (optional).',default=False)

        (args,options) = parser.parse_args()# @UnusedVariable : Tells Eclipse IDE to ignore warning.

        # Update variables with command line parameters.
        self.verbose    = args.verbose
        self.outputPath = args.outputPath
        self.url        = args.url
        self.outputDir  = args.outputDir

        # ****************************************
        #   Print command line arguments & Run
        # ****************************************

        print "\n\t**************************"
        print "\t| Command Line Arguments |"
        print "\t**************************"
        print "\tDebug:",self.verbose
        print "\tEPN database URL:",self.url
        print "\tOutput file path:",self.outputPath
        print "\tOutput directory path:",self.outputDir

        sys.exit()
        # Now we know the input files exist...

        # Clear the output file of text.
        self.clearFile(self.outputPath)

        # ******************************
        #
        # Perform parsing....
        #
        # ******************************

        for line in urllib2.urlopen(self.url):
            if("<tr>" in line and "/icons/folder.gif" in line):

                HREF = self.extractHREF(line)
                sub_dir = self.url+HREF

                for line_2 in urllib2.urlopen(sub_dir):
                    if("<tr>" in line_2 and "[DIR]" in line_2 and "/icons/folder.gif" in line_2):
                        HREF_2 = self.extractHREF(line_2)
                        sub_dir_2 = sub_dir+HREF_2
                        #print "2: " , sub_dir_2

                        for line_3 in urllib2.urlopen(sub_dir_2):

                            #print "3: " , line_3
                            if("<tr>" in line_3 and "[TXT]" in line_3 and "/icons/text.gif" in line_3):
                                HREF_3 = self.extractTextFILE(line_3)
                                sub_dir_3 = sub_dir_2+HREF_3

                                print sub_dir_3
                                file = sub_dir_3
                                if(".txt" in file):
                                    file_prefix = sub_dir.replace("/","_") + sub_dir_2.replace("/","_")
                                    components = file.split("/")
                                    filename = file_prefix+"_"+components[len(components)-1]

                                    response = urllib2.urlopen(file)
                                    html = response.read()
                                    #u = urllib2.urlopen(file)
                                    #print u
                                    self.appendToFile(self.outputDir + filename,html)
                                    self.appendToFile(self.outputPath,file+"\n")




        print "\n\tDone."
        print "\t**************************************************************************" # Used only for formatting purposes.

    # ****************************************************************************************************

    def extractHREF(self,text):
        """

        :param text:
        :return:
        """

        tmp = text[text.find("href=")+6:len(text)]
        tmp_1 = tmp[0:int(tmp.find("/")+1)]
        return tmp_1

    def extractTextFILE(self,text):
        """

        :param text:
        :return:
        """

        tmp = text[text.find("href=")+6:len(text)]
        tmp_1 = tmp[0:int(tmp.find(">")-1)]
        return tmp_1


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
    EPNDataExtractor().main()