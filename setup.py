import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="advanced_logger-neilgoldman305",  # Replace with your own username
    version="0.1.0",
    author="Neil Goldman",
    author_email="neil@everymundo.com",
    description="A logger module with a few extra quality-of-life features not available in the base logger module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/everymundo/python_advanced_logger",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)
