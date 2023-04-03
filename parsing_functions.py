def fulllog(logfile):
    with open(logfile, 'r') as f:
        for line in f:
            print(line.strip())
    return()