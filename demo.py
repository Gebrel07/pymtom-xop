import responses
from requests import Response
from zeep import Client, Settings

from pymtom_xop import MtomAttachment, MtomTransport


@responses.activate
def demo_request() -> Response:
    # adding a mock response just for the demonstration
    responses.add(
        responses.POST,
        "https://service-test.com/UploadFileWs",
        body="this is a mock response",
        status=200,
    )

    # create a MtomAttachment instance to represent the file
    att = MtomAttachment(file=r"documents/python.pdf")

    # use MtomTransport instead of Zeep's standard Tranport
    transp = MtomTransport()
    # add files to transport as a list of MtomAttachment objects
    transp.add_files(files=[att])

    # using raw response here just to be able to see the request body after
    conf = Settings(raw_response=True)  # type: ignore

    # set up CLient using MtomTransport
    client = Client(wsdl=r"documents/UploadWSDL.wsdl", transport=transp, settings=conf)

    # WARNING: namespace might change according to Webservice's configuration
    factory = client.type_factory(namespace="ns0")

    # build SOAP Envelope normally using Zeep
    arg0 = factory.uploadFileWs(
        file=att.get_cid(), fileName="python", fileExtension="pdf"
    )

    # call the service normally using Zeep
    return client.service.uploadFile(arg0)


# execute the demonstration
resp = demo_request()

print(f"Request Headers: {resp.request.headers}", end="\n\n")

msg: bytes = resp.request.body
end_of_msg = msg.index(b"%PDF-1") - 1

print(f"Request Body:\n\n{msg[:end_of_msg].decode()}")
print("###file's binary data goes here###", end="\n\n")
print("--final boundary goes here--")
