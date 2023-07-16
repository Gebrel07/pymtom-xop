# **SOAP MTOM-XOP Support for Python**

This library adds SOAP MTOM-XOP support for python 3 using Python Zeep. 

The library uses custom classes to override the behavior of Python Zeep, tranforming a basic SOAP message into a MTOM-XOP message before handling it back to Zeep to be sent in a POST request.

Its main actors are the MtomTransport and MtomAttachment classes.

**MtomTransport** inherits from Zeep's Transport class and overrides its post_xml method.

**MtomAttachment** is used to represent each file in the request body.


## **How to use**

Consider the following type definitions in a WSDL where the operation name is "UploadFile":

``` xml
<xs:complexType name="uploadFileWs">
    <xs:sequence>
        <xs:element minOccurs="0" name="file" type="xs:base64Binary"/>
        <xs:element minOccurs="0" name="fileName" type="xs:string"/>
        <xs:element minOccurs="0" name="fileExtension" type="xs:string"/>
    </xs:sequence>
</xs:complexType>
```

To use this Web Service we can use the **MtomTransport** and **MtomAttachment** classes like this:

``` python
from pymtom_xop import MtomAttachment, MtomTransport
from zeep import Client, Settings

# create a MtomAttachment instance to represent the file
# the "file" argument can be a file path or a BytesIO object, in this case, lets use a file stored in the "documents" folder
mtom_attachment = MtomAttachment(file="documents/python.pdf")

# use MtomTransport instead of Zeep's standard Tranport
mtom_transport = MtomTransport()
# use the add_files method to add files to the transport
# the "files" argument must be a list of MtomAttachment objects
mtom_transport.add_files(files=[mtom_attachment])

# set up a Client using MtomTransport
client = Client(wsdl="documents/UploadWSDL.wsdl", transport=mtom_transport)

# WARNING: namespace might change according to your Webservice's configuration
factory = client.type_factory(namespace="ns0")

# build SOAP Envelope normally using Zeep
# NOTE: use mtom_attachment's get_cid method to insert the attachment's Content-ID in the "file" field
arg0 = factory.uploadFileWs(
    file=mtom_attachment.get_cid(),
    fileName="python",
    fileExtension="pdf"
)

# call the service normally using Zeep
response = client.service.uploadFile(arg0)
```

## **Classes**

### **MTOMAttachment:**

The **MTOMAttachment** class is responsible for setting up all of the necessary information about the file before adding it to the request body.

When inserting a file in the SOAP Envelope, the get_cid method must be used in place of the file's binary data.

**Methods**

get_cid:

    Returns cid without the < > parts

    Returns:
        bytes: File's Content-ID

        Example: b"168954589437.10472.2748258243972472116@pymtom-xop"

### **MTOMTransport:**

After calling the service's operation, Zeep will parse the SOAP message as it normally does. The SOAP message and HTTP headers will be passed on to the **MTOMTransport** class.

**MTOMTransport** uses its methods to transform the SOAP message into a MTOM-XOP message, adds the necessary HTTP headers and gives it back to **Zeep** to be sent as a **POST** request.

MTOMTransport objects will accept any of zeep Tranport arguments when initialized, such as: cache, timeout, operation_timeout, session etc...

## **Examples**

- See "documents" folder for examples of MTOM Request and Response in XML
- See "demo.py" for demonstration of a request 


## **References:**

- inspired by pymtom by zvolsky (https://github.com/pyutil/pymtom)
- based on requests made with SOAPUI

See https://docs.python-zeep.org/en/master/ for Python Zeep's official documentaion.