from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_desc = f.read()

setup(
    name="pymtom_xop",
    version="0.0.1",
    description="SOAP MTOM-XOP Support for Python",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://github.com/Gebrel07/pymtom-xop.git",
    author="Gabriel Santos",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    keywords=["SOAP", "MTOM-XOP", "WebService"],
    python_requires=">=3.10",
    install_requires=["zeep>=4.2.1"],
    extras_require={"dev": ["pytest>=7.4.0", "twine>=4.0.2"]},
    packages=find_packages(include=["pymtom_xop"])
)
