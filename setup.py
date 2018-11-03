from setuptools import setup

setup(name='pytwig',
      version='0.1.2',
      description='Library for modifying and creating Bitwig files. (Not affiliated with Bitwig at all. Something something trademark of Bitwig GmbH etc.)',
      url='',
      author='jaxter184',
      author_email='jaxter184@gmail.com',
      license='GPL3',
      packages=['pytwig'],
      zip_safe=False)

# python setup.py sdist upload

# so far, this library is designed to only accommodate the default Bitwig bytecode files rather than the JSON-style files
