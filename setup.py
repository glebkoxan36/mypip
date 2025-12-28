from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="node-manager",
    version="2.1.0",
    author="Gleb Koxan",
    author_email="glebkoxan36@gmail.com",
    description="Универсальный менеджер криптовалютных нод с поддержкой Nownodes и веб-панелью",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/glebkoxan36/node-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.8.0",
        "websockets>=11.0.0",
        "PyYAML>=6.0",
        "python-dotenv>=1.0.0",
        "bip-utils>=2.7.0",
        "bcrypt>=4.0.0",
        "pyjwt>=2.0.0",
        "psutil>=5.9.0",
        "aiohttp_cors>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.0.0",
        ],
        "telegram": [
            "aiogram>=2.25.0",
        ],
        "monitoring": [
            "prometheus-client>=0.17.0",
        ],
        "web": [
            # Веб-зависимости уже включены в install_requires
        ]
    },
    entry_points={
        "console_scripts": [
            "node-manager=node_manager.cli:main",
            "node-manager-web=node_manager.web.server:web_server_cli",
        ],
    },
    package_data={
        "node_manager": [
            "web/static/*",
            "web/templates/*",
        ],
    },
    include_package_data=True,
    keywords=[
        "cryptocurrency",
        "bitcoin",
        "litecoin",
        "dogecoin",
        "blockchain",
        "node",
        "manager",
        "api",
        "web",
        "dashboard",
        "monitoring",
        "collection",
    ],
    project_urls={
        "Bug Reports": "https://github.com/glebkoxan36/node-manager/issues",
        "Source": "https://github.com/glebkoxan36/node-manager",
        "Documentation": "https://github.com/glebkoxan36/node-manager/wiki",
    },
)
