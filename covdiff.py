#!/usr/bin/python
import argparse

from report_display import ReportDisplayGenerator, HtmlReportDisplay
from project_code_coverage import ProjectCodeCoverage
from summary_report import MiniReport

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
    parser.add_argument('--report-formats', metavar='report_formats', action="store", default="html",
                        help='coma separated list of report formats to be created')
    parser.add_argument('--summary-reports', metavar='summary_reports', action="store", default="minireport",
                        help='coma separated list of summary reports to be created')
    return parser.parse_args()

def Main():

    # Parsiranje argumenata komandne linije.
    parser = argparse.ArgumentParser(description='Run tests and generate code coverage diff.')
    args = parse_program_args(parser)
    
    # Dodavanje "-" argumentima komande za pokretanje testova.
    for i in range(0,len(args.command_arg)):
        if not args.command_arg[i].startswith("-") and args.command_arg[i-1] != '-o':
            args.command_arg[i] = "-" + args.command_arg[i]

    # Liste sumarnih izvestaja koje je potrebno formirati.
    summaryReportsList1 = []
    summaryReportsList2 = []
    for summary_report in args.summary_reports.split(","):
        if summary_report == 'minireport':
            summaryReportsList1.append(MiniReport())
            summaryReportsList2.append(MiniReport())
        else:
            print("Summary report type \"" + summary_report +  "\" not recognized! Skipping...")

    # Prikupljanje i cuvanje informacija o pokrivenosti koda projekta prvim i drugim testom.
    projectCCTest1 = ProjectCodeCoverage(args.directory_path, args.test1, args.command, args.command_arg,
                                         args.coverage_dest, args.source_file, args.object_path, summaryReportsList1)
    projectCCTest2 = ProjectCodeCoverage(args.directory_path, args.test2, args.command, args.command_arg,
                                         args.coverage_dest, args.source_file, args.object_path, summaryReportsList2)

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

    # Lista formata izvestaja koje je potrebno kreirati.
    reportDisplayList = []
    for report_format in args.report_formats.split(","):
        if report_format == "html":
            reportDisplayList.append(HtmlReportDisplay(projectCCTest1, projectCCTest2, args.coverage_dest))
        else:
            print("Report format \"" + report_format + "\" not recognized! Skipping...")

    # Generisanje prikaza razlika u pokrivenosti koda testovima u zadatim formatima.
    generator = ReportDisplayGenerator(reportDisplayList, projectCCTest1, projectCCTest2, numOfWorkers=4)
    generator.generate()

if __name__ == "__main__":
  Main()

