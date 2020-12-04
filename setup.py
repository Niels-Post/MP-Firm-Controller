import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

long_description = "yeet"

setuptools.setup(
    name="warehouse_pmsv_tracker",
    version="1.0",
    author="Niels Post",
    author_email="niels.post.97@gmail.com",
    description="/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows 10, Linux",
    ],
    python_requires='>=3.7.3',
)
