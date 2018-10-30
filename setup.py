import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="riscv-model",
    use_scm_version={
        "relative_to": __file__,
        "write_to": "riscvmodel/version.py",
    },
    author="Stefan Wallentowitz",
    author_email="stefan@wallentowitz.de",
    description="RISC-V Model",
    long_description=long_description,
    url="https://github.com/wallento/riscv-python-model",
    packages=setuptools.find_packages(),
    entry_points={
      'console_scripts': [
         'riscv-random-asm = riscvmodel.random:gen_asm',
         'riscv-random-asm-check = riscvmodel.random:check_asm',
         'riscv-machinsn-decode = riscvmodel.code:machinsn_decode'
      ],
    },
    setup_requires=[
        'setuptools_scm',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)