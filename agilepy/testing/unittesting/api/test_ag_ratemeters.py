import pytest

from agilepy.api.AGRatemeters import AGRatemeters
from agilepy.utils.AstroUtils import AstroUtils

class TestAGRatemeters:

    @pytest.mark.skip("Temporary skip")
    @pytest.mark.testlogsdir("core/test_logs/test_ag_ratemeters")
    @pytest.mark.testconfig("api/conf/agilepyconf_ratemeters.yaml")
    def test_readratemeters(self, config, logger):

        # Test constructor
        ag = AGRatemeters(str(config))

        # Test nex indexfile argument
        print(f"Indexfile: {ag.getOption('indexfile')}")
        # Add Completion strategies for indexfile?

        # Test class methods
        assert ag.read_ratemeters()

