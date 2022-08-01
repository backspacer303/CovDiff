#!/usr/bin/python

import sys
import os
import subprocess
import argparse
import shutil
import json
import gzip
import time


class CodeCoverage:

    ID = 1

    def __init__(self, sourceFile, test, command, commandArgs, coverageInfoDest):
        self.sourceFile = sourceFile
        self.test = test
        self.ID = CodeCoverage.ID
        self.command = command
        self.commandArgs = commandArgs
        self.coverageInfoDest = os.path.join(coverageInfoDest, "")

        self.sourceFileNameWithExt = None
        self.sourceFileNameWithNoExt = None
        self.sourceFileRoot = None
        self.sourceFileExt = None

        self.gcnoFileName = None
        self.gcdaFileName = None

        self.report = None
        self.coveredLines = None
        self.lineCount = None        
        self.coveredFunctions = None
        self.functionCount = None

        self.parseSourceFileName()

        CodeCoverage.ID = CodeCoverage.ID + 1

    def parseSourceFileName(self):
        if not os.path.exists(self.sourceFile):
            raise Exception("ERROR: source file does not exist")
        self.sourceFileNameWithExt = os.path.basename(self.sourceFile)
        (self.sourceFileRoot, self.sourceFileExt) = os.path.splitext(self.sourceFile)
        self.sourceFileNameWithNoExt = os.path.basename(self.sourceFileRoot)

    def makeCoverageInfoDestDir(self):
        if not os.path.exists(self.coverageInfoDest):
            try:
                os.mkdir(self.coverageInfoDest)
            except OSError as e:
                print(e) 

    def copyGcno(self):
        gcnoFileName_tmp = self.sourceFileRoot + '.gcno'
        if not os.path.exists(gcnoFileName_tmp):
            raise Exception("ERROR: .gcno file does not exist")
        self.makeCoverageInfoDestDir()        
        shutil.copy2(gcnoFileName_tmp, self.coverageInfoDest + self.sourceFileNameWithNoExt + '_test' + str(self.ID) + '.gcno')
        self.gcnoFileName = self.coverageInfoDest + self.sourceFileNameWithNoExt + '_test' + str(self.ID) + '.gcno'

    def moveGcda(self, gcda):
        shutil.move(gcda, self.coverageInfoDest + self.sourceFileNameWithNoExt + '_test' + str(self.ID) + '.gcda')
        self.gcdaFileName = self.coverageInfoDest + self.sourceFileNameWithNoExt + '_test' + str(self.ID) + '.gcda'


    def readArchive(self):
        archiveName = self.coverageInfoDest + self.sourceFileNameWithExt + ".gcov.json.gz"        
        if not os.path.exists(archiveName):
            raise Exception("ERROR: archive that contains json report does not exist")

        with gzip.open(archiveName, 'rb') as f:
            self.report = json.load(f)
        
        os.remove(archiveName)

    def runTest(self):
                
        processsRetVal = subprocess.run([self.command, self.test] + self.commandArgs)
        
        processsRetVal.check_returncode()

        gcdaFileName_tmp = self.sourceFileRoot + '.gcda'    
        if not os.path.exists(gcdaFileName_tmp):
            raise Exception("ERROR: .gcda file does not exist, after running test " + self.test + " " + str(self.ID))                
        
        self.moveGcda(gcdaFileName_tmp)

    def runGcov(self):        

        currentWorkDir = os.getcwd()
        os.chdir(self.coverageInfoDest)  #kako bi se json fajl generisao u dest_dir nakon poziva gcov      
        
        (root, ext) = os.path.splitext(self.gcdaFileName)
        searchPath = os.path.basename(root)
        processsRetVal = subprocess.run(["gcov", "--json-format", "--branch-probabilities", "--object-file", searchPath, self.sourceFile])        
        
        processsRetVal.check_returncode()

        os.chdir(currentWorkDir)
        
        self.readArchive()
                    
    def saveJsonReport(self):
        jsonReportFileName = self.coverageInfoDest + "report_test" + str(self.ID) + ".json"
        with open(jsonReportFileName, 'w') as f:
            json.dump(self.report, f, indent=4)

    def parseReport(self):
        
        self.coveredLines = set()
        self.coveredFunctions = set()        

        for key in self.report:

            if key == "files":
            
                fileInfo = self.report[key][0]
                
                lines = fileInfo["lines"]
                for l in lines:
                    if l["count"] != 0:
                        self.coveredLines.add(l["line_number"])

                functions = fileInfo["functions"]
                for f in functions:
                    if f["execution_count"] != 0:
                        self.coveredFunctions.add(f["name"])

    def runCodeCoverage(self):
        self.copyGcno()
        self.runTest()
        self.runGcov()
        self.saveJsonReport()
        self.parseReport()

def parse_program_args(parser):
    parser.add_argument('source_file', metavar='source_file', action="store",
                        help='the path to the source file to be tested')
    parser.add_argument('test1', metavar='test1', action="store",
                        help='the first test to be run (ll file)')
    parser.add_argument('test2', metavar='test2', action="store",
                        help='the second test to be run (ll file)')
    parser.add_argument('coverage_dest', metavar='coverage_dest', action="store",
                        help='directory for storing code coverage information')
    parser.add_argument('command', metavar='command', action="store",
                        help='command to run the tests')
    parser.add_argument('command_arg', metavar='command_arg', action="store", nargs='*',
                        help='command arguments must be specified in the form -<option>')
    return parser.parse_args()

def Main():
    
    parser = argparse.ArgumentParser(description='Run llvm tests and generate code coverage diff.')
    args = parse_program_args(parser)    
    
    #TODO Mozda premestiti u konstruktor klase...
    for i in range(0,len(args.command_arg)):
        if not args.command_arg[i].startswith("-"):
            args.command_arg[i] = "-" + args.command_arg[i]

    test1 = CodeCoverage(args.source_file, args.test1, args.command, args.command_arg, args.coverage_dest)    
    test2 = CodeCoverage(args.source_file, args.test2, args.command, args.command_arg, args.coverage_dest)
    
    try:
        test1.runCodeCoverage()
    except Exception as e:
        print(e)
        exit()

    #Samo za debagovanje
    #print("Sleep...")
    #time.sleep(5)

    try:
        test2.runCodeCoverage()
    except Exception as e:
        print(e)
        exit()

    print("\n\n================== Report ========================")
    print("Lines covered with test1 but not test2:")
    print(test1.coveredLines.difference(test2.coveredLines))
    print("Lines covered with test2 but not test1:")
    print(test2.coveredLines.difference(test1.coveredLines))
    print("Lines covered with both tests:")
    print(test1.coveredLines.intersection(test2.coveredLines))
    print("==================================================")

    
if __name__ == "__main__":
  Main()