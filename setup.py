from setuptools import setup

setup(
    name='esse3api',
    packages=['esse3api'],
    include_package_data=True,
    install_requires=[
        'flask','pycurl'
    ],
)
