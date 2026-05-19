# MIT License – No Military Use
# Copyright (c) 2026 David Haberthür
# Permission granted for any use except military applications.

import re
import datetime
import pandas


# Convenience functions
def fulllog(logfile):
    """Print the full log file"""
    with open(logfile, 'r', encoding='utf-8') as f:
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
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Scanner=' in line:
                if verbose:
                    print(line)
                if 'Sky' in line:
                    # Sometimes it's SkyScan, sometimes Skyscan
                    # We thus have to regex it :)
                    machine = re.split('Sky.can', line)[1].strip()
                else:
                    machine = line.split('=')[1].strip()
            if 'Hardware' in line:  # Only for 1272
                if verbose:
                    print(line)
                hardwareversion = line.split('=')[1].strip()
            if machine is not None and hardwareversion:
                return 'SkyScan %s (Version %s)' % (machine, hardwareversion)
    if machine is None:
        return None
    if hardwareversion:
        return 'SkyScan %s (Version %s)' % (machine, hardwareversion)
    else:
        if 'Poseidon' in machine:
            return machine
        else:
            return 'SkyScan ' + machine


def controlsoftware(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Software' in line and 'Version' in line:
                if verbose:
                    print(line)
                # Sometimes it's 'Software Verion=Number'
                # Sometimes it's 'Software=Version Number' (with a space in Number)
                return line.split('=')[1].strip().strip('Version ').replace(". ", ".")
    return None


def source(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
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
    return None


# How did we set up the scan?
def voltage(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Voltage' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None


def current(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Source Current' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None

def power(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Source Target Power' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None


def spotsize(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Source spot size' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip()
    return None


def beamposition(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Beam position' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1])
    return None


def whichfilter(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Filter=' in line:
                if verbose:
                    print(line)
                fltr = line.split('=')[1].strip().replace('  ', ' ')
                if fltr == 'No Filter':
                    fltr = None
                return fltr
    return None


def camera(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Camera T' in line or 'Camera=' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip().strip(' camera')
    return None


def cameraposition(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Camera' in line and 'osition=' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip()
    return None


def distance_source_to_detector(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Camera to Source' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip()
    return None


def distance_source_to_sample(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Object to Source' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip()
    return None


def numproj(logfile, verbose=False):
    """How many projections are recorded?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            # Sometimes it's 'Number of Files'
            # Sometimes it's 'Number Of Files'
            if 'Number' in line and 'f Files' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1])
    return None


def projection_size(logfile):
    """How big did we set the camera?"""
    x = None
    y = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            # Sometimes it's 'Number of'
            # Sometimes it's 'Number Of'
            if 'Number' in line and 'f Rows' in line:
                y = int(line.split('=')[1])
            if 'Number' in line and 'f Columns' in line:
                x = int(line.split('=')[1])
            if x is not None and y is not None:
                return (x, y)
    return (x, y)


def rotationstep(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Rotation Step' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None


def pixelsize(logfile, verbose=False, rounded=False):
    """Get the pixel size from the scan log file"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Image Pixel' in line and 'Scaled' not in line:
                if verbose:
                    print(line)
                px_size = float(line.split('=')[1])
                if rounded:
                    return round(px_size, 2)
                return px_size
    return None


def stacks(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
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
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'orizontal' in line and 'ffset' in line and 'osition' in line:
                if verbose:
                    print(line)
                wide = int(line.split('=')[1])
                if wide == 1:
                    wide = False
                return wide
    return False


def threesixtyscan(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
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
    return None


def highaspectratio(logfile, verbose=False):
    with open(logfile, 'r') as f:
        for line in f:
            if 'High Aspect Ratio' in line:
                if verbose:
                    print(line)
                hart = line.split('=')[1]
                if 'YES' in hart:
                    hart = True
                elif 'NO' in hart:
                    hart = False
                return hart
    return False


def exposuretime(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Exposure' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1])
    return None


def averaging(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
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
    return None


def randommovement(logfile, verbose=False):
    with open(logfile, 'r', encoding='utf-8') as f:
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
    return None


def duration(logfile, prose=False, verbose=False):
    '''Returns scan duration in *seconds*'''
    with open(logfile, 'r', encoding='utf-8') as f:
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
                if verbose:
                    print(time_delta.total_seconds())
                # Return the scan time in seconds
                return time_delta.total_seconds()
    return None


def scandate(logfile, verbose=False):
    """When did we scan the Sample?"""
    with open(logfile, 'r', encoding='utf-8') as f:
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
    return None


# How did we reconstruct the scan?
def nreconversion(logfile, verbose=False):
    """Return reconstruction program and its version"""
    # Is only written to log files if reconstructed, thus set empty first
    program = None
    version = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Reconstruction Program' in line:
                if verbose:
                    print(line)
                program = line.split('=')[1].strip()
            elif 'Program Version' in line:
                if verbose:
                    print(line)
                version = line.split('sion:')[1].strip()
            if program is not None and version is not None:
                return (program, version)
    return (program, version)


def ringremoval(logfile, verbose=False):
    """Did we use ring removal?"""
    # Is only written to log files if reconstructed, thus set empty first
    ring = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Ring' in line:
                if verbose:
                    print(line)
                ring = int(line.split('=')[1].strip())
                if ring == 0:
                    ring = None
                return ring
    return ring


def beamhardening(logfile, verbose=False):
    """Did we set a beam hardening correction?"""
    # Is only written to log files if reconstructed, thus set empty first
    bh = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'ardeni' in line:
                if verbose:
                    print(line)
                bh = int(line.split('=')[1].strip())
                if bh == 0:
                    bh = None
                return bh
    return bh


def defectpixelmasking(logfile, verbose=False):
    """Check the 'defect pixel masking' setting"""
    dpm = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'defect pixel mask' in line:
                if verbose:
                    print(line)
                dpm = int(line.split('=')[1].strip())
                if dpm == 0:
                    dpm = None
                return dpm
    return dpm


def larger_than_fov(logfile, verbose=False):
    """Did we set the 'object larger than field of view' option"""
    ltfov = False
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Object Bigger' in line:
                if verbose:
                    print(line)
                ltfov = line.split('=')[1].strip()
                if ltfov == 'ON':
                    return True
                elif ltfov == 'OFF':
                    return False
    return False


def postalignment(logfile, verbose=False):
    """Read the postalignment value"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'post alignment' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1].strip())
    return None


def reconstruction_grayvalue(logfile, which='Maximum', verbose=False):
    """
    How did we map the brightness of the reconstructions?
    Usually we read only the 'Maximum' value, but which='Minimum' is also possible.
    """
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if which + ' for CS to Image' in line:  # Either search for 'Maximum for CS to Image' or 'Minimum for CS to Image'
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None


def reconstruction_size(logfile, verbose=False):
    """How large are the resulting reconstructions?"""
    x = None
    y = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Result' in line and 'Width' in line:
                if verbose:
                    print(line)
                x = int(line.split('=')[1])
            elif 'Result' in line and 'Height' in line:
                if verbose:
                    print(line)
                y = int(line.split('=')[1])
            if x is not None and y is not None:
                return (x, y)
    return (x, y)


def reconstruction_rotation(logfile, verbose=False):
    """How did we rotate the reconstructions? (NRecons "CS Static Rotation (deg)" value)"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'CS Static Rotation Total' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None


def slice_first(logfile, verbose=False):
    """What's the first slice?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'First Section' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1])
    return None


def slice_last(logfile, verbose=False):
    """What's the last slice?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Last Section' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1])
    return None


def slice_number(logfile, verbose=False):
    """How many slices can we expect on disk?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Sections Count' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1])
    return None


def region_of_interest(logfile, verbose=False):
    """
    Did we reconstruct a ROI?
    If yes, give out its top, bottom, left and right coordinates.
    """
    top = False
    bottom = False
    left = False
    right = False
    with open(logfile, 'r', encoding='utf-8') as f:
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
                left = int(line.split('=')[1])
            elif 'ROI' in line and 'Right' in line:
                if verbose:
                    print(line)
                right = int(line.split('=')[1])
            if (
                top is not False
                and bottom is not False
                and left is not False
                and right is not False
            ):
                return (top, bottom, left, right)
    return (top, bottom, left, right)
