#!/usr/bin/env python
"""
Setup script for Cash Manager
"""

import os

from setuptools import find_packages, setup

# Read the contents of README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


# Read requirements
def read_requirements(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


setup(
    name="cash-manager",
    version="1.0.0",
    author="Cash Manager Contributors",
    author_email="qinjie545@163.com",
    description="一个简单易用的零钱管理系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qinjie545/kids-pocketmoney",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Education",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "docker": [
            "gunicorn>=21.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cash-manager=backend.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["frontend/templates/*.html", "backend/database/*.sql"],
    },
    project_urls={
        "Homepage": "https://github.com/qinjie545/kids-pocketmoney",
        "Repository": "https://github.com/qinjie545/kids-pocketmoney",
        "Issues": "https://github.com/qinjie545/kids-pocketmoney/issues",
        "Changelog": "https://github.com/qinjie545/kids-pocketmoney/blob/main/CHANGELOG.md",
        "Documentation": "https://github.com/qinjie545/kids-pocketmoney/blob/main/README.md",
    },
)
