##### Version_diffs checks for any differences among the different versions 
##### of an API by scanning through the GIT directory of the API. The desired 
##### GIT directory's location, the version number from which the version 
##### history has to be checked for variations and the file name and line number 
##### where the API's versions have to be checked for version differences are 
##### mentioned by the user. Version_diffs helps to find the existence of any
##### version difference from the initial version till the user desired version.

import subprocess, optparse, os
from subprocess import Popen, PIPE, STDOUT


def get_proc_str(cmd):
    proc = Popen(cmd, stdout = PIPE, stderr = STDOUT, shell = True)
    output_str = proc.stdout.read()
    return output_str.strip()


##### The function generate_diffs generates the differences between every 
##### consecutive version of the API
def generate_diffs(repository, filename, line_number, version_num = None):
    os.chdir(repository) # Navigate into the git directory
    cmd = 'git log' # To collect the commit IDs to spot version differences
    output_list = get_proc_str(cmd).split("\n")
    commitlst = []
    
##### To generate a list of all commit IDs (version numbers)
    for line in output_list:
        line.strip()
        if line.startswith("commit "):
            commitlst.append(line.strip("commit "))
    
##### If a version number is not mentioned or not known, check for differences
##### from the initial version till the latest version.
    if version_num:
        commitlst = commitlst[commitlst.index(version_num):]

    if len(commitlst) <= 1:
		print "Commit list too short"
		exit()

    for index in range(len(commitlst) - 1):
        diff_to_find = ("git diff " + commitlst[index] + " " + commitlst[index + 1])
        print diff_to_find
        diff_between = get_proc_str(diff_to_find)
        search_in_diff(diff_between, filename, line_number)
        print "\n****************************************************\n"
        

##### The search_in_diff function searches for the presence of difference
##### in a particular file in the GIT directory and a particular line
def search_in_diff(diff_between, filename, line_number):
    line_diff = diff_between.split("\n")
    try:
        for index in range(len(line_diff) - 1):
            line = line_diff[index]
            if line.startswith("---"):
                diff_filename = line.strip("--- ").split("/", 1)[-1]
                index = index + 2 #skip --- line and +++ line
                if (filename == diff_filename):
					if index < len(line_diff):
						nextline = line_diff[index] # @@ line
					else:
						break

##### Versions with more than one chunk of differences are addressed.
					while not nextline.startswith("---"):
						if nextline.startswith("@@"):
							remove, add = nextline.strip("@@ ").split(" @@")[0].split(" ")
							linediff, numoflines = [int(x) for x in remove.strip("-").split(",")]
							if int(linediff) <= line_number and line_number <= (int(linediff) + int(numoflines)):
								print diff_filename, linediff, numoflines
							else:
								print "no match"
						index = index + 1
						if index < len(line_diff):
							nextline = line_diff[index]
						else:
							break
                else:
					print "no match"               
    except StopIteration:
        pass
    
    
if __name__ == '__main__':
    parser = optparse.OptionParser("usage: %prog [options] repository filename line_number")
    parser.add_option("-v", "--version", type = "string", help = "Version number", dest = "end_version")
    (opts, args) = parser.parse_args()

    generate_diffs(args[0], args[1], int(args[2]), version_num = opts.end_version)
    
