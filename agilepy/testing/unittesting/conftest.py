import os
import pytest
from pathlib import Path
from shutil import rmtree
from os.path import expandvars
from agilepy.config.AgilepyConfig import AgilepyConfig 
from agilepy.core.AgilepyLogger import AgilepyLogger


@pytest.fixture(scope="function", autouse=True)
def set_env_var(monkeypatch):
    # Get the directory containing this conftest.py file
    conftest_dir = Path(__file__).parent.resolve()
    
    # Set the environment variable
    monkeypatch.setenv("AGILEPY_UNITTESTING_DIR", str(conftest_dir))

@pytest.fixture(scope="function")
def logger(request):

    marker = request.node.get_closest_marker("testlogsdir")

    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testlogsdir' to fixture!")

    testlogsdir = marker.args[0]
    try:
        marker = request.node.get_closest_marker("loglevel")
        loglevel = marker.args[0]
    except Exception:
        loglevel = 2
        pass

    rootLogsPath = Path( __file__ ).absolute().parent.joinpath(testlogsdir)
    if rootLogsPath.exists() and rootLogsPath.is_dir():
        rmtree(rootLogsPath)
        rootLogsPath.mkdir(exist_ok=True, parents=True)
    singletonLogger = AgilepyLogger()
    singletonLogger.setLogger(rootLogsPath, loglevel)
    os.environ["TEST_LOGS_DIR"] = str(rootLogsPath)
    yield singletonLogger.getLogger(request.node.name)
    
@pytest.fixture(scope="function")
def environ_test_logs_dir(request):
    """Sets the TEST_LOGS_DIR environment variable for the current test."""
    
    marker = request.node.get_closest_marker("testlogsdir")
    if marker is None:
        raise ValueError("Missing 'testlogsdir' marker!")
    testlogsdir = marker.args[0]
    test_name = request.node.name

    log_root = Path( __file__ ).absolute().parent.joinpath(testlogsdir)

    os.environ["TEST_LOGS_DIR"] = str(log_root)

    yield log_root


@pytest.fixture(scope="function")
def config(request):

    script_path = Path( __file__ ).absolute().parent

    marker = request.node.get_closest_marker("testconfig")

    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testconfig' to fixture!")

    testconfig = marker.args[0]

    return script_path.joinpath(testconfig)



@pytest.fixture(scope="function")
def testdata(request):

    script_path = Path( __file__ ).absolute().parent

    marker = request.node.get_closest_marker("testdatafile")

    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testdatafile' to fixture!")

    testdatafile = marker.args[0]

    return str(script_path.joinpath(testdatafile))


@pytest.fixture(scope="function")
def testdata2(request):

    script_path = Path( __file__ ).absolute().parent

    marker = request.node.get_closest_marker("testdatafile2")

    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testdatafile2' to fixture!")

    testdatafile2 = marker.args[0]

    return str(script_path.joinpath(testdatafile2))


@pytest.fixture(scope="function")
def testdatafiles(request):

    script_path = Path( __file__ ).absolute().parent

    marker = request.node.get_closest_marker("testdatafiles")

    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testdatafiles' to fixture!")

    testdatafiles = marker.args[0]

    return [str(script_path.joinpath(filename)) for filename in testdatafiles]


@pytest.fixture(scope="function")
def configObject(request):

    script_path = Path( __file__ ).absolute().parent

    # Handle TestConfig Marker
    marker = request.node.get_closest_marker("testconfig")
    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testconfig' to fixture!")
    testconfig = marker.args[0]
    
    # Handle testlogsdir marker
    logs_marker = request.node.get_closest_marker("testlogsdir")
    if logs_marker is not None:
        testlogsdir = logs_marker.args[0]
        log_root = script_path.joinpath(testlogsdir)
        os.environ["TEST_LOGS_DIR"] = str(log_root)

    config = AgilepyConfig()
    config.loadBaseConfigurations(script_path.joinpath(testconfig))
    config.loadConfigurationsForClass("AGAnalysis")
    return config

@pytest.fixture(scope="function")
def testdataset():

    evt = expandvars("$AGILE/agilepy-test-data/test_dataset_6.0/EVT")
    log = expandvars("$AGILE/agilepy-test-data/test_dataset_6.0/LOG")

    return {"evt": evt, "log": log}

@pytest.fixture(scope="function")
def gettmpdir(request):

    script_path = Path( __file__ ).absolute().parent

    marker = request.node.get_closest_marker("testdir")

    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testdir' to fixture!")

    testdir = marker.args[0]

    tmpDir = Path( __file__ ).absolute().parent.joinpath(testdir, "tmp")
    tmpDir.mkdir(exist_ok=True, parents=True)

    return tmpDir


@pytest.fixture(scope="function")
def datacoveragepath(request):
    
    marker = request.node.get_closest_marker("testdir")

    testdir = marker.args[0]

    datacoveragepath = Path( __file__ ).absolute().parent.joinpath(testdir, "test_data", "AGILE_test_datacoverage")

    return datacoveragepath


###### This part is for running tests that require a connection with SSDC datacenter

def pytest_addoption(parser):
    parser.addoption(
        "--runrest", action="store_true", default=False, help="run tests that use a connection with SSDC datacenter"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "ssdc: mark test that requires a SSDC connection")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runrest"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_rest = pytest.mark.skip(reason="need --runrest option to run")
    for item in items:
        if "ssdc" in item.keywords:
            item.add_marker(skip_rest)