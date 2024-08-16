from setuptools import setup, find_packages

setup(
    name="mongodesu",
    version="1.1.0",
    description="A mongodb ODM dependant on pymongo with the extensive of model creation and validation and relational model machanism. This helps you create the ODM in the python program with the similarities of an SQL class model.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Akuyaku",
    author_email="babai.akuyaku@gmail.com",
    url="https://github.com/AKA-Per/mongudesu",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "pymongo==4.8.0",
        "inflect==7.3.1"
    ],
)
