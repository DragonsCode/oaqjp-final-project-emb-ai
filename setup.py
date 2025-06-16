from setuptools import setup, find_packages

setup(
    name="EmotionDetection",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    author="DragonsCode",
    description="A package for emotion detection using Watson NLP",
    license="MIT",
)