"""
Parse relevant metadata from Bruker X-ray MicroCT machine log files.

License details are provided in the repository LICENSE file.
"""

import re
import datetime
import pandas


# Convenience functions
def fulllog(logfile):
    """Print the full log file"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            print(line.strip())


def timeformat(tdelta, fmt):
    """Helper to format the scan duration in a human-readable way"""
    # From https://stackoverflow.com/a/8907269/323100
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


# How is the machine set up in general?
def scanner(logfile, verbose=False):
    """ What machine did we use? Also return hardware version for 1272 """
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
                break
    if hardwareversion:
        return f'SkyScan {machine} (Version {hardwareversion})'
    if 'Poseidon' in machine:
        return machine
    return 'SkyScan ' + machine


def controlsoftware(logfile, verbose=False):
    """What control software did we use?"""
    with open(logfile, 'r', encoding='utf-8') as f:
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
    return None


def source(logfile, verbose=False):
    """"What X-ray source is in the machine?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Source Type' in line:
                if verbose:
                    print(line)
                which_source = line.split('=')[1].strip()
                if 'HAMAMA' in which_source:
                    # Split the string at '_L' to separate HAMAMATSU_L118
                    # Then capitalize HAMAMATSU and join the strings back
                    # with ' L' to get the beginning of the reference back
                    which_source = ' L'.join(
                        [s.capitalize() for s in which_source.split('_L')]
                    )
                return which_source
    return None


# How did we set up the scan?
def voltage(logfile, verbose=False):
    """What voltage did we set the X-ray source to?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Voltage' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None


def current(logfile, verbose=False):
    """What current did we set the X-ray source to?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Source Current' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None

def power(logfile, verbose=False):
    """What's the resulting power of the X-ray source?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Source Target Power' in line:
                if verbose:
                    print(line)
                return float(line.split('=')[1])
    return None


def spotsize(logfile, verbose=False):
    """What's the set spot size of the X-ray source?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Source spot size' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip()
    return None


def beamposition(logfile, verbose=False):
    """What's the beam position?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Beam position' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1])
    return None


def whichfilter(logfile, verbose=False):
    """Which filter did we use?"""
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
    """What camera/detector is in the machine?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Camera T' in line or 'Camera=' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip().strip(' camera')
    return None

def cameraposition(logfile, verbose=False):
    """What's the camera position?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Camera' in line and 'osition=' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip()
    return None

def distance_source_to_detector(logfile, verbose=False):
    """What's the distance from the X-ray source to the detector?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Camera to Source' in line:
                if verbose:
                    print(line)
                return line.split('=')[1].strip()
    return None

def distance_source_to_sample(logfile, verbose=False):
    """What's the distance from the X-ray source to the sample?"""
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
    """How big are the projections? E.g. did we set any binning?"""
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
                if y is not None:
                    return (x, y)
    return None


def rotationstep(logfile, verbose=False):
    """What's the rotation step size?"""
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
                pxlsz = float(line.split('=')[1])
                if rounded:
                    return round(pxlsz, 2)
                return pxlsz
    return None


def stacks(logfile, verbose=False):
    """How many stacks did we scan?"""
    # If only one stack, then Bruker writes nothing to the log file
    numstacks = 0
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Sub-scan scan length' in line:
                if verbose:
                    print(line)
                numstacks = int(line.split('[')[1].split(']')[0])
    return numstacks + 1


def overlapscan(logfile, verbose=False):
    """Did we do an overlap scan?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'orizontal' in line and 'ffset' in line and 'osition' in line:
                if verbose:
                    print(line)
                wide = int(line.split('=')[1])
                if wide == 1:
                    wide = False
                return wide
    return None


def threesixtyscan(logfile, verbose=False):
    """Did we do a 360° scan?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if '360 Rotation' in line:
                if verbose:
                    print(line)
                threesixty = line.split('=')[1]
                if 'YES' in threesixty:
                    return True
                if 'NO' in threesixty:
                    return False
    return None


