import logging
from pathlib import Path
import sys

from agilepy.utils.Utils import Utils
from agilepy.core.AGBaseAnalysis import AGBaseAnalysis

########################################################################################################
# Add BBrta module path to the system path
BBRTA_PATH = (Path(__file__).parent / "../external_packages/BBrta/python_code").resolve()
if not BBRTA_PATH.exists():
    logging.error(f"BBrta path does not exist: {BBRTA_PATH}")
    AGILE_BBlocks = None
else:
    sys.path.insert(0, str(BBRTA_PATH))

    try:
        from agile_bblocks import AGILE_BBlocks
    except ImportError as e:
        logging.error(f"Failed to import AGILE_BBlocks from BBrta: {e}")
        AGILE_BBlocks = None
    finally:
        # Clean up sys.path to avoid side effects
        sys.path.pop(0)
########################################################################################################



class AGBayesianBlocks(AGBaseAnalysis):
    """
    Wrapper for the Bayesian Blocks Real-Time Analysis (RTA) module.
    Provides an interface to process data using Bayesian Blocks segmentation.
    """

    def __init__(self, configurationFilePath):
        """
        Initialize the AGBayesianBlocks class.

        Args:
            configurationFilePath (str): a relative or absolute path to the yaml configuration file.

        Raises:
            AGILENotFoundError: if the AGILE environment variable is not set.
            PFILESNotFoundError: if the PFILES environment variable is not set.

        Example:
            >>> from agilepy.api import AGBayesianBlocks
            >>> agilebb = AGBayesianBlocks('agconfig.yaml')
        """
        # Load the AGBaseAnalysis object and attributes
        super().__init__(configurationFilePath)
        self.config.loadConfigurationsForClass("AGBayesianBlocks")
        self.logger = self.agilepyLogger.getLogger(__name__, "AGBayesianBlocks")

        # Load the AGILE BB RTA class as an object
        self.agile_bblocks = AGILE_BBlocks()
        
        # End initialization
        self.logger.info("AGBayesianBlocks initialized")
        
        
    @staticmethod
    def getConfiguration(confFilePath, outputDir, filePath,
                         userName="my_name", sourceName="bb-source", verboselvl=0,
                         fileMode="AGILE_AP", rateCorrection=0, tstart="null", tstop="null",
                         fitness="events", p0="null", gamma=0.35, useerror="true"
                         ):
        """Utility method to create a configuration file.

        Args:
            confFilePath (str): the path and filename of the configuration file that is going to be created.
            outputDir (str): the path to the output directory. The output directory will be created using the following format: 'userName_sourceName_todaydate'
            userName (str): the username of who is running the software.
            sourceName (str): the name of the source.
            verboselvl (int): the verbosity level of the console output. Message types: level 0 => critical, warning, level 1 => critical, warning, info, level 2 => critical, warning, info, debug
            
            filePath (str): The path to the data file. 
            fileMode (str or int) : it defines the format of the data. Allowed data formats:
                - UNBINNED data: AGILE_PH (1)
                - BINNED data: AGILE_AP (2), AGILE_MLE (3), CUSTOM_LC (4)
            tstart, tstop (float) : Time start, stop in MJD to select events. If None, no selection is applied.
            rateCorrection (None or 0 or float) : Multiplication factor to convert rates (cts/exp) into integers.
                - Set to None to not use.
                - Set to 0 to use the mean exposure (effective area * dt).
                - Set to a float value to use it directly.
            
            fitness (str): The fitness function to use.
            p0 (float): Prior on the number of blocks (optional). Calculated with eq. 21 in Scargle (2013)
            gamma (float): Regularization parameter (optional).
            useerror : Flag for using error for computing blocks or not.

        Returns:
            None
        """

        configuration = f"""
output:
  outdir: {outputDir}
  filenameprefix: analysis_product
  logfilenameprefix: analysis_log
  sourcename: {sourceName}
  username: {userName}
  verboselvl: {verboselvl}

selection:
  file_path: {filePath}
  file_mode: {fileMode}
  tstart: {tstart}
  tstop: {tstop}
  ratecorrection: {rateCorrection}

bayesianblocks:
  fitness: {fitness}
  p0: {p0}
  gamma: {gamma}
  useerror: {useerror}


        """
        full_file_path = Utils._expandEnvVar(confFilePath)
        parent_directory = Path(full_file_path).absolute().parent
        parent_directory.mkdir(exist_ok=True, parents=True)

        with open(full_file_path,"w") as cf:

            cf.write(configuration)
            
        return None

        
        
    def selectEvents(self, file_path=None, file_mode=None, tstart=None, tstop=None, ratecorrection=None):
        """
        Select an event by specifying its ID and data paths.
        If None, they are selected from the configuration.

        Parameters:
        -----------
        file_path : str
            The path to the data file. 
        file_mode : str, int or FileMode
            FileMode to set read function and DataMode. Allowed data formats:
            - UNBINNED data: AGILE_PH (1)
            - BINNED data: AGILE_AP (2), AGILE_MLE (3), CUSTOM_LC (4)
        tstart, tstop : float 
            Time start, stop in MJD to select events. If None, no selection is applied.
        ratecorrection: None or 0 or float
            Multiplication factor to convert rates (cts/exp) into integers.
            - Set to None to not use.
            - Set to 0 to use the mean exposure (effective area * dt), typical value 1e7.
            - Set to a float value to use it directly.
        """
        # If arguments are not provided explicitly, set them from the configuration
        file_path    = file_path    if file_path    is not None else self.config.getOptionValue("file_path")
        file_mode    = file_mode    if file_mode    is not None else self.config.getOptionValue("file_mode")
        ratecorrection = ratecorrection if ratecorrection is not None else self.config.getOptionValue("ratecorrection")
        tstart     = tstart     if tstart     is not None else self.config.getOptionValue("tstart")
        tstop      = tstop      if tstop      is not None else self.config.getOptionValue("tstop")
        # Call the function from the external package
        self.logger.info("Select Events...")
        self.agile_bblocks.select_event(file_path=file_path, file_mode=file_mode,
                                        tstart=tstart, tstop=tstop,
                                        ratecorrection=ratecorrection
                                        )
        self.logger.info("... done!")
        return None
        
    def headDetections(self, n:int = 5):
        """Return the first `n` rows of the detections DataFrame."""
        return self.agile_bblocks.head_detections(n)
    
    def headEvents(self, n:int = 5):
        """Return the first `n` rows of the event DataFrame."""
        return self.agile_bblocks.head_event(n)
    
    def getDataOut(self):
        """Return Output Data."""
        return self.agile_bblocks.get_data_out()
    
    def getDataIn(self):
        """Return Input Data."""
        return self.agile_bblocks.get_data_in()
    
    @property
    def datamode(self):
        try:
            return self.agile_bblocks.datamode
        except AttributeError:
            return None
        
    @property
    def filemode(self):
        try:
            return self.agile_bblocks.filemode
        except AttributeError:
            return None
        
    @property
    def df_event(self):
        try:
            return self.agile_bblocks.df_event
        except AttributeError:
            return None
    
    def bayesianBlocks(self, fitness=None, p0=None, gamma=None, useerror=None):
        """
        Compute the Bayesian blocks using the given parameters and plot the result.

        Parameters:
        -----------
        fitness : str
            The fitness function to use ('events' by default).
        p0 : float
            Prior on the number of blocks (optional). Calculated with eq. 21 in Scargle (2013)
        gamma : float
            Regularization parameter (optional).
        useerror : Bool
            Flag for using error for computing blocks or not.
        """
        # If arguments are not provided explicitly, set them from the configuration
        fitness  = fitness  if fitness  is not None else self.config.getOptionValue("fitness")
        p0       = p0       if p0       is not None else self.config.getOptionValue("p0")
        gamma    = gamma    if gamma    is not None else self.config.getOptionValue("gamma")
        useerror = useerror if useerror is not None else self.config.getOptionValue("useerror")
        # Call the function from the external package
        self.logger.info("Compute Bayesian Blocks...")
        self.agile_bblocks.bayesian_blocks(fitness, p0, gamma, useerror, plotBlocks=False)
        self.logger.info("... done!")
        return None
    
    def plotBayesianBlocks(self, plotYErr=True, saveImage=False, plotBayesianBlocks=True, plotRate=False, plotDataCells=False, plotSumBlocks=False):
        """
        Plot the data and the results of the Bayesian Blocks analysis.
        
        Parameters:
        -----------
        plotYErr : bool
            Plot errors on Y data or not.
        plotBayesianBlocks : bool
            Plot The Bayesian blocks over the data if they were computed.
        plotRate : bool
            Add a second panel with the plot of the rate.
        plotDataCells : bool
            If True, plot the Data Cells vertical lines.
        saveImage : bool
            Write a copy of the image if True.
        plotSumBlocks :
            Plot the Sum of the events in the Block if True.
        """
        plotTDelta = False if self.datamode==1 else True
                
        data = {"in":self.getDataIn(),"out":self.getDataOut()}
        
        if plotBayesianBlocks and data['out']=={}:
            self.logger.warning("Bayesian Blocks not computed yet. Plotting only data...")
            plotBayesianBlocks = False
        if plotRate and data['out']=={}:
            self.logger.warning("Bayesian Blocks not computed yet. Plotting only data...")
            plotRate = False
        
        if self.datamode==2:
            plot = self.plottingUtils.plotBayesianBlocks(data=data,
                                                         plotTDelta=plotTDelta, plotYErr=plotYErr,
                                                         edgePoints=plotBayesianBlocks, meanBlocks=plotBayesianBlocks,
                                                         dataCells=plotDataCells, plotRate=plotRate, sumBlocks=plotSumBlocks,
                                                         saveImage=saveImage,
                                                         )
        elif self.datamode==1:
            plot = self.plottingUtils.plotBayesianBlocksUnbinned(data=data,
                                                         plotTDelta=plotTDelta, plotYErr=plotYErr,
                                                         edgePoints=plotBayesianBlocks, meanBlocks=plotBayesianBlocks,
                                                         dataCells=plotDataCells, plotRate=plotRate, sumBlocks=plotSumBlocks,
                                                         saveImage=saveImage,
                                                         )
        else:
            raise ValueError(f"Datamode {self.datamode} not recognised, run selectEvents first.")
        
        return plot

