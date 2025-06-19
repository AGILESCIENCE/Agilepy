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
    def getConfiguration(confFilePath, outputDir,
                         userName="my_name", sourceName="bb-source", verboselvl=0,
                         ap_path="null", mle_path="null", ph_path="null", rate_path="null",
                         detections_csv_path="null", rate="null", ratefactor="null", event_id="null", tstart="null", tstop="null",
                         fitness="events", p0="null", gamma=0.35, useerror="true"
                         ):
        """Utility method to create a configuration file.

        Args:
            confFilePath (str): the path and filename of the configuration file that is going to be created.
            outputDir (str): the path to the output directory. The output directory will be created using the following format: 'userName_sourceName_todaydate'
            userName (str): the username of who is running the software.
            sourceName (str): the name of the source.
            verboselvl (int): the verbosity level of the console output. Message types: level 0 => critical, warning, level 1 => critical, warning, info, level 2 => critical, warning, info, debug
            
            ap_path, mle_path, ph_path, rate_path (str): The path to the data file, in AP, MLE (binned light curves), TTE (events) or rate format. 
            rate (bool): For ap_path. Enable the evaluation of the rate multiplied for a ratefactor and converted into integer. If ratefactor == 0 use the mean of the exposure
            ratefactor (float). Scale a rate to int. Usualy set it as the a mean effective area * dt
            detections_csv_path (str): The path to the CSV file containing detection data time ranges.
            event_id (str): The ID of the event to select (default is None) if detections_csv_path is not None.
            tstart, tstop (float): Time start and stop in MJD. This is used if event_id is None.

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
  ap_path: {ap_path}
  mle_path: {mle_path}
  ph_path: {ph_path}
  rate_path: {rate_path}
  rate: {rate}
  ratefactor: {ratefactor}
  detections_csv_path: {detections_csv_path}
  event_id: {event_id}
  tstart: {tstart}
  tstop: {tstop}

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

        
        
    def selectEvents(self, 
                     ap_path=None, mle_path=None, ph_path=None,
                     rate_path=None, rate=None, ratefactor=None,
                     detections_csv_path= None, event_id=None,
                     tstart=None, tstop=None, 
                     ):
        """
        Select an event by specifying its ID and data paths.
        If None, they are selected from the configuration.

        Parameters:
        -----------
        ap_path, mle_path : str
            The path to the binned light curve data file, in AP or MLE format. 
        ph_path : str
            The path to the TTE data file.
        rate_path : str
            Path to the rate file.
        rate: bool
            For ap_path. Enable the evaluation of the rate multiplied for a ratefactor and converted into integer. If ratefactor == 0 use the mean of the exposure
        ratefactor: float
            Scale a rate to int. Usualy set it as the a mean effective area * dt
            For ap_path: A scale factor of the cts/exp values to obtain an integer after conversion. Typical value 1e7
            For rate_path: ratefactor=0 scale to int with a mean rate scaling, ratefactor=-1 show row data, scalefactor > 1 give your own scale factor
        detections_csv_path : str or None
            The path to the CSV file containing detection data time ranges.
            Example of csv:
            ```
            flare_id,mjd_start,mjd_stop
            E01,54343.0,54344.0
            E02,54732.0,54733.0
            E03,54746.0,54747.0
            E04,54915.0,54916.0
            ```
        event_id : str
            The ID of the event to select (default is None) if detections_csv_path is not None.
        tstart 
            Time start in MJD. This is used if event_id is None
        tstop 
            Time stop in MJD. This is used if event_id is Non
        """
        # If arguments are not provided explicitly, set them from the configuration
        ap_path    = ap_path    if ap_path    is not None else self.config.getOptionValue("ap_path")
        mle_path   = mle_path   if mle_path   is not None else self.config.getOptionValue("mle_path")
        ph_path    = ph_path    if ph_path    is not None else self.config.getOptionValue("ph_path")
        rate_path  = rate_path  if rate_path  is not None else self.config.getOptionValue("rate_path")
        rate       = rate       if rate       is not None else self.config.getOptionValue("rate")
        ratefactor = ratefactor if ratefactor is not None else self.config.getOptionValue("ratefactor")
        event_id   = event_id   if event_id   is not None else self.config.getOptionValue("event_id")
        tstart     = tstart     if tstart     is not None else self.config.getOptionValue("tstart")
        tstop      = tstop      if tstop      is not None else self.config.getOptionValue("tstop")
        detections_csv_path = detections_csv_path if detections_csv_path is not None else self.config.getOptionValue("detections_csv_path")
        # Call the function from the external package
        self.logger.info("Select Events...")
        self.agile_bblocks.select_event(ap_path=ap_path, mle_path=mle_path, ph_path=ph_path, rate_path=rate_path,
                                        rate=rate, ratefactor=ratefactor,
                                        detections_csv_path=detections_csv_path, event_id=event_id, tstart=tstart, tstop=tstop)
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
    def sigma(self):
        try:
            return self.agile_bblocks.sigma
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
        self.agile_bblocks.bayesian_blocks(fitness, p0, gamma, useerror)
        self.logger.info("... done!")
        return None
    
    def plotBayesianBlocks(self, plotYErr=True, saveImage=False, plotBayesianBlocks=True, plotRate=False, plotDataCells=False):
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
        """
        plotTDelta = False if self.datamode==1 else True
        
        plotSumBlocks = plotRate and not plotTDelta
                
        data = {"in":self.getDataIn(),"out":self.getDataOut()}
        
        if plotBayesianBlocks and data['out']=={}:
            self.logger.warning("Bayesian Blocks not computed yet. Plotting only data...")
            plotBayesianBlocks = False
        if plotRate and data['out']=={}:
            self.logger.warning("Bayesian Blocks not computed yet. Plotting only data...")
            plotRate = False
        
        plot = self.plottingUtils.plotBayesianBlocks(data=data,
                                                     plotTDelta=plotTDelta, plotYErr=plotYErr,
                                                     edgePoints=plotBayesianBlocks, meanBlocks=plotBayesianBlocks,
                                                     dataCells=plotDataCells, plotRate=plotRate, sumBlocks=plotSumBlocks,
                                                     saveImage=saveImage,
                                                     )
        
        return plot

