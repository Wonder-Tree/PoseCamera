import pathlib
from setuptools import setup, find_packages

current_dir = pathlib.Path(__file__).parent

README = (current_dir / "README.md").read_text()
REQUIREMENTS = (current_dir / "requirements.txt").read_text().splitlines()

setup(
    name="posecamera",
    version="2.1",
    description="Realtime Human Pose Estimation",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Wonder-Tree/PoseCamera",
    author="WonderTree",
    author_email="hello@wondertree.co",
    license="Apache-2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages= find_packages(),
    include_package_data=True,
    install_requires = REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "posecamera=posecamera.cli:main",
        ]
    },
)