import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="srv",
    version="0.0.4",
    author="David Teresi",
    author_email="dkteresi@gmail.com",
    description="Serve a directory with one command",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dkter/srv",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Typing :: Typed",
    ],
    install_requires=setuptools.find_packages(),
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'srv = srv:main'
        ]
    },
)
