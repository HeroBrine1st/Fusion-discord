import setuptools
import fusion

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='fusion',
    version=fusion.__version__,
    scripts=[],
    author=fusion.__author__,
    license=fusion.__license__,
    author_email="",
    description=fusion.__title__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HeroBrine1st/Fusion-discord",
    packages=setuptools.find_packages(),
    classifiers=[
        "",
    ],
    install_requires=["discord.py"]
)
