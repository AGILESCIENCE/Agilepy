import pytest
from agilepy.utils.AstroUtils import AstroUtils

@pytest.mark.parametrize("input_date,expected", [
    (2459608.09921296, {"agile_seconds":570464572,"mjd":59607.59921296,"unix":1643379772,"fits":"2022-01-28T14:22:52.000","iso":"2022-01-28 14:22:52.000"}),
    (2458208.99921296, {"agile_seconds":449582332,"mjd":58208.49921296,"unix":1522497532,"fits":"2018-03-31T11:58:52.000","iso":"2018-03-31 11:58:52.000"})])

def test_jd_conversion(input_date, expected):

    assert AstroUtils.time_jd_to_agile_seconds(input_date) == expected["agile_seconds"]
    assert AstroUtils.time_jd_to_mjd(input_date) == pytest.approx(expected["mjd"], 0.00001)
    assert AstroUtils.time_jd_to_unix(input_date) == expected["unix"]
    assert AstroUtils.time_jd_to_fits(input_date) == expected["fits"]
    assert AstroUtils.time_jd_to_iso(input_date) == expected["iso"]


@pytest.mark.parametrize("input_date,expected", [
    (59607.59921296, {"agile_seconds":570464572,"jd":2459608.09921296,"unix":1643379772,"fits":"2022-01-28T14:22:52.000","iso":"2022-01-28 14:22:52.000"}),
    (58208.49921296, {"agile_seconds":449582332,"jd":2458208.99921296,"unix":1522497532,"fits":"2018-03-31T11:58:52.000","iso":"2018-03-31 11:58:52.000"})])

def test_mjd_conversion(input_date, expected):

    assert AstroUtils.time_mjd_to_agile_seconds(input_date) == expected["agile_seconds"]
    assert AstroUtils.time_mjd_to_jd(input_date) == pytest.approx(expected["jd"], 0.00001)
    assert AstroUtils.time_mjd_to_unix(input_date) == expected["unix"]
    assert AstroUtils.time_mjd_to_fits(input_date) == expected["fits"]
    assert AstroUtils.time_mjd_to_iso(input_date) == expected["iso"]

@pytest.mark.parametrize("input_date,expected", [
    (1643379772, {"agile_seconds":570464572,"jd":2459608.09921296,"mjd":59607.59921296,"fits":"2022-01-28T14:22:52.000","iso":"2022-01-28 14:22:52.000"}),
    (1522497532, {"agile_seconds":449582332,"jd":2458208.99921296,"mjd":58208.49921296,"fits":"2018-03-31T11:58:52.000","iso":"2018-03-31 11:58:52.000"})])

def test_unix_conversion_1(input_date, expected):

    assert AstroUtils.time_unix_to_agile_seconds(input_date) == expected["agile_seconds"]
    assert AstroUtils.time_unix_to_jd(input_date) == pytest.approx(expected["jd"], 0.00001)
    assert AstroUtils.time_unix_to_mjd(input_date) == pytest.approx(expected["mjd"], 0.00001)
    assert AstroUtils.time_unix_to_fits(input_date) == expected["fits"]
    assert AstroUtils.time_unix_to_iso(input_date) == expected["iso"]

@pytest.mark.parametrize("input_date,expected", [
    ("2022-01-28T14:22:52.000", {"agile_seconds":570464572,"jd":2459608.09921296,"mjd":59607.59921296,"unix":1643379772,"iso":"2022-01-28 14:22:52.000"}),
    ("2018-03-31T11:58:52.000", {"agile_seconds":449582332,"jd":2458208.99921296,"mjd":58208.49921296,"unix":1522497532,"iso":"2018-03-31 11:58:52.000"})])

def test_unix_conversion_2(input_date, expected):

    assert AstroUtils.time_fits_to_agile_seconds(input_date) == expected["agile_seconds"]
    assert AstroUtils.time_fits_to_jd(input_date) == pytest.approx(expected["jd"], 0.00001)
    assert AstroUtils.time_fits_to_mjd(input_date) == pytest.approx(expected["mjd"], 0.00001)
    assert AstroUtils.time_fits_to_unix(input_date) == expected["unix"]
    assert AstroUtils.time_fits_to_iso(input_date) == expected["iso"]

@pytest.mark.parametrize("input_date,expected", [
    ("2022-01-28 14:22:52.000", {"agile_seconds":570464572,"jd":2459608.09921296,"mjd":59607.59921296,"unix":1643379772,"fits":"2022-01-28T14:22:52.000"}),
    ("2018-03-31 11:58:52.000", {"agile_seconds":449582332,"jd":2458208.99921296,"mjd":58208.49921296,"unix":1522497532,"fits":"2018-03-31T11:58:52.000"})])

def test_unix_conversion_3(input_date, expected):

    assert AstroUtils.time_iso_to_agile_seconds(input_date) == expected["agile_seconds"]
    assert AstroUtils.time_iso_to_jd(input_date) == pytest.approx(expected["jd"], 0.00001)
    assert AstroUtils.time_iso_to_mjd(input_date) == pytest.approx(expected["mjd"], 0.00001)
    assert AstroUtils.time_iso_to_unix(input_date) == expected["unix"]
    assert AstroUtils.time_iso_to_fits(input_date) == expected["fits"]

@pytest.mark.parametrize("input_date,expected", [
    (570464572, {"iso":"2022-01-28 14:22:52.000","jd":2459608.09921296,"mjd":59607.59921296,"unix":1643379772,"fits":"2022-01-28T14:22:52.000"}),
    (449582332, {"iso":"2018-03-31 11:58:52.000","jd":2458208.99921296,"mjd":58208.49921296,"unix":1522497532,"fits":"2018-03-31T11:58:52.000"})])

def test_unix_conversion_4(input_date, expected):

    assert AstroUtils.time_agile_seconds_to_iso(input_date) == expected["iso"]
    assert AstroUtils.time_agile_seconds_to_jd(input_date) == pytest.approx(expected["jd"], 0.00001)
    assert AstroUtils.time_agile_seconds_to_mjd(input_date) == pytest.approx(expected["mjd"], 0.00001)
    assert AstroUtils.time_agile_seconds_to_unix(input_date) == expected["unix"]
    assert AstroUtils.time_agile_seconds_to_fits(input_date) == expected["fits"]