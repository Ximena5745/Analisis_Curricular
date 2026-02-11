"""
Setup script para el proyecto de análisis microcurricular.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Leer README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Leer requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f
                       if line.strip() and not line.startswith('#')]
else:
    requirements = []

setup(
    name="analisis-microcurricular",
    version="1.0.0",
    author="Coordinación Académica",
    author_email="coordinacion@institucion.edu",
    description="Sistema de análisis automatizado de diseños microcurriculares",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/institucion/analisis-microcurricular",
    packages=find_packages(exclude=["tests", "tests.*", "docs"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'analisis-curricular=src.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.txt', '*.md', '*.yaml', '*.yml'],
        'templates': ['*.html', '*.css'],
    },
    zip_safe=False,
)
