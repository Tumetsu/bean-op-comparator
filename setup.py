from setuptools import setup

setup(name='op_bean_compare',
      version='0.1',
      description='Compare OP and Beancount ledgers and report differences.',
      author='Tuomas Salmi',
      license='MIT',
      packages=['op_bean_compare'],
      scripts=['bin/op-bean-compare'])
