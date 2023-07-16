from io import BytesIO

import pytest
import responses
from zeep import Client
from zeep.settings import Settings

from pymtom_xop import MtomAttachment, MtomTransport


@responses.activate
def test_mtom_transport():
    responses.add(
        responses.POST,
        "https://service-test.com/UploadFileWs",
        body='mock response',
        status=200
    )

    mtom_transport = MtomTransport()

    file = MtomAttachment(file=BytesIO(b'test 123'), file_name='test.pdf')

    mtom_transport.add_files(files=[file])

    conf = Settings(raw_response=True)  # type: ignore

    client = Client(
        wsdl="documents/UploadWSDL.wsdl", transport=mtom_transport, settings=conf
    )

    factory = client.type_factory("ns0")

    body = factory.uploadFileWs(
        file=file.get_cid(),
        fileName="test",
        fileExtension="pdf"
    )

    response = client.service.uploadFile(body)
    assert response is not None


def test_generate_http_headers():
    cid = '123456@pymtom-xop'
    boundary = 'root@123'

    transp = MtomTransport()

    headers = transp.generate_http_headers(
        start_cid=cid,
        boundary=boundary,
    )

    assert cid in headers['Content-Type']
    assert boundary in headers['Content-Type']


def test_update_headers():
    prev_headers = {'test': 'abc', 'test2': 'def'}

    transp = MtomTransport()

    transp.update_headers(headers=prev_headers)

    for k, v in prev_headers.items():
        assert k in transp.headers.keys()
        assert v in transp.headers.values()


def test_add_files():
    file_content = b'file content 123'

    transp = MtomTransport()

    f_list = [
        MtomAttachment(file=BytesIO(file_content), file_name='f1'),
        MtomAttachment(file=BytesIO(file_content), file_name='f2')
    ]

    transp.add_files(files=f_list)

    for f in f_list:
        assert f in transp.files

    with pytest.raises(TypeError, match='must be MtomAttachment objects'):
        transp.add_files(files=['asgdhjsag'])  # type: ignore
