This repository contains a Jupyter notebook and some supporting files I reuse often.
I work with tomographic data acquired with three different [Bruker SkyScan](https://www.bruker.com/en/products-and-solutions/preclinical-imaging/micro-ct.html) (1172, 1272 and 2214).
Usually, I have to produce an overview of what was scanned, either for a publication, a report for a proprietary customer, or as an overview to keep track in for an internal project.
All the necessary data to do this is recorded in the log files of the scans, produced by the Bruker machines.
The code here parsed this data and produces a nice output, be it either in prose or as a tabular overview.

*Very* often, the code is adapted from what is shown here, but this is a common baseline I always use.
The repository contains a `logfiles` subfolder with some examples of log files and is set up in a way that it can be run in Binder, just click the link button at the top.
