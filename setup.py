from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="secret_fetcher",  # Required
    version="0.3.0",  # Required
    description="Fetch deployment variables from kubernetes and write local .env file.",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    author="parklez",  # Optional
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="kubernetes, secrets, dotenv",  # Optional
    packages=find_packages(),  # Required
    python_requires=">=3.7, <4",
    install_requires=["click<9", "pyyaml<7"],  # Optional
    entry_points={
        'console_scripts': [
            'secrets=secret_fetcher.main:cli'
        ]
    },
    project_urls={  # Optional
        "Bug Reports": "https://github.com/parklez/deployment-secrets-dotenv/issues",
        "Source": "https://github.com/parklez/deployment-secrets-dotenv",
    },
)