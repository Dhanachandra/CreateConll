from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["ipython>=6", "nbformat>=4", "requests>=2"]

setup(
    name="CreateConll",
    version="0.0.1",
    author="Dhanachandra",
    author_email="dhana1991@gmail.com",
    description="Converting annotated data for NER to Conll format",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/Dhanachandra/CreateConll",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        #"License :: Unlicience",
    ],
)
