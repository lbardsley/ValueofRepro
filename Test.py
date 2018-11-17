import segyio
import numpy as np
import matplotlib.pyplot as plt

from shutil import copyfile
filename = '/Users/Mikey/Documents/Workspace/segy/ESP2D_RAW_FULL_KPSTM_STACK_008A094.segy'

with segyio.open(filename, "r") as segyfile:

    # Memory map file for faster reading (especially if file is big...)
    segyfile.mmap()

    # Print binary header info
    print(segyfile.bin)
    print(segyfile.bin[segyio.BinField.Traces])

    # Read headerword inline for trace 10
    print(segyfile.header[10][segyio.TraceField.INLINE_3D])

    # Print inline and crossline axis
    print(segyfile.xlines)
    print(segyfile.ilines)
