from setuptools import setup, find_packages


setup(
    name='GSense',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'napari',
        'numpy',
        'imageio',
        'scikit-image',
        'transformers',
        'qtpy',
        'pillow',
        'spectral',
    ],
    extras_require={
        'torch': ['torch', 'torchvision', 'torchaudio']  # Optional torch dependencies
    },
    entry_points={
        'console_scripts': [
            'gsense=app.main:main', # Command to run the app
        ],
    },
    author='Ayesha Naikodi',
    author_email='ma.naikodi@ufl.edu',
    description='A Napari-based tool for hyperspectral image analysis and segmentation',
    keywords='hyperspectral image analysis segmentation',
    url='https://github.com/GatorSense/GSense',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Programming Language :: Python :: 3',
    ],
)
