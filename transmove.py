#! /usr/bin/python

import magic
import re
import os
import shutil
import subprocess
import sys
import getopt
import time

def compare_dirs(source,dest,fmt=False):
    '''
    Function to compare files and sub directories between a source
    and destination directory. This function does a strict string
    comparison, and will skip checking empty directories.
    source - (string) The originating directory
    dest   - (string) Destination directory
    fmt    - (string/ an optional extension type to check for,
              list/   i.e. myfile.mp4 in the dest when source has
              bool  ) myfile.avi, fmt would be ".mp4". Optionalally,
                      this can be specified as a list of extension
                      types to check for. i.e. [".mp4",".m4v"]. By
                      default this option is False and no additional
                      types will be checked for

    '''
    #if only a string is provided as a format, convert to a list
    if type(fmt) == type(""):
        fmt = [fmt]
    print("Here is a list of what is not in the destination")
    #walk over the origional source tree
    for x,y,z in os.walk(source):
        #only look for files, skip empty directories
        if len(z) != 0:
            #change the file tree to be rebased for the dest dir
            newdir = os.path.join(dest,x.replace(source,""))
            #actually look at the files in the given directory
            for a in z:
                #start a truth variable to check the truth condition of each ext
                truth = os.path.exists(os.path.join(newdir,a))
                #check to see if additional formats should be concidered
                if fmt:
                    #loop over the provided extensions and check if they exist
                    for ext in fmt:
                        truth += os.path.exists(os.path.join(newdir,os.path.splitext(a)[0]+ext))
                #negate the truth, i.e. if all the paths are false, the file does not exist and
                #the if statment should be evaluated
                if not bool(truth):
                    print(str(os.path.join(newdir,a).encode("utf-8",errors='replace'),encoding='utf-8')+" is missing")



def transcode(source,dest,fmt=".mp4"):
    '''
    Function to transcode all video files in a source directory tree into a destination directory tree.
    Any non video files will be copied into the corresponding locations. This function uses hanbrake
    to do the transcoding. The options specified in this functions seem to be optimal ballance of speed
    and quality. If desired change according to handbrake manual in the runstr variable. This will
    preserve the directory structure of the source in the destination, but will ignore empty directories.
    This function will create a log in your user directory called transmove.log, check after transcodeing
    to ensure there were no errors, as a file compare check will not catch aborted transcodings that were
    written to the destination directory.
    source - (string) The source directory from which the video files will be taken
    dest   - (string) The desination directory the video files will be placed
    fmt    - (string) The video format to transcode to. Default is ".mp4"
    '''
    #handbrake string to be run
    runstr = r'HandBrakeCLI -i "{0}" -o "{1}" --preset="High Profile" -e "x264" --x264-preset="fast" --crop 0:0:0:0 --custom-anamorphic --keep-display-aspect'
    #get the users 'home' directory, will work on windows!
    home = os.path.expanduser("~")
    #set the string for the log
    logfile = os.path.join(home,"transmove.log")
    #open the logfile
    logf    = open(logfile,'a')
    #write the datetime into the logfile
    logf.write(time.strftime("%c")+"\n")
    #create a tracking variable to indicate if there were transcoding errors
    tracking = 0
    #loop over the directory structure
    for x,y,z in os.walk(source):
        #only look in directories which are not empty
        if len(z) != 0:
            #generate the full path of destination directory
            newdir = os.path.join(dest,x.replace(source,""))
            #if the new directory does not exist, then create it
            if not os.path.exists(newdir):
                os.makedirs(newdir)
            #loop over all the files in a directory
            for a in z:
                #print out the directory and file being worked on
                print(x.replace(source,""),":",a)
                #try statement if the transcode fails
                try:
                    #check if the file is a video
                    if magic.from_file(os.path.join(x,a),mime=True).startswith(b"video"):
                        #create the new filename
                        newname = os.path.splitext(a)[0]+'.mp4'
                        #check if the file already exists,if so skip, this is so the command can be rerun if interrupted
                        if not os.path.exists(os.path.join(newdir,newname)):
                            #log the start of the transcode
                            logf.write(os.path.join(x,a)+' start\n')
                            #run the actual transcoding on the file
                            subprocess.check_call(runstr.format(os.path.join(x,a),os.path.join(newdir,newname)),shell=True)
                            #log when the transcode completes, useful to detect failed transcodes!
                            logf.write(os.path.join(x,a)+' end\n')
                        #if the file already exists then skip it
                        else:
                            print("Done, skipping")
                    #if the file is not a movie file, then simply copy the file to the new location
                    else:
                        shutil.copy2(os.path.join(x,a),os.path.join(newdir,a))
                #if something in the transcode step fails, print the exception
                except Exception as e:
                    print(e)
                    tracking += 1
    #close our log file
    logf.close()
    #if there were transcoding errors indicate such to the user
    if tracking != 0:
        print("There were transcoding errors, please check the log to make sure all files were completed successfully")
    #as a final step run the directory comparison to print any missing files
    compare_dirs(source,dest,fmt=fmt)

