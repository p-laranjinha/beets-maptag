import setuptools

# Mostly taken from:
# https://github.com/adammillerio/beets-copyartifacts

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="beets-maptag",
    version="0.0.4",
    description="beets plugin to help dynamically tag any database value",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/p-laranjinha/beets-maptag",
    license="MIT",
    platforms="ALL",
    packages=["beetsplug"],
    namespace_packages=["beetsplug"],
    install_requires=["beets"],
    classifiers=[
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Players :: MP3",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
