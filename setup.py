from setuptools import setup, find_packages

setup(
    name='bandecocalendar',
    version='0.1',
    packages=find_packages(),
    
    url='https://github.com/athyrson06/bandeco-calendar',
    author='Athyrson M. Ribeiro',
    author_email='athyrsonmr@gmail.com',
    description='Integration from bandeco API to Google Calendar API',

    # Choose your license
    license='MIT',

    # Requirements
    install_requires=[
        'beautifulsoup4==4.12.0',
        'google_api_python_client==2.140.0',
        'protobuf==5.27.3',
        'Requests==2.32.3',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish 
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
