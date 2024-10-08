import setuptools
import subprocess

version = "9999"
try:
    ret = subprocess.run(
        "git describe --tags --abbrev=0",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        shell=True,
    )
    version = ret.stdout.decode("utf-8").strip()
except:
    pass


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sphinxext-delta",
    version=version,
    author="Vasista Vovveti, Dalton Smith",
    author_email="daltzsmith@gmail.com",
    description="Sphinx extension for listing changed Sphinx articles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wpilibsuite/sphinxext-delta",
    install_requires=["sphinx>=2.0", "six", "requests"],
    packages=["sphinxext"],
    classifiers=[
        "Environment :: Plugins",
        "Environment :: Web Environment",
        "Framework :: Sphinx :: Extension",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)
