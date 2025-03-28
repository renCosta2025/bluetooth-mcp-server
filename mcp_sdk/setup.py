from setuptools import setup, find_packages

setup(
    name='bluetooth-mcp-sdk',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'model-context-protocol-sdk'
    ],
    description='MCP SDK for Bluetooth Device Scanning',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/bluetooth-mcp-sdk',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)