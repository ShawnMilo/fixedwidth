from distutils.core import setup

setup(
    name='FixedWidth',
    packages=['fixedwidth'],
    version='1.0',
    description='Two-way fixed-width <--> Python dict converter.',
    author='Shawn Milochik',
    author_email='shawn@milochik.com',
    url='https://github.com/ShawnMilo/fixedwidth',
    download_url='https://github.com/ShawnMilo/fixedwidth/archive/1.0.tar.gz',
    install_requires=['six'],
    license='BSD',
    zip_safe=False,
    keywords='fixed width',
    test_suite="fixedwidth.tests",
    classifiers=[],
)
