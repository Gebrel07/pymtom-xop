"""
    pymtom_xop
    ---------

    Converts a basic SOAP message from Zeep into a MTOM-XOP package.

    Its classes are responsible for adapting the message body, and adding the \
    necessary HTTP headers before handling the message back to Zeep to be sent \
    as a POST request.
"""
from .mtom_attachment import MtomAttachment
from .mtom_transport import MtomTransport

__all__ = ["MtomAttachment", "MtomTransport"]
