# DESCRIPTION

# I still have to understand how to work with pytest and turn this script into a class test.

from agilepy.api.AGRatemeters import AGRatemeters
from agilepy.utils.AstroUtils import AstroUtils

confFilePath="/Agilepy/agilepy/testing/unittesting/api/conf/agilepyconf_ratemeters.yaml"

# Test Static Method to write YAML configuration file
AGRatemeters.getConfiguration(confFilePath=confFilePath,
                              userName="userName",
                              outputDir="/Agilepy/agilepy/testing/unittesting/api/conf/",
                              verboselvl=0,
                              indexfile='PATH/TO/INDEX',
                              timetype='MJD',
                              contact="080618",
                              T0=59875.86219907,# 593642494.0,
                              tmin=-100.0,
                              tmax=+100.0,
                              tmin_bkg=-100.0,
                              tmax_bkg=-75.0,
                              tmin_src=0.0,
                              tmax_src=+30.0,
                              flag_detrending="ND",
                              sourceName="GRB221023A",
                              flag_N_RM="8RM"                             
                              )

# Test constructor
ag = AGRatemeters(confFilePath)

# Test the methods and attributes of the AGBaseAnalysis mother class
print(ag.config, ag.logger, ag.plottingUtils)
print(f"Output Directory: {ag.outdir}")
print(f"Analysis Directory:{ag.getAnalysisDir()}")
print(f"T0: {ag.getOption('T0')}")
ag.setOptions(T0=600000000.0,timetype='TT')
print(f"T0: {ag.getOption('T0')}")
ag.setOptions(T0=59875.86219907,timetype='MJD')
print(f"T0: {ag.getOption('T0')}")
ag.printOptions()

# Test nex indexfile argument
print(f"Indexfile: {ag.getOption('indexfile')}")
# Add Completion strategies for indexfile?

# Test class methods
ag.run_ratemeters_script()

ag.destroy()

# Clean up Directory
ag.deleteAnalysisDir()
