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