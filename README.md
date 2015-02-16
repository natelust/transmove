#Transmove

This is a python script developed to satisfy a need to bulk convert a directory
containing video files. There are many similar scripts available which convert
files in place (leaving them in the same directory). This program however will
create a new directory tree which mirrors the original, as well as copy any non
video files into the corresponding directory under the new tree.

The upon completion the program will check both directory trees, and report any
missing files which may have failed for some reason. Additionally the whole
process is logged out to a file.

The file tree functionality of the program can also be used independently of
the transcoding function. This allows the user to compare two directory trees
regardless of the file types, which may be useful for files such as images.
Optionally the file compare function takes alternative file types to search
for, i.e. by specifying alternative file type '.mp4' myvideo.avi will match
myvideo.mp4. More than one alternative file type may also be specified.

This program is fully resumable, with the caveat that if it is interrupted
during a transcoding operation, the program has no way to know if the transcode
successfully completed. This will be evident in the log as a transcode
operation will have been started but not finished. It is important that the
user delete the uncompleted video before re-running the script or it will be
skipped. Future versions of this program may eliminate this requirement, and
pull requests which fix this are welcome.

Basic usage of this program is as follows:
transmove.py source destination 

Where source is the directory to be transcoded and destination is where the
results are to be placed. Full documentation is found below, or with the -h or
--help options in the program.

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


This program requires the python programming language to be installed, which
should be default on Os X and *nix environments, but will need installed on
windows. In the future an exe may be provided for windows users. In addtion to
the core language of python this program requires python-magic to be installed
for file type identification. Future versions may eliminate this requirement.
This program also requires handbrake command line program to be installed for
the transcoding operation. 
