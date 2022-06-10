import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name='tclh',
    version='0.1.0',    
    description='Tools ',
    url='https://github.com/eufmike/tripodcats-little-helper',
    author='Mike Shih',
    author_email='m.cc.shih@gmail.com',
    license='BSD 2-clause',
    install_requires=['numpy'],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
