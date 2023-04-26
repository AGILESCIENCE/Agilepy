export AGILE=$CONDA_PREFIX/agiletools
export PFILES=$PFILES:$AGILE/share
export ROOTSYS=$CONDA_PREFIX
export CFITSIO=$CONDA_PREFIX
export GSL=$CONDA_PREFIX
export OLD_PATH=$PATH
export PATH=$AGILE/bin:$AGILE/scripts:$AGILE/scripts/extendesources:$PATH
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$CONDA_PREFIX/lib64:$AGILE/lib:$LD_LIBRARY_PATH

chmod +x $AGILE/scripts/start_agilepy_notebooks.sh
chmod +x $AGILE/scripts/start_coverage.sh
chmod +x $AGILE/scripts/start_coverage_local.sh
