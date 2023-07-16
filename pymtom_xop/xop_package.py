from uuid import uuid4

from .mtom_attachment import MtomAttachment
from .soap_envelope import SoapEnvelope


class XopPackage:
    def __init__(self, soap_env: SoapEnvelope, files: list[MtomAttachment]) -> None:
        """Represents the XOP package that is sent as the request body.

        Args:
            soap_env (SoapEnvelope): SOAP Envelope object
            files (list[MTOMAttachment]): List of files to be added in XOP Package
        """
        self.soap_env: SoapEnvelope = soap_env
        self.files: list[MtomAttachment] = files

        self.boundary: bytes = b"uuid:" + str(uuid4()).encode()

        self.package: bytes = self.__parse_package()

    def __parse_package(self):
        # initial boundary
        xop_package = b"--" + self.boundary + b"\r\n"

        # SOAP Envelope's MIME headers
        xop_package += self.soap_env.mime_headers
        # XOP optimized SOAP Envelope
        xop_package += self.soap_env.get_xop_env_as_bytes() + b"\r\n"

        # MTOMAtachments
        for att in self.files:
            xop_package += b"--" + self.boundary + b"\r\n"
            xop_package += att.mime_headers
            xop_package += att.file_data + b"\r\n"

        # final boundary
        xop_package += b"--" + self.boundary + b"--"

        return xop_package
