from .api import LuasDirection, LuasLine, LuasClient
import os
import requests_mock


def test_default_balally(requests_mock):

    with open(_file_path('tests/balally.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=BAL', text=xml_file.read())
    client = LuasClient()
    next = client.next_tram('BAL')
    assert next is not None
    assert next.direction == LuasDirection.Inbound

def test_inbound_ranelagh(requests_mock):
    with open(_file_path('tests/ranelagh.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=RAN', text=xml_file.read(), status_code=200)

    client = LuasClient()
    next = client.next_tram('RAN', LuasDirection.Inbound)
    assert next is not None
    assert next.direction == LuasDirection.Inbound
    assert next.due == 'DUE'

def test_outbound_balally(requests_mock):
    with open(_file_path('tests/balally.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=BAL', text=xml_file.read(), status_code=200)

    client = LuasClient()
    next = client.next_tram('BAL', LuasDirection.Outbound)
    assert next is not None
    assert next.direction == LuasDirection.Outbound
    assert next.due ==  '3'

def test_raw_balally(requests_mock):
    with open(_file_path('tests/balally.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=BAL', text=xml_file.read(), status_code=200)

    client = LuasClient()
    stop_details = client.stop_details('BAL')
    assert stop_details is not None
    assert stop_details['status'] is not None
    assert stop_details['trams'] is not None


def test_all_trams(requests_mock):
    with open(_file_path('tests/balally.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=BAL', text=xml_file.read(), status_code=200)

    client = LuasClient()
    all_trams = client.all_trams('BAL')
    assert all_trams is not None
    assert all_trams[0] is not None
    assert all_trams[0].due ==  '5'
    assert all_trams[0].direction == LuasDirection.Inbound
    assert all_trams[0].destination =='Broombridge'


def test_default_line_status(requests_mock):
    with open(_file_path('tests/balally.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=STS', text=xml_file.read(), status_code=200)
    client = LuasClient()
    assert  "Green Line services operating normally" == client.line_status()


def test_red_line_status(requests_mock):
    with open(_file_path('tests/tallaght.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=TAL', text=xml_file.read(), status_code=200)
    client = LuasClient()
    assert "Red Line services operating normally" ==client.line_status(LuasLine.Red)


def test_tallaght_status(requests_mock):
    with open(_file_path('tests/tallaght.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=TAL', text=xml_file.read(), status_code=200)

    client = LuasClient()
    tallaght = client.all_trams('TAL')
    assert tallaght is not None
    assert len(tallaght) ==2

def test_tallaght_outbound(requests_mock):
    with open(_file_path('tests/tallaght.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=TAL', text=xml_file.read(), status_code=200)

    client = LuasClient()
    tallaght = client.next_tram('Tallaght', LuasDirection.Outbound)
    # There are never any outbound trams from Tallaght as it is the end of the line
    assert tallaght is None

def test_endpoint_failure(requests_mock):
    requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=STS', status_code=404)

    client = LuasClient()
    status = client.line_status()
    assert status == 'n/a'

def test_invalid_response(requests_mock):
    with open(_file_path('tests/failed.xml')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=STS', text=xml_file.read(), status_code=200)

    client = LuasClient()
    status = client.line_status()
    assert 'n/a'== status

def test_invalid_response_empty(requests_mock):
    with open(_file_path('tests/empty_response')) as xml_file:
        requests_mock.get('/xml/get.ashx?action=forecast&encrypt=false&stop=STS', text=xml_file.read(), status_code=200)

    client = LuasClient()
    status = client.line_status()
    assert 'n/a' == status

def test_invalid_stop_name():
    client = LuasClient()
    details = client.next_tram('My pretend stop')
    assert details is None
    stop_details = client.stop_details('My pretend stop')
    assert 'n/a' == stop_details['status']


def test_load_stops_file():
    from luas.models import LuasStops
    stops = LuasStops()

    assert stops.stops is not None
    assert stops.stop_exists('BAL')
    assert stops.stop_exists('St. Stephen\'s Green')
    assert stops.stop_exists('O\'Connell - GPO')
    assert not stops.stop_exists('123')
    balally = stops.stop('Balally')
    assert balally['isParkRide'] =='1'


def _file_path(file_name):
    thispath = os.path.dirname(__file__)
    return "{}/{}".format(thispath, file_name)