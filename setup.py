from pathlib import Path

from setuptools import find_packages, setup

VERSION = '0.0.5.dev1'

this_dir = Path(__file__).parent
long_description = this_dir.joinpath('README.md').read_text()
requirements = this_dir.joinpath('requirements.txt').read_text()

setup(
    name="streamyard-downloader",
    version=VERSION,
    description="Download Past Broadcast from StreamYard",
    keywords="streamyard downloader scrapper",
    url="https://github.com/gabubellon/streamyard-downloader",
    author="Gabriel (Gabu) Bellon",
    author_email="gabubellon@gmail.com",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.8",
    project_urls={
        "Source": "https://github.com/gabubellon/streamyard-downloader",
    },
    entry_points={
        'console_scripts': [
            "streamyard-downloader = streamyard_down.__main__:main"
            ]
    }
)
