import setuptools
with open('README.md', 'r') as readme:
    README_TEXT = readme.read()

setuptools.setup(
    name='FixedWidth',
    packages=['fixedwidth'],
    version='1.3',
    description='Two-way fixed-width <--> Python dict converter.',
    long_description = README_TEXT,
    long_description_content_type='text/markdown',
    author='Shawn Milochik',
    author_email='shawn@milochik.com',
    url='https://github.com/ShawnMilo/fixedwidth',
    install_requires=['six'],
    license='BSD',
    keywords='fixed width',
    test_suite="fixedwidth.tests",
    classifiers=[],
)
