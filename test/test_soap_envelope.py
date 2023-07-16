import base64
from io import BytesIO

from lxml import etree
from zeep.wsdl.utils import etree_to_string

from pymtom_xop.mtom_attachment import MtomAttachment
from pymtom_xop.soap_envelope import SoapEnvelope

CID = b'123456@pymtom-xop'
ENCODED_CID = base64.b64encode(CID)  # MTIzNDU2QHB5bXRvbS14b3A=
DECODED_CID = base64.b64decode(ENCODED_CID)
SOAP_ENV = b'<?xml version="1.0" encoding="utf-8"?><soap-env:Envelope xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"><soap-env:Body><ns0:uploadFile xmlns:ns0="http://service-test.com/"><arg0><file>MTIzNDU2QHB5bXRvbS14b3A=</file><fileName>test_document</fileName><fileExtension>pdf</fileExtension></arg0></ns0:uploadFile></soap-env:Body></soap-env:Envelope>'


def test_optimize_envelope():
    att = MtomAttachment(file=BytesIO(b'test123'), file_name='test_file.pdf')
    att.cid = f'<{CID.decode()}>'

    el_tree = etree.fromstring(SOAP_ENV)

    soap_env = SoapEnvelope(env_el=el_tree, files=[att])

    str_xml = etree_to_string(soap_env.xop_env)

    xop = b'<xop:Include xmlns:xop="http://www.w3.org/2004/08/xop/include" href="cid:123456@pymtom-xop"/>'

    assert xop in str_xml


def test_create_xop_include_element():
    prev_map = {'test': b'123', 'test2': b'456'}

    el = SoapEnvelope._SoapEnvelope__create_xop_include_element(
        cid=CID.decode(),
        prev_nsmap=prev_map
    )

    assert el.attrib['href'] == f'cid:{CID.decode()}'
    assert el.prefix == 'xop'
    assert el.text is None
    for key, val in prev_map.items():
        assert key in el.nsmap.keys()
        assert val.decode() in el.nsmap.values()
