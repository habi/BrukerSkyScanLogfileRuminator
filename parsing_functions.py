import re
import datetime


# Convenience functions
def fulllog(logfile):
    """Print the full log file"""
    with open(logfile, 'r') as f:
        for line in f:
            print(line.strip())
    return()


# How is the machine set up in general?
def scanner(logfile, verbose=False):
    hardwareversion = []
    with open(logfile, 'r') as f:
        for line in f:
            if 'Scanner' in line:
                if verbose:
                    print(line)
                # Sometimes it's SkyScan, sometimes Skyscan
                # We thus have to regex it :)
                machine = re.split('Sky.can', line)[1].strip()
            if 'Hardware' in line:
                if verbose:
                    print(line)
                hardwareversion = line.split('=')[1].strip()
    if hardwareversion:
        return('SkyScan %s (Version %s)' % (machine, hardwareversion))
    else:
        return('SkyScan ' + machine)


def controlsoftware(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Software' in line and 'Version' in line:
                if verbose:
                    print(line)
                # Sometimes it's 'Software Verion=Number'
                # Sometimes it's 'Software=Version Number' (with a space in Number)
                version = line.split('=')[1].strip().strip('Version ').replace(". ", ".")
    return(version)


def source(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Source Type' in line:
                if verbose:
                    print(line)
                source = line.split('=')[1].strip()
                if 'HAMAMA' in source:
                    # Split the string at '_L' to separate HAMAMATSU_L118
                    # Then capitalize HAMAMATSU and join the strings back
                    # with ' L' to get the beginning of the reference back
                    source = ' L'.join([s.capitalize() for s in source.split('_L')])
    return(source)


# How did we set up the scan?
def voltage(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Voltage' in line:
                if verbose:
                    print(line)
                V = float(line.split('=')[1])
    return(V)


def current(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Source Current' in line:
                if verbose:
                    print(line)
                A = float(line.split('=')[1])
    return(A)


def whichfilter(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Filter=' in line:
                if verbose:
                    print(line)
                fltr = line.split('=')[1].strip().replace('  ', ' ')
                if fltr == 'No Filter':
                    fltr = False
    return(fltr)


def camera(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Camera T' in line or 'Camera=' in line:
                if verbose:
                    print(line)
                cam = line.split('=')[1].strip().strip(' camera')
    return(cam)


def numproj(logfile, verbose=False):
    """How many projections are recorded?"""
    with open(logfile, 'r') as f:
        for line in f:
            # Sometimes it's 'Number of Files'
            # Sometimes it's 'Number Of Files'
            if 'Number' in line and 'f Files' in line:
                if verbose:
                    print(line)
                numproj = int(line.split('=')[1])
    return(numproj)


def projectionsize(logfile):
    """How big did we set the camera?"""
    with open(logfile, 'r') as f:
        for line in f:
            # Sometimes it's 'Number of'
            # Sometimes it's 'Number Of'
            if 'Number' in line and 'f Rows' in line:
                y = int(line.split('=')[1])
            if 'Number' in line and 'f Columns' in line:
                x = int(line.split('=')[1])
    return(x, y)


def rotationstep(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Rotation Step' in line:
                if verbose:
                    print(line)
                rotstep = float(line.split('=')[1])
    return(rotstep)


def pixelsize(logfile, verbose=False, rounded=False):
    """Get the pixel size from the scan log file"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'Image Pixel' in line and 'Scaled' not in line:
                if verbose:
                    print(line)
                pixelsize = float(line.split('=')[1])
    if rounded:
        return(round(pixelsize, 1))
    else:
        return(pixelsize)


def stacks(logfile, verbose=False):
    with open(logfile, 'r') as f:
        numstacks = 0
        for line in f:
            if 'b-scan' in line:
                if verbose:
                    print(line)
                # The 'Sub-scan scan length' is listed in the log file
                # We simply select the last one, and add 1,
                # since Bruker also starts to count at zero
                numstacks = int(line.split('[')[1].split(']')[0])
            else:
                # If only one stack, then there's nothing in the log file
                numstacks = 0
    return(numstacks + 1)


def overlapscan(logfile, verbose=False):
    wide = None
    with open(logfile, 'r') as f:
        for line in f:
            if 'orizontal' in line and 'ffset' in line and 'osition' in line:
                if verbose:
                    print(line)
                wide = int(line.split('=')[1])
                if wide == 1:
                    wide = False
    return(wide)


def threesixtyscan(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if '360 Rotation' in line:
                if verbose:
                    print(line)
                threesixty = line.split('=')[1]
                print(threesixty)
                if 'YES' in threesixty:
                    threesixty = True
                elif 'NO' in threesixty:
                    threesixty = False
    return(threesixty)


def exposure(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Exposure' in line:
                if verbose:
                    print(line)
                exp = int(line.split('=')[1])
    return(exp)


def averaging(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Avera' in line:
                if verbose:
                    print(line)
                details = line.split('=')[1]
                if 'ON' in details:
                    # https://stackoverflow.com/a/4894156/323100
                    avg = int(details[details.find("(") + 1:details.find(")")])
                else:
                    avg = False
    return(avg)


def randommovement(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Random' in line:
                if verbose:
                    print(line)
                details = line.split('=')[1]
                if 'ON' in details:
                    # https://stackoverflow.com/a/4894156/323100
                    rndm = int(details[details.find("(") + 1:details.find(")")])
                else:
                    rndm = False
    return(rndm)


def duration(logfile, verbose=False):
    '''Returns scantime in *seconds*'''
    with open(logfile, 'r') as f:
        for line in f:
            if 'Scan duration' in line and 'Estimated' not in line:
                if verbose:
                    print(line)
                duration = line.split('=')[1].strip()
    # Sometimes it's '00:24:26', sometimes '0h:52m:53s' :-/
    if 'h' in duration:
        scantime = datetime.datetime.strptime(duration, '%Hh:%Mm:%Ss')
    else:
        scantime = datetime.datetime.strptime(duration, '%H:%M:%S')
    return((scantime-datetime.datetime(1900, 1, 1)).total_seconds())


# How did we reconstruct the samples?
def version(logfile, verbose=False):
    """Return reconstruction program an its version"""
    # Is only written to log files if reconstructed, thus set empty first
    program = None
    version = None
    with open(logfile, 'r') as f:
        for line in f:
            if 'Reconstruction Program' in line:
                if verbose:
                    print(line)
                program = line.split('=')[1].strip()
            if 'Program Version' in line:
                if verbose:
                    print(line)
                version = line.split('sion:')[1].strip()
    return(program, version)


def ringremoval(logfile, verbose=False):
    # Is only written to log files if reconstructed, thus set empty first
    ring = None
    with open(logfile, 'r') as f:
        for line in f:
            if 'Ring' in line:
                if verbose:
                    print(line)
                ring = int(line.split('=')[1].strip())
    return(ring)


def beamhardening(logfile, verbose=False):
    # Is only written to log files if reconstructed, thus set empty first
    bh = None    
    with open(logfile, 'r') as f:
        for line in f:
            if 'ardeni' in line:
                if verbose:
                    print(line)
                bh = int(line.split('=')[1].strip())
    return(bh)