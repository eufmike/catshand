import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name='catshand',
    version='0.1.1',
    author='Mike Chien-Cheng Shih',
    author_email='m.cc.shih@gmail.com',
    description='Tools for Podcast editing',
    url='https://github.com/eufmike/catshand',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='BSD 2-clause',
    install_requires=['numpy'],
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
    package_dir={"": "src"},
    entry_points={
        'console_scripts':[
            'prjpre = catshand.tools.prjpre:main', 
            'prjpost = catshand.tools.prjpost:main',
            'audmerger = catshand.tools.audmerger:main',
            'audacitypipe = catshand.tools.audacitypipe:main',
            'linkparser = catshand.tools.linkparser:main',
            'highlight = catshand.tools.highlight:main',
        ]
    },
    packages=setuptools.find_packages(where="src"),
    python_requires='>=3.9',
    
)