def print_help():
    help_str = """
    This is a program which will take a source directory containing videos and
    transcode them using handbrake into an alternative directory. The process will
    preserve all subdirectory structure. Any files which are not video files will
    be copied into their corresponding directories. The process is logged in the
    the users home directory as transmove.log. After the transcode, the directories
    will be compared to ensure all files have been moved. There however is a
    possibility that the transcode failed after creating the file, so if indicated
    the user should check the log output to ensure all files completed successfully.
    Using options to this program the check function can be run indipendently of the
    transcoding. This allows comparing before a run to check nessessity. It also
    allows the comparing of filesystems which may contain no video files, but which
    need comparison. This program is known to have issues if your filenames have non
    standard utf-8 characters. These will be flagged in the file check.
    Below is the syntax of the program:

    transmove.py [-h --help -c --check -f --format -a --alternative] source destination

    only the source and destination are required, each of the other switches are
    optional arguments described below:
    -h, --help                 Print this help message
    -c, --check                Only run the check of the souce and destination
    -f, --format <string>      Format of the transcoded videos, defaults to .mp4, specify
                               alternatives in .abc format
    -a, --alternative <string> Specify alternative file formats to accept in file comparison.
                               i.e. if the source is myfile.avi, accept myfile.mp4 in the
                               destination, else the file check will indicate myfile.avi is
                               missing. Multiple file types may be specified by separating
                               with commas, i.e. .mp4,.mkv do not put spaces around the
                               commas.
    """
    print(help_str)

if __name__ == "__main__":
    #parse the command line arguments and exit if there is an error
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hcf:a:",["help","check","format","alternative"])
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)
    #set up the default values for some variables
    #default format
    fmt       = '.mp4'
    #dont only run check by default
    onlycheck = False
    #there are no default alternative extension to check
    hassub    = False
    #actually parse the options
    for o,a in opts:
        #print help if asked
        if o in ("-h","--help"):
            print_help()
            sys.exit(0)
        #only execute a check
        elif o in ("-c","--check"):
            onlycheck = True
        #specify a file type to transcode
        elif o in ("-f",'--format'):
            fmt = a
        #specify alternative filetypes to accept in compare
        elif o in ("-a","--alternative"):
            subopt = a
            hassub = True
        #catch remaining errors
        else:
            assert False, "unhandled option"
    if len(args) < 2:
        print("Source and destination are required")
        sys.exit(2)
    #if the user only wants to check directories run and exit
    if onlycheck:
        #if there are alternative filetypes parse
        if hassub:
            try:
                fmtstr = subopt.split(",")
            except:
                print("Error parsing substitute string, please check and re-run")
        else:
            fmtstr = False
        #run the compare
        compare_dirs(args[0],args[1],fmtstr)
        #exit
        sys.exit(0)
    #run the actual transcode
    transmove(args[0],args[1],fmt=fmt)
