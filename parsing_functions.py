import re
import datetime
import pandas


# Convenience functions
def fulllog(logfile):
    """Print the full log file"""
    with open(logfile, 'r') as f:
        for line in f:
            print(line.strip())
    return ()


def timeformat(tdelta, fmt):
    # From https://stackoverflow.com/a/8907269/323100
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


# How is the machine set up in general?
def scanner(logfile, verbose=False):
    machine = None
    hardwareversion = False
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
        return 'SkyScan %s (Version %s)' % (machine, hardwareversion)
    else:
        return 'SkyScan ' + machine


def controlsoftware(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Software' in line and 'Version' in line:
                if verbose:
                    print(line)
                # Sometimes it's 'Software Verion=Number'
                # Sometimes it's 'Software=Version Number' (with a space in Number)
                version = (
                    line.split('=')[1].strip().strip('Version ').replace(". ", ".")
                )
    return str(version)


def source(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Source Type' in line:
                if verbose:
                    print(line)
                whichsource = line.split('=')[1].strip()
                if 'HAMAMA' in whichsource:
                    # Split the string at '_L' to separate HAMAMATSU_L118
                    # Then capitalize HAMAMATSU and join the strings back
                    # with ' L' to get the beginning of the reference back
                    whichsource = ' L'.join(
                        [s.capitalize() for s in whichsource.split('_L')]
                    )
    return whichsource


# How did we set up the scan?
def voltage(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Voltage' in line:
                if verbose:
                    print(line)
                V = float(line.split('=')[1])
    return V


def current(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Source Current' in line:
                if verbose:
                    print(line)
                A = float(line.split('=')[1])
    return A


def spotsize(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Source spot size' in line:
                if verbose:
                    print(line)
                whichspotsize = line.split('=')[1].strip()
    return whichspotsize


def beamposition(logfile, verbose=False):
    position = None
    with open(logfile, 'r') as f:
        for line in f:
            if 'Beam position' in line:
                if verbose:
                    print(line)
                position = int(line.split('=')[1])
    return position


def whichfilter(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Filter=' in line:
                if verbose:
                    print(line)
                fltr = line.split('=')[1].strip().replace('  ', ' ')
                if fltr == 'No Filter':
                    fltr = None
    return fltr


def camera(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Camera T' in line or 'Camera=' in line:
                if verbose:
                    print(line)
                cam = line.split('=')[1].strip().strip(' camera')
    return cam


def cameraposition(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Camera' in line and 'osition=' in line:
                if verbose:
                    print(line)
                camposition = line.split('=')[1].strip()
    return camposition


def distance_source_to_detector(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Camera to Source' in line:
                if verbose:
                    print(line)
                sdd = line.split('=')[1].strip()
    return sdd


def distance_source_to_sample(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Object to Source' in line:
                if verbose:
                    print(line)
                ssd = line.split('=')[1].strip()
    return ssd


def numproj(logfile, verbose=False):
    """How many projections are recorded?"""
    with open(logfile, 'r') as f:
        for line in f:
            # Sometimes it's 'Number of Files'
            # Sometimes it's 'Number Of Files'
            if 'Number' in line and 'f Files' in line:
                if verbose:
                    print(line)
                numberofprojections = int(line.split('=')[1])
    return numberofprojections


def projection_size(logfile):
    """How big did we set the camera?"""
    with open(logfile, 'r') as f:
        for line in f:
            # Sometimes it's 'Number of'
            # Sometimes it's 'Number Of'
            if 'Number' in line and 'f Rows' in line:
                y = int(line.split('=')[1])
            if 'Number' in line and 'f Columns' in line:
                x = int(line.split('=')[1])
    return (x, y)


def rotationstep(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Rotation Step' in line:
                if verbose:
                    print(line)
                rotstep = float(line.split('=')[1])
    return rotstep


def pixelsize(logfile, verbose=False, rounded=False):
    """Get the pixel size from the scan log file"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'Image Pixel' in line and 'Scaled' not in line:
                if verbose:
                    print(line)
                pixelsize = float(line.split('=')[1])
    if rounded:
        return round(pixelsize, 2)
    else:
        return pixelsize


def stacks(logfile, verbose=False):
    with open(logfile, 'r') as f:
        # If only one stack, then Bruker writes nothing to the log file
        numstacks = 0
        for line in f:
            if 'Sub-scan scan length' in line:
                if verbose:
                    print(line)
                # The 'Sub-scan scan length' is listed in the log file
                # We simply select the last one, and add 1,
                # since Bruker also starts to count at zero
                numstacks = int(line.split('[')[1].split(']')[0])
    return numstacks + 1


def overlapscan(logfile, verbose=False):
    wide = False
    with open(logfile, 'r') as f:
        for line in f:
            if 'orizontal' in line and 'ffset' in line and 'osition' in line:
                if verbose:
                    print(line)
                wide = int(line.split('=')[1])
                if wide == 1:
                    wide = False
    return wide


def threesixtyscan(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if '360 Rotation' in line:
                if verbose:
                    print(line)
                threesixty = line.split('=')[1]
                if 'YES' in threesixty:
                    threesixty = True
                elif 'NO' in threesixty:
                    threesixty = False
    return threesixty


def exposuretime(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Exposure' in line:
                if verbose:
                    print(line)
                exp = int(line.split('=')[1])
    return exp


def averaging(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Avera' in line:
                if verbose:
                    print(line)
                details = line.split('=')[1]
                if 'ON' in details:
                    # https://stackoverflow.com/a/4894156/323100
                    avg = int(details[details.find("(") + 1 : details.find(")")])
                else:
                    avg = None
    return avg


def randommovement(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'Random' in line:
                if verbose:
                    print(line)
                details = line.split('=')[1]
                if 'ON' in details:
                    # https://stackoverflow.com/a/4894156/323100
                    rndm = int(details[details.find("(") + 1 : details.find(")")])
                else:
                    rndm = None
    return rndm


def duration(logfile, prose=False, verbose=False):
    '''Returns scan duration in *seconds*'''
    with open(logfile, 'r') as f:
        for line in f:
            if 'Scan duration' in line and 'Estimated' not in line:
                if verbose:
                    print(line)
                duration_log = line.split('=')[1].strip()
    # Sometimes it's '00:24:26', sometimes '0h:52m:53s' :-/
    if 'h' in duration_log:
        # Thanks to ChatGPT for the help with Regex parsing and grouping
        pattern = r"(?:(\d+)h)(?::?(\d+)m)(?::?(\d+)s)"
    else:
        pattern = r"(?:(\d+))(?::?(\d+))(?::?(\d+))"
    # Matches are grouped; hours in group 1, minutes in group 2 and seconds in group 3
    matches = re.match(pattern, duration_log)
    # Create a timedelta object with relevant matches in relevant data
    time_delta = datetime.timedelta(
        hours=int(matches.group(1)),
        minutes=int(matches.group(2)),
        seconds=int(matches.group(3)),
    )
    if not time_delta.total_seconds():
        print('No time could be parsed from', logfile)
        print('The string found was', duration_log)
    if prose:
        if verbose:
            print(time_delta)
        # Return Timedelta object
        # We can then split it with time_delta.components.hour, time_delta.components.minute, time_delta.components.seconds
        # Hat tip to https://stackoverflow.com/a/71407740/323100
        return time_delta
    else:
        if verbose:
            print(time_delta.total_seconds())
        # Return the scan time in seconds
        return time_delta.total_seconds()


def scandate(logfile, verbose=False):
    """When did we scan the Sample?"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'Study Date and Time' in line:
                if verbose:
                    print('Found "date" line: %s' % line.strip())
                datestring = line.split('=')[1].strip().replace('  ', ' ')
                if verbose:
                    print('The date string is: %s' % datestring)
                try:
                    # Try to read explicitly
                    date = pandas.to_datetime(datestring, format='%d %b %Y %Hh:%Mm:%Ss')
                except ValueError:
                    # If we fail, try to figure it out automatically
                    date = pandas.to_datetime(datestring)
                if verbose:
                    print('Parsed to: %s' % date)
    return date


# How did we reconstruct the scan?
def nreconversion(logfile, verbose=False):
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
            elif 'Program Version' in line:
                if verbose:
                    print(line)
                version = line.split('sion:')[1].strip()
    return (program, version)


def ringremoval(logfile, verbose=False):
    """Did we use ring removal?"""
    # Is only written to log files if reconstructed, thus set empty first
    ring = None
    with open(logfile, 'r') as f:
        for line in f:
            if 'Ring' in line:
                if verbose:
                    print(line)
                ring = int(line.split('=')[1].strip())
                if ring == 0:
                    ring = None
    return ring


def beamhardening(logfile, verbose=False):
    """Did we set a beam hardening correction?"""
    # Is only written to log files if reconstructed, thus set empty first
    bh = None
    with open(logfile, 'r') as f:
        for line in f:
            if 'ardeni' in line:
                if verbose:
                    print(line)
                bh = int(line.split('=')[1].strip())
                if bh == 0:
                    bh = None
    return bh


def defectpixelmasking(logfile, verbose=False):
    """Check the 'defect pixel masking' setting"""
    dpm = None
    with open(logfile, 'r') as f:
        for line in f:
            if 'defect pixel mask' in line:
                if verbose:
                    print(line)
                dpm = int(line.split('=')[1].strip())
                if dpm == 0:
                    dpm = None
    return dpm


def larger_than_fov(logfile, verbose=False):
    """Did we set the 'object larger than field of view' option"""
    ltfov = False
    with open(logfile, 'r') as f:
        for line in f:
            if 'Object Bigger' in line:
                if verbose:
                    print(line)
                ltfov = line.split('=')[1].strip()
    if ltfov == 'ON':
        return True
    elif ltfov == 'OFF':
        return False


def postalignment(logfile, verbose=False):
    """Read the postalignment value"""
    pav = None
    with open(logfile, 'r') as f:
        for line in f:
            if 'post alignment' in line:
                if verbose:
                    print(line)
                pav = float(line.split('=')[1].strip())
    return pav


def reconstruction_grayvalue(logfile, verbose=False):
    grayvalue = None
    """How did we map the brightness of the reconstructions?"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'Maximum for' in line:
                if verbose:
                    print(line)
                grayvalue = float(line.split('=')[1])
    return grayvalue


def reconstruction_size(logfile, verbose=False):
    x = None
    y = None
    """How large are the resulting reconstructions?"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'Result' in line and 'Width' in line:
                if verbose:
                    print(line)
                x = int(line.split('=')[1])
            elif 'Result' in line and 'Height' in line:
                if verbose:
                    print(line)
                y = int(line.split('=')[1])
    return (x, y)


def reconstruction_rotation(logfile, verbose=False):
    rotation = None
    """How did we rotate the reconstructions? (NRecons "CS Static Rotation (deg)" value)"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'CS Static Rotation Total' in line:
                if verbose:
                    print(line)
                rotation = float(line.split('=')[1])
    return rotation


def slice_first(logfile, verbose=False):
    first = None
    """What's the first slice?"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'First Section' in line:
                if verbose:
                    print(line)
                first = int(line.split('=')[1])
    return first


def slice_last(logfile, verbose=False):
    last = None
    """What's the last slice?"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'Last Section' in line:
                if verbose:
                    print(line)
                last = int(line.split('=')[1])
    return last


def slice_number(logfile, verbose=False):
    number = None
    """How many slices can we expect on disk?"""
    with open(logfile, 'r') as f:
        for line in f:
            if 'Sections Count' in line:
                if verbose:
                    print(line)
                number = int(line.split('=')[1])
    return number


def region_of_interest(logfile, verbose=False):
    """
    Did we reconstruct only ROI?
    If yes, give out its top, bottom, right and left coordinates.
    """
    top = False
    bottom = False
    left = False
    right = False
    with open(logfile, 'r') as f:
        for line in f:
            if 'Reconstruction from ROI' in line:
                if verbose:
                    print(line)
                if line.split('=')[1].strip() == 'OFF':
                    return False
                else:
                    pass
            elif 'ROI' in line and 'Top' in line:
                if verbose:
                    print(line)
                top = int(line.split('=')[1])
            elif 'ROI' in line and 'Bottom' in line:
                if verbose:
                    print(line)
                bottom = int(line.split('=')[1])
            elif 'ROI' in line and 'Left' in line:
                if verbose:
                    print(line)
                right = int(line.split('=')[1])
            elif 'ROI' in line and 'Right' in line:
                if verbose:
                    print(line)
                left = int(line.split('=')[1])
                return (top, bottom, right, left)
    return False
