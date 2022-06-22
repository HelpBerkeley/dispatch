import setuptools

setuptools.setup(
    name="dispatcher",
    version="0.0.1",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "gmaps==0.9.0",
        "googlemaps==4.2.0",
        "numpy==1.22.0",
    ],
)
