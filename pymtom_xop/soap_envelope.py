from base64 import b64encode

from lxml import etree
from lxml.etree import _Element, _ElementTree
from zeep.wsdl.utils import etree_to_string

from .constants import PYMTOM_XOP_DOMAIN, XOP_INCLUDE_NS
from .mtom_attachment import MtomAttachment


class SoapEnvelope:
    def __init__(self, env_el: _Element, files: list[MtomAttachment]) -> None:
        """
        Represents the SOAP Envelope (XML) to be added in the XOP package.

        This class sets up the necessary configurations for the SOAP Envelope to be included \
        as a part of the XOP package.
        """
        self.soap_env: _Element = env_el
        self.files: list[MtomAttachment] = files
        self.xop_env: _ElementTree = self.__optimize_envelope()

        # MIME header attributes
        self.content_type: str = "application/xop+xml"
        self.type: str = "text/xml"
        self.charset: str = "UTF-8"
        self.content_transfer_encoding: str = "8bit"
        self.cid: str = f"<rootpart@{PYMTOM_XOP_DOMAIN}>"

        self.mime_headers: bytes = self.__generate_mime_headers()

    def get_xop_env_as_bytes(self) -> bytes:
        return etree_to_string(node=self.xop_env)

    def get_cid(self) -> str:
        '''Returns cid without the < > parts'''
        return self.cid[1:-1]

    def __generate_mime_headers(self) -> bytes:
        headers = (
            f'Content-Type: {self.content_type}; charset={self.charset}; type="{self.type}"\r\n'
            f"Content-Transfer-Encoding: {self.content_transfer_encoding}\r\n"
            f"Content-ID: {self.cid}\r\n\r\n"
        )
        return headers.encode()

    def __optimize_envelope(self):
        """Finds the tags in the SOAP Envelope containing each MtomAttachment's cid \
        , removes the base64 encoded data and adds a 'xop:include' tag in its place.
        """
        # NOTE: convert to ElementTree so that getpath() is avaliable on it's children
        el_tree: _ElementTree = etree.ElementTree(self.soap_env)

        # look for element that contains the file's cid and place insert xop tag
        for f in self.files:
            b64_cid: str = b64encode(f.get_cid()).decode()
            plain_cid: str = f.get_cid().decode()

            # find element by base64 encoded cid as its text content
            el: _Element = self.__find_elements_by_text(
                element_tree=el_tree, cid=b64_cid
            )[0]

            if el is None:
                continue

            xop_el: _Element = self.__create_xop_include_element(
                cid=plain_cid, prev_nsmap=el.nsmap
            )

            # remove text content and add xop tag as child element
            el.text = None
            el.insert(index=0, element=xop_el)

        return el_tree

    @staticmethod
    def __find_elements_by_text(element_tree: _ElementTree, cid: str) -> list[_Element]:
        """Finds elements in the _ElementTree  by xpath based on their text content (cid)

        Args:
            element_tree (_ElementTree): _ElementTree containing the desired tags
            cid (str): content id of the message part (usually MtomAttachment)

        Returns:
            list[_Element]: list of matching elements in the _ElementTree
        """
        # using exact match
        els: list[_Element] = element_tree.xpath(f'//*[text()="{cid}"]')

        # using contains
        # el = xml2.xpath(f'//*[contains(text(), "{ENCODED_CID.decode()}")]')

        return els

    @staticmethod
    def __create_xop_include_element(
        cid: str, prev_nsmap: dict[str, str] | None = None
    ) -> _Element:
        """
        Args:
            cid (str): must not contain < or >
            prev_nsmap (dict[str, str], optional): nsmap of parent element. Defaults to None.

        Returns:
            XOP Include tag.

        Example:
        <xop:Include href="123456@domain.com" xmlns:inc="http://www.w3.org/2004/08/xop/include"/>
        """
        ns_map = {"xop": XOP_INCLUDE_NS}

        if prev_nsmap and isinstance(prev_nsmap, dict):
            ns_map.update(prev_nsmap)

        el = etree.Element(
            f"{{{XOP_INCLUDE_NS}}}Include", nsmap=ns_map, attrib={"href": f"cid:{cid}"}
        )

        return el
