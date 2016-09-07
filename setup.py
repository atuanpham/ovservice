from setuptools import setup

setup(
        name='ovservice',
        version='0.1',
        py_modules=['ovservice'],
        install_requires=[
            'Click',
            ],
        entry_points='''
            [console_scripts]
            ovservice=ovservice:cli
            ''',
)
