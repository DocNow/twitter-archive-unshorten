from setuptools import setup

__version__ = "0.0.7"

def long_description():
    with open("README.md") as f:
        return f.read()

setup(
    name="twitter_archive_unshorten",
    version=__version__,
    author="Ed Summers",
    author_email="ehs@pobox.com",
    license="MIT",
    py_modules=["twitter_archive_unshorten"],
    url="https://github.com/docnow/twitter-archive-unshorten",
    description="Unshorten the URLs in your Twitter archive",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    python_requires=">3.5.0",
    zip_safe=True,
    entry_points="""
        [console_scripts]
        twitter-archive-unshorten = twitter_archive_unshorten:main
    """,
)
