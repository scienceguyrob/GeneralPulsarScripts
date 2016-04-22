"""
    **************************************************************************
    |                                                                        |
    |             EPN Database Profile Extractor Version 2.0                 |
    |                                                                        |
    **************************************************************************
    | Description:                                                           |
    |                                                                        |
    | Extracts pulse profiles stored in the EPN database, and writes them    |
    | to a plain text output file. To work it requires a version of the      |
    | html used to present the database - this file must be saved to the     |
    | local disk. The application then reads this file, and extracts file    |
    | paths for download from it.                                            |
    |                                                                        |
    | Downloading the html file ( http://www.epta.eu.org/epndb/ ) is not     |
    | exactly straightforward. This is because the site uses a script to     |
    | populate the html file dynamically. This just loading this file via a  |
    | url library will not work, as the dynamic javascript is not executed.  |
    | As a workaround, it is possible to view the dynamic page source live   |
    | in modern browsers such as chrome and firefox. If you extract the live |
    | html and save it to a file, this application may be able to process it.|
    | It will likely require some minor modifications however!!              |
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

import os, sys, re

import urllib2

import BeautifulSoup

# ******************************
#
# CLASS DEFINITION
#
# ******************************

class EPNDataExtractor_v2:
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
        parser.add_option("-d", action="store", dest="htmlPath",help='Path to input html file.',default="")
        parser.add_option("-w", action="store", dest="outputPath",help='Path to write outputs to.'  ,default="")
        parser.add_option("--dir", action="store", dest="outputDir",help='Directory to store downloaded files to.'  ,default="")

        # OPTIONAL ARGUMENTS
        parser.add_option("-v", action="store_true", dest="verbose",help='Verbose debugging flag (optional).',default=False)

        (args,options) = parser.parse_args()# @UnusedVariable : Tells Eclipse IDE to ignore warning.

        # Update variables with command line parameters.
        self.verbose    = args.verbose
        self.htmlPath   = args.htmlPath
        self.outputPath = args.outputPath
        self.outputDir  = args.outputDir

        # ****************************************
        #   Print command line arguments & Run
        # ****************************************

        print "\n\t**************************"
        print "\t| Command Line Arguments |"
        print "\t**************************"
        print "\tDebug:",self.verbose
        print "\tEPN database file:",self.htmlPath
        print "\tOutput file path:",self.outputPath
        print "\tOutput directory path:",self.outputDir

        # Now we know the input files exist...

        # Clear the output file of text.
        if(os.path.exists(self.outputPath) == True):
            self.clearFile(self.outputPath)

        # Clear the output file of text.
        if(os.path.exists(self.htmlPath) == False):
            print "You must specifiy an input html file via -d flag!"
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

        # ******************************
        #
        #
        # Perform parsing of file
        #
        #
        # ******************************

        # The file downloaded from the live chrome version of the EPN
        # database, was modified to make parsing simpler. The file being
        # parsed then has the simple format shown below...
        #
        # <html><head>
        # </head>
        # <body>
        # <div id="searchMain">
        # <ul>
        # ...
        # </ul>
        # </div>
        # </body></html>
        #
        # where ... represents the space where links to EPN pages appear.
        #
        # General psuedocode for parsing...
        #
        # for each line in html file
        #     get pulsar name
        #     for nested list in the line
        #         get frequency
        #         get file path
        #         write out new file with format <Pulsar>_<Frequency>_.acn
        #
        #

        links = []
        altLinks = []
        fileNames = []
        print "\n\nParsing...\n\n"
        self.htmlFile = open(self.htmlPath,'r') # Read only access

        # For each line in the file, split on whitespace...
        for line in self.htmlFile.readlines():
            # If line starts with a list item
            if(line.startswith("<li>")):
                # First remove unhelpful text in the data
                line_cleaned = line.replace("&nbsp;","")
                line_cleaned = line_cleaned.replace("\r","")
                line_cleaned = line_cleaned.replace("\n","")
                line_cleaned = line_cleaned.replace("<small>","")
                line_cleaned = line_cleaned.replace("</small>","")

                # Use regex to remove other components...
                re1='.*?'	# Non-greedy match on filler
                re2='(\\[.*?\\])'	# Square Braces 1
                rg = re.compile(re1+re2,re.IGNORECASE|re.DOTALL)
                m = rg.search(line_cleaned)

                if m:
                    line_cleaned =line_cleaned.replace(m.group(1),"")

                line_cleaned = line_cleaned.replace(" <ul>","<ul>")

                linkComponents = line_cleaned.split("<li>")

                pulsarName_1 = linkComponents[1].replace("<ul>","")
                pulsarName_2 = linkComponents[1].replace("<ul>","")

                re3='.*?'	# Non-greedy match on filler
                re4='(\\(.*?\\))'	#
                rg = re.compile(re3+re4,re.IGNORECASE|re.DOTALL)
                m = rg.search(pulsarName_1)

                if m:
                    pulsarName_1 = pulsarName_1.replace(m.group(1),"")
                    pulsarName_2 = m.group(1).replace(")","").replace("(","")

                print "\tPulsar name 1: ", pulsarName_1, "\tPulsar name 2: ", pulsarName_2

                for linkComponent in linkComponents[2:len(linkComponents)]:

                    linkComponent_clean = linkComponent.replace("<ul>","")
                    linkComponent_clean = linkComponent_clean.replace("</li>","")
                    linkComponent_clean = linkComponent_clean.replace("</ul>","")

                    # Now get frequency
                    indexOfFrequencyStart = linkComponent_clean.find(">")
                    indexOfFrequencyEnd   = linkComponent_clean.find(",")
                    frequency = linkComponent_clean[indexOfFrequencyStart+1:indexOfFrequencyEnd]
                    frequency = frequency.replace("MHz","").strip()
                    frequency = frequency[0:frequency.find(".")]
                    print "\tFrequency (MHz): " , frequency

                    # Now get path to file...
                    indexOfFileStart = linkComponent_clean.find("href=")
                    indexOfFileEnd   = linkComponent_clean.find(">")
                    FirstFile = linkComponent_clean[indexOfFileStart+6:indexOfFileEnd-1]
                    SecondFile = FirstFile.replace(pulsarName_1,pulsarName_2)

                    print "\tFile 1: " , FirstFile
                    print "\tFile 2: " , SecondFile

                    outputFilePath = pulsarName_1 + "_" + frequency + ".acn"

                    print "\tOutput file: " , outputFilePath
                    fileNames.append(outputFilePath)
                    # First part of URL
                    # http://www.epta.eu.org/epndb/
                    #
                    # Thus if we extract the link...
                    # #cn95/J0006+1834/cn95.epn
                    #
                    # The full path to the link will be...
                    # http://www.epta.eu.org/epndb/#cn95/J0006+1834/cn95.epn
                    #
                    # Whilst the actual ascii file is stored at...
                    # http://www.epta.eu.org/epndb/ascii/cn95/J0006+1834/cn95.txt

                    urlLink = "http://www.epta.eu.org/epndb/" + FirstFile.replace("#","ascii/").replace(".epn",".txt").replace(".STF",".txt").replace(".TF",".txt").replace(".STFC",".txt").replace(".SFTC",".txt")
                    alternativeLink = "http://www.epta.eu.org/epndb/" + SecondFile.replace("#","ascii/").replace(".epn",".txt").replace(".STF",".txt").replace(".TF",".txt").replace(".STFC",".txt").replace(".SFTC",".txt")

                    urlLink = urlLink[0:urlLink.rfind(".")] + ".txt"
                    alternativeLink = alternativeLink[0:alternativeLink.rfind(".")] + ".txt"
                    print "\tURL Link: " , urlLink
                    print "\tURL Link (alt): " , alternativeLink

                    links.append(urlLink)
                    altLinks.append(alternativeLink)

        print "Links found: " , len(links)
        downloaded = 0
        for l, al,fn in zip(links,altLinks,fileNames):

            print "\t", downloaded,":", "\t",l,"\t",al

            if("/J1012+5307" in l):
                l = "http://www.epta.eu.org/epndb/ascii/nsk+15/1012+5307/J1012+5307_L81268.txt"
                al = "http://www.epta.eu.org/epndb/ascii/nsk+15/1012+5307/J1012+5307_L81268.txt"
            try:
                response = urllib2.urlopen(l)
            except Exception:
                response = urllib2.urlopen(al)


            html = response.read()
            fpath = self.outputDir + "/" + fn

            if(os.path.exists(fpath) == True):

                for x in range(1, 100):
                    fpath = fpath.replace(".acn","_" + str(x) + ".acn")

                    if(os.path.exists(fpath) == True):
                        continue
                    else:
                        break

            self.appendToFile(fpath,html)
            downloaded +=1

        print "Downloaded: ", downloaded
        #page = open("EPN_Links.html").read()

        #soup = BeautifulSoup.BeautifulSoup(page)

        #div = soup.find('div', id='searchMain')
        #text = ''.join(map(str, div.contents))

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
    EPNDataExtractor_v2().main()