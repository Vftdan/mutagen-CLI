from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "requirements.txt"), "r") as f:
    install_requires = f.read().splitlines()

classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    # ? "Intended Audience :: End Users/Desktop",
    # "License :: OSI Approved :: ??)",
    "Programming Language :: Python",
    "Topic :: Multimedia :: Sound/Audio",
    ]

setup(
    name="mutagen-CLI",
    version="0.2",
    desciption="a mutagen frontend that handles universal ID3 music tagging.",
    url="https://github.com/Vftdan/mutagen-CLI",
    author="Lingnan Dai; Vftdan",
    license="",
    classifiers=classifiers,
    keywords="mp3 mp4 m4a xmp id3 tagger command-line",
    packages=find_packages(),
    include_package_data=True,
    scripts=[
    ],
    install_requires=install_requires,
    entry_points={
        "console_scripts": "mutagenc = mutagenc.cli:main"
    }
)
