import pytest
from pathlib import Path
from os.path import expandvars 
from agilepy.core.AgilepyLogger import AgilepyLogger

@pytest.fixture(scope="function")
def logger(request):

    testlogger = AgilepyLogger()

    script_path = Path( __file__ ).absolute().parent

    marker = request.node.get_closest_marker("testdir")

    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testdir' to fixture!")

    testdir = marker.args[0]
    testname = marker.args[1]

    testlogger.initialize(testdir, f"{testname}", 1)

    yield testlogger

    testlogger.reset() 
    


@pytest.fixture(scope="function")
def config(request):

    script_path = Path( __file__ ).absolute().parent

    marker = request.node.get_closest_marker("testdir")

    if marker is None:
        raise ValueError("marker is None! Something wrong passing 'testdir' to fixture!")

    testdir = marker.args[0]

    return script_path.joinpath(testdir, "conf", "agilepyconf.yaml")

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