import setuptools

setuptools.setup(
    name="dispatcher",
    version="0.0.1",
    package_dir={"": "src"},
    py_modules=['dispatcher'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
