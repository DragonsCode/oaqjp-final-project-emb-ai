from setuptools import find_packages, setup

setup(
    name="EmotionDetection",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.34.2,<3",
    ],
    author="DragonsCode",
    description="A package for emotion detection using Watson NLP",
    license="MIT",
)