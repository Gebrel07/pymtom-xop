import random
from io import BytesIO

import pytest

from pymtom_xop import MtomAttachment

FILE_PATH = "documents/python.pdf"
FILE_NAME = "python.pdf"


def test__handle_file_as_path():
    MtomAttachment._MtomAttachment__handle_file_as_path(FILE_PATH)  # type: ignore


def test__handle_file_as_bytesio():
    file = BytesIO(b'test 123')
    MtomAttachment._MtomAttachment__handle_file_as_bytesio(file, file_name='test123.pdf')  # type: ignore


def test__handle_file_input():
    MtomAttachment._MtomAttachment__handle_file_input(FILE_PATH)  # type: ignore

    file = BytesIO(b'test 123')
    with pytest.raises(ValueError, match='Error while handling file'):
        MtomAttachment._MtomAttachment__handle_file_input(file=file, file_name='')  # type: ignore

    MtomAttachment._MtomAttachment__handle_file_input(file=file, file_name='test.pdf')  # type: ignore

    # test as invalid type
    file = random.choice((b'test 123', 123, {'test': 123}))
    with pytest.raises(TypeError, match='Error while handling file'):
        MtomAttachment._MtomAttachment__handle_file_input(file=file)  # type: ignore


def test__get_content_type():
    att = MtomAttachment(file=FILE_PATH)
    setattr(att, 'file_name', '')
    with pytest.raises(AttributeError, match="file_name attribute is required"):
        att._MtomAttachment__get_content_type()  # type: ignore

    setattr(att, 'file_name', FILE_NAME)
    att._MtomAttachment__get_content_type()  # type: ignore

    assert att.content_type == 'application/pdf'


def test__generate_mime_headers():
    att = MtomAttachment(file=FILE_PATH)

    headers: bytes = att._MtomAttachment__generate_mime_headers()  # type: ignore

    header_lst = headers.splitlines()
    # remove empty and decode
    header_lst = [h.decode() for h in header_lst if h]

    validate_headers = [
        f'Content-Type: {att.content_type}',
        f'Content-Transfer-Encoding: {att.content_transfer_encoding}',
        f'Content-ID: {att.cid}',
        f'Content-Disposition: {att.content_disposition}; name="{att.file_name}"'
    ]

    assert header_lst == validate_headers


def test_init():
    att = MtomAttachment(FILE_PATH)

    assert att.content_transfer_encoding == 'binary'
    assert att.content_disposition == 'attachment'


def test_get_cid():
    att = MtomAttachment(FILE_PATH)
    cid = att.get_cid()

    assert isinstance(cid, bytes)
