#!/usr/bin/python
import argparse

from html_report import HtmlReport
from project_code_coverage import ProjectCodeCoverage

def parse_program_args(parser):
    parser.add_argument('directory_path', metavar='directory_path', action="store",
                    help="directory to search for all files affected by the test")
    parser.add_argument('--source-file', metavar='source_file', action="store",
                        help='the path to the source file of intrest')
    parser.add_argument('--object-path',  metavar='object_path', action="store",
                        help="the path to the object file corresponding to the given source file, if known")
    parser.add_argument('test1', metavar='test1', action="store",
                        help='the first test to be run')
    parser.add_argument('test2', metavar='test2', action="store",
                        help='the second test to be run')
    parser.add_argument('coverage_dest', metavar='coverage_dest', action="store",
                        help='directory for storing code coverage information')
    parser.add_argument('command', metavar='command', action="store",
                        help='command to run the tests (specify "./" if test is already an executable)')
    parser.add_argument('command_arg', metavar='command_arg', action="store", nargs='*',
                        help='command arguments')                        
    return parser.parse_args()

def Main():
    
    # Parsiranje argumenata komandne linije.
    parser = argparse.ArgumentParser(description='Run tests and generate code coverage diff.')
    args = parse_program_args(parser)
    
    # Dodavanje "-" argumentima komande za pokretanje testova.
    for i in range(0,len(args.command_arg)):
        if not args.command_arg[i].startswith("-") and args.command_arg[i-1] != '-o':
            args.command_arg[i] = "-" + args.command_arg[i]
    
    # Prikupljanje i cuvanje informacija o pokrivenosti koda projekta prvim i drugim testom.
    projectCCTest1 = ProjectCodeCoverage(args.directory_path, args.test1, args.command, args.command_arg, args.coverage_dest, args.source_file, args.object_path)
    projectCCTest2 = ProjectCodeCoverage(args.directory_path, args.test2, args.command, args.command_arg, args.coverage_dest, args.source_file, args.object_path)
    
    try:
        projectCCTest1.runProjectCodeCoverage()
    except Exception as e:
        print(e)
        exit()

    try:
        projectCCTest2.runProjectCodeCoverage()
    except Exception as e:
        print(e)
        exit()

    # Generisanje prikaza razlika u pokrivenosti koda testovima u formatu html.
    htmlReport = HtmlReport(projectCCTest1, projectCCTest2, args.coverage_dest)
    htmlReport.generateHtml()
    
if __name__ == "__main__":
  Main()

