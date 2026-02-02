#!/usr/bin/env python3
"""
AI Video Dubbing Warehouse - 标准项目架构

重构项目为标准Python项目结构，提升可维护性和可扩展性。
"""

from setuptools import setup, find_packages

setup(
    name="ai-video-dubbing",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
)
