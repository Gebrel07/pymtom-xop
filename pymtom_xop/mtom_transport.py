from lxml.etree import _Element
from zeep.transports import Transport

from .mtom_attachment import MtomAttachment
from .soap_envelope import SoapEnvelope
from .xop_package import XopPackage


class MtomTransport(Transport):
    """
    Custom Transport class for MTOM requests

    Inherits from zeep.Transport

    Overrides the post_xml method from parent class

    Methods:
        - add_files: adds files to the MtomTransport
        - update_headers: update the headers used in the request

    Arguments from zeep.Transport:
        :param cache: The cache object to be used to cache GET requests
        :param timeout: The timeout for loading wsdl and xsd documents.
        :param operation_timeout: The timeout for operations (POST/GET). By default this is None (no timeout).
        :param session: A :py:class:`request.Session()` object (optional)

    """

    def __init__(self, cache=None, timeout=300, operation_timeout=None, session=None):
        super().__init__(cache, timeout, operation_timeout, session)

        self.files: list[MtomAttachment] = []

        self.headers: dict[str, str] = {}

    def generate_http_headers(self, start_cid: str, boundary: str | bytes):
        """Generates and sets the necessary HTTP MTOM-XOP headers for the request.

        Args:
            start_cid (str): Content-ID (cid) for the first part of the XOP Package. \
            Usually, this is the SOAP Envelope.
            boundary (str | bytes): boundary of the XOP Package.
        """
        if isinstance(boundary, bytes):
            boundary = boundary.decode()

        headers = {
            "MIME-Version": "1.0",
            "Content-Type": (
                "multipart/related; "
                'type="application/xop+xml"; '
                f'start="{start_cid}"; '
                'start-info="text/xml"; '
                f'boundary="{boundary}"'
            ),
        }

        return headers

    def update_headers(self, headers: dict[str, str]):
        """Adds or updates the headers attribute

        Args:
            headers (dict[str, str]): headers to add or update
        """
        self.headers.update(headers)
        return None

    def add_files(self, files: list[MtomAttachment]):
        """
            Adds files to be inserted in the MTOM message

            If the transport already has a list of files in it, \
            the new ones will be appended to the current list

            Arguments:
                - files: must be a list of MtomAttachment objects
        """
        for f in files:
            if not isinstance(f, MtomAttachment):
                raise TypeError(
                    f"files in the list must be MtomAttachment objects not {f.__class__.__name__}"
                )

        self.files.extend(files)
        self.__assert_unique_file_cids()
        return None

    def __assert_unique_file_cids(self):
        file_cids = []
        for f in self.files:
            if f.cid in file_cids:
                f.generate_new_cid()
            file_cids.append(f.cid)
        return None

    def post_xml(self, address: str, message: _Element, headers: dict[str, str]):
        """
        Overrides zeep.Transport post_xml method

        Parses MTOM message, adds HTTP headers, MIME headers and file data.

        Handles message back to Zeep for the POST request.
        """
        soap_env = SoapEnvelope(env_el=message, files=self.files)

        xop_pack = XopPackage(soap_env=soap_env, files=self.files)

        mtom_xop_headers = self.generate_http_headers(
            start_cid=soap_env.get_cid(), boundary=xop_pack.boundary
        )

        if not headers:
            headers = mtom_xop_headers
        else:
            headers.update(mtom_xop_headers)

        # give the message back to Zeep to be posted
        response = super().post(address, xop_pack.package, headers)

        return response
