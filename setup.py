import os
import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

# Get version from environment variable or fallback to a default value
version = os.getenv("PACKAGE_VERSION", "0.0.1")  # Default to '0.0.7' if not provided

setuptools.setup(
    name="fastapi-extended-query-method",
    version=version,  # Use the dynamic version from the environment variable
    author="Jorge Cardona",
    description="Native HTTP QUERY method support for FastAPI with automatic cache control and Swagger compatibility.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jorgecardona/fastapi-extended-query-method",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi>=0.139.0",
        "uvicorn>=0.5.1",
        "requests>=2.34.2",
        "requests-cache>=1.3.3",
        "tabulate>=0.10.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: FastAPI",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=[
        "fastapi",
        "query",
        "http-query",
        "openapi",
        "swagger",
        "rest",
        "api",
        "middleware",
    ],
    python_requires=">=3.10",
)