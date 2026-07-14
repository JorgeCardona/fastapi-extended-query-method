import os
import setuptools

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

# Get version from environment variable or fallback to a default value
version = os.getenv("PACKAGE_VERSION", "0.0.1")  # Default to '0.0.1' if not provided

setuptools.setup(
    name="fastapi-extended-query-method",
    version=version,
    author="Jorge Cardona",
    description="Native HTTP QUERY method support for FastAPI with automatic cache control and Swagger compatibility.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JorgeCardona/fastapi-extended-query-method",
    package_dir={"": "src"},
    py_modules=["fastapi_extended_query_method"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "fastapi>=0.139.0",
        "uvicorn>=0.5.1",
        "requests>=2.34.2",
        "requests-cache>=1.3.3",
        "tabulate>=0.10.0",
    ],
)
