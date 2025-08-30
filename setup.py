"""
Setup script for VRChat Proximity App
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = [
        'PyQt6>=6.5.0',
        'numpy>=1.24.0',
        'python-osc>=1.8.0',
        'PyYAML>=6.0',
        'platformdirs>=3.0.0',
        'psutil>=5.9.0',
        'aiofiles>=23.0',
        'websockets>=11.0',
    ]

setup(
    name="vrchat-proximity-app",
    version="1.0.0",
    author="VRChat Proximity Team",
    description="Proximity-based user visibility control for VRChat",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vrchat-proximity/vrchat-proximity-app",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Environment :: X11 Applications :: Qt",
        "Environment :: Win32 (MS Windows)",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "vr": ["openvr>=1.21.4"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0", "mypy>=1.0.0"],
    },
    entry_points={
        "console_scripts": [
            "vrchat-proximity=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.json"],
    },
)