def highaspectratio(logfile, verbose=False):
    """Did we do a 'High Aspect Ratio' scan?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'High Aspect Ratio' in line:
                if verbose:
                    print(line)
                hart = line.split('=')[1]
                if 'YES' in hart:
                    return True
                if 'NO' in hart:
                    return False
    return None


def exposuretime(logfile, verbose=False):
    """What exposure time did we set?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Exposure' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1])
    return None


def averaging(logfile, verbose=False):
    """Did we do averaging? If yes, how many frames did we average?"""
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
    """Did we do a random movement scan?"""
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
    """Returns scan duration in *seconds*"""
    duration_log = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Scan duration' in line and 'Estimated' not in line:
                if verbose:
                    print(line)
                duration_log = line.split('=')[1].strip()
                break
    if duration_log is None:
        return None
    # Sometimes it's '00:24:26', sometimes '0h:52m:53s'
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
        # Return Timedelta object, which we can then split into components like
        # time_delta.components.hour, time_delta.components.minute, time_delta.components.seconds
        # Hat tip to https://stackoverflow.com/a/71407740/323100
        return time_delta
    if verbose:
        print(time_delta.total_seconds())
    # Return the scan time in seconds
    return time_delta.total_seconds()


def scandate(logfile, verbose=False):
    """When did we scan the Sample?"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Study Date and Time' in line:
                if verbose:
                    print(f'Found "date" line: {line.strip()}')
                datestring = line.split('=')[1].strip().replace('  ', ' ')
                if verbose:
                    print(f'The date string is: {datestring}')
                try:
                    # Try to read explicitly
                    date = pandas.to_datetime(datestring, format='%d %b %Y %Hh:%Mm:%Ss')
                except ValueError:
                    # If we fail, try to figure it out automatically
                    date = pandas.to_datetime(datestring)
                if verbose:
                    print(f'Parsed to: {date}')
                return date
    return None


# How did we reconstruct the scan?
def nreconversion(logfile, verbose=False):
    """Return reconstruction program and its version"""
    # Is only written to log files if reconstructed; returns (None, None) if absent
    program = version = None
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
                break
    return program, version


def ringremoval(logfile, verbose=False):
    """Did we use ring removal?"""
    # Is only written to log files if reconstructed; returns None if absent or zero
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Ring' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1].strip()) or None
    return None


def beamhardening(logfile, verbose=False):
    """Did we set a beam hardening correction?"""
    # Is only written to log files if reconstructed; returns None if absent or zero
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'ardeni' in line:
                if verbose:
                    print(line)
                return int(line.split('=')[1].strip()) or None
    return None


def defectpixelmasking(logfile, verbose=False):
    """Check the 'defect pixel masking' setting"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'defect pixel mask' in line:
                if verbose:
                    print(line)
                # Return found value OR None if the value is 0
                # Also return None if the line is not found
                return int(line.split('=')[1].strip()) or None
    return None


def larger_than_fov(logfile, verbose=False):
    """Did we set the 'object larger than field of view' option"""
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Object Bigger' in line:
                if verbose:
                    print(line)
                # Checks if the line says 'ON', and then returns True, otherwise False
                return line.split('=')[1].strip() == 'ON'
    return None


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
            # Either search for 'Maximum for CS to Image' or 'Minimum for CS to Image'
            if which + ' for CS to Image' in line:
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
    return (x, y)


def reconstruction_rotation(logfile, verbose=False):
    """How did we rotate the reconstructions? (NRecons "CS Static Rotation (deg)" value)"""
    rotation = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'CS Static Rotation Total' in line:
                if verbose:
                    print(line)
                rotation = float(line.split('=')[1])
    return rotation


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
    top = None
    bottom = None
    left = None
    right = None
    with open(logfile, 'r', encoding='utf-8') as f:
        for line in f:
            if 'Reconstruction from ROI' in line:
                if verbose:
                    print(line)
                if line.split('=')[1].strip() == 'OFF':
                    return False
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
            if None not in (top, bottom, left, right):
                return (top, bottom, left, right)
    return (top, bottom, left, right)
