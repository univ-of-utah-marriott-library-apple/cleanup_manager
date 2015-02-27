from distutils.core import setup
import cleanup_management

setup(
    name='Cleanup Manager',
    version=cleanup_management.__version__,
    url='https://github.com/univ-of-utah-marriott-library-apple/cleanup_manager',
    author='Pierce Darragh, Marriott Library IT Services',
    author_email='mlib-its-mac-github@lists.utah.edu',
    description=("Cleanup Manager helps you clean up folders on your Mac's hard drive."),
    license='MIT',
    packages=['cleanup_management'],
    package_dir={'cleanup_management': 'cleanup_management'},
    scripts=['cleanup_manager.py'],
    classifiers=[
        'Development Status :: 5 - Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration'
    ],
)
