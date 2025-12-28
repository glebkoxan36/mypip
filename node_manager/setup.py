from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="node-manager",
    version="2.0.0",
    author="Crypto Node Manager",
    author_email="support@example.com",
    description="Universal cryptocurrency node manager for Nownodes API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/node-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
    },
    package_data={
        "node_manager": [
            "utils/*.py",
            "config/*.py",
        ],
    },
    include_package_data=True,
    keywords="crypto, blockchain, nownodes, litecoin, dogecoin, bitcoin, node, rpc, blockbook",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/node-manager/issues",
        "Source": "https://github.com/yourusername/node-manager",
        "Documentation": "https://github.com/yourusername/node-manager/wiki",
    },
)
