import os
from email.utils import make_msgid
from io import BytesIO
from mimetypes import guess_type

from .constants import PYMTOM_XOP_DOMAIN


class MtomAttachment:
    """Represents a file to be added in the XOP package.

    When initialized, this class will generate the necessary data \
    to be used when attaching it to the XOP package.

    Arguments:
        - file (str | bytesIO): path to file (str) or BytesIO object \
        representation of the file's data
        - file_name (str, optional): name of the file (must contain file extension). \
        This is mandatory if the file argument is a BytesIO object.

    Methods:
        - get_cid (returns bytes): gets the object's Content-ID without < >
    """

    def __init__(self, file: str | BytesIO, file_name: str | None = None) -> None:
        # File infos
        self.file_path: str | None
        self.file_name: str
        self.file_data: bytes

        self.__handle_file_input(file=file, file_name=file_name)

        # MIME header attributes
        self.content_type = self.__get_content_type()
        self.content_transfer_encoding: str = "binary"
        self.cid: str = make_msgid(domain=PYMTOM_XOP_DOMAIN)
        self.content_disposition: str = "attachment"

        self.mime_headers: bytes = self.__generate_mime_headers()

        # used in SOAP Envelope
        # NOTE: must be xop:include according to https://www.w3.org/TR/2005/REC-xop10-20050125/#xop_href
        # self.href: bytes = f'<xop:Include href="cid:{self.cid[1:-1]}" xmlns:xop="{XOP_INCLUDE_NS}"/>'.encode()
        # self.href: bytes = f'<inc:Include href="cid:{self.cid[1:-1]}" xmlns:inc="http://www.w3.org/2004/08/xop/include"/>'.encode()

    def generate_new_cid(self):
        '''Sets a new random cid for the MtomAttachment'''
        self.cid = make_msgid(domain=PYMTOM_XOP_DOMAIN)
        return None

    def get_cid(self) -> bytes:
        '''Returns cid without the < > parts'''
        return self.cid[1:-1].encode()

    def __generate_mime_headers(self) -> bytes:
        headers = (
            f"Content-Type: {self.content_type}\r\n"
            f"Content-Transfer-Encoding: {self.content_transfer_encoding}\r\n"
            f"Content-ID: {self.cid}\r\n"
            f'Content-Disposition: {self.content_disposition}; name="{self.file_name}"\r\n\r\n'
        )
        return headers.encode()

    @classmethod
    def __handle_file_input(cls, file: str | BytesIO, file_name: str | None = None):
        if isinstance(file, str):
            cls.__handle_file_as_path(file=file)
        elif isinstance(file, BytesIO):
            if not file_name:
                raise ValueError("Error while handling file, file_name must be provided if file is a BytesIO object")
            cls.__handle_file_as_bytesio(file=file, file_name=file_name)
        else:
            raise TypeError("Error while handling file, file must be a file path (str) or BytesIO object")
        return None

    @classmethod
    def __handle_file_as_path(cls, file: str):
        cls.file_path = file
        cls.file_name = os.path.basename(file)
        with open(file, mode="rb") as f:
            cls.file_data = f.read()
        return None

    @classmethod
    def __handle_file_as_bytesio(cls, file: BytesIO, file_name: str):
        cls.file_path = None
        cls.file_name = file_name
        cls.file_data = file.read()
        return None

    def __get_content_type(self) -> str:
        if not self.file_name:
            raise AttributeError('file_name attribute is required for setting content_type')
        return guess_type(self.file_name)[0] or "application/octet-stream"
