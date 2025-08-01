from setuptools import setup, find_packages

setup(
    name='codeinsight',
    version='0.1',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
'click',
        'typer',
        'rich',
        'fastapi',
        'uvicorn[standard]',
        'pydantic',
        'python-dotenv',
        'langchain',
        'ollama',
        'chromadb',
        'sentence-transformers',
        'httpx',
        'beautifulsoup4',
        'lxml',
        'aiohttp',
        'pathlib',
        'typing-extensions',
        'asyncio',
        'pytest',
        'black',
        'flake8',
        'mypy',
    ],
    entry_points={
        'console_scripts': [
            'codeinsight=codeinsight.cli.main:main',
        ],
    },
)
