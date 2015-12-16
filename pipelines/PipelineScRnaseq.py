import sys, glob, gzip, os, itertools, re, math, types, collections, time
import optparse, shutil
import sqlite3
import pandas as pd
import rpy2.robjects as R

import pandas.rpy.common as pdcom
import pandas as pd
import numpy as np
import scipy as scipy
from scipy import stats

import CGAT.Experiment as E
import CGAT.IOTools as IOTools
import CGAT.Database as DB
#import CGATPipelines.PipelineUtilities as PU

import CGATPipelines.Pipeline as P

PARAMS = P.getParameters(
    ["%s/pipeline.ini" % os.path.splitext(__file__)[0],
     "../pipeline.ini",
     "pipeline.ini"])

###############################################################################
######################## Copy number functions ################################
###############################################################################

def estimateCopyNumber(infiles, outfile, params):
    '''Estimate copy number based on ERCC spike in concentrations.
       Expects the location of the directory containing the
       R code as a single parameter.'''

    infile, cuffnorm_load, ercc_load = infiles
    code_dir = params[0]

    cuffnorm_table = P.toTable(cuffnorm_load)
    ercc_table = P.toTable(ercc_load)

    track = outfile.split("/")[-1][:-len(".spike.norm")]
    plotname = outfile+".png"

    #col_name = track.replace("-","_") + "_0"
    col_name = re.sub(r"[-.]","_",track) + "_0"

    ### connect to the database.
    con = sqlite3.connect(PARAMS["database_name"])

    ### retrieve the spike in data
    statement = '''select e.gene_id, %(col_name)s as FPKM, copies_per_cell
                   from %(ercc_table)s e
                   inner join %(cuffnorm_table)s c
                   on e.gene_id=c.tracking_id
                ''' % locals()

    #spikedf = PU.fetch_DataFrame(statement, PARAMS["database"])
    spikedf = pd.read_sql(statement, con)
    rspikedf = pdcom.convert_to_r_dataframe(spikedf)

    ### retrieve the data to normalise
    statement = ''' select tracking_id as gene_id, %(col_name)s as FPKM
                    from %(cuffnorm_table)s
                ''' % locals()



    fpkms = pd.read_sql(statement, con)
    rfpkms = pdcom.convert_to_r_dataframe(fpkms)

    script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

    r = R.r

    rscript = os.path.join(os.path.join(code_dir,
                                        PARAMS["rsource"]))


    r.source(rscript)

    plotname, outfile = [os.path.abspath(x) for x in [plotname, outfile]]

    r.normalise_to_spikes(rspikedf, rfpkms, plotname, outfile, track)
