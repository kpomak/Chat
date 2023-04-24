from setuptools import setup, find_packages


setup(
    name="devChat_server",
    version="0.1.0",
    description="server application",
    author="kpomak",
    author_email="romka_ne@mail.ru",
    packages=find_packages(),
    install_requires=[
        "pony>=0.7",
        "pyqt6>=6.4",
        "pyqt6-tools>=6.4.2",
        "pycryptodome>=3.17",
    ],
)
