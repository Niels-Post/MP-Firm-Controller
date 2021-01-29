#
# Copyright (c) 2021. Niels Post. AI Lab Vrije Universiteit Brussel.
#
# This file is part of MP-Firm.
#
# MP-Firm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MP-Firm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with MP-Firm.  If not, see <https://www.gnu.org/licenses/>.
#


import setuptools

long_description = open("README.md").read()

setuptools.setup(
    name="warehouse_pmsv_tracker",
    version="1.0",
    author="Niels Post",
    author_email="niels.post.97@gmail.com",
    description="/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.ai.vub.ac.be/multi-agent-benchmarking/warehouse-pmsv-tracker",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: GPL v3",
        "Operating System :: Linux"
    ],
    license=open("COPYING").read(),
    python_requires='>=3.7.3',
)
