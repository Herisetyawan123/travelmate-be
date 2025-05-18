from setuptools import setup

requires = [
    'pyramid',
    'sqlalchemy',
    'psycopg2-binary',
    'pyjwt',
    'pyramid_sockjs',
    'python-dotenv',
    'waitress',
    'passlib',
    'bcrypt',
    'pyramid-apispec',
    'werkzeug',
    'websockets',
    'aiohttp',
    'requests',
]

setup(
    name='travelmate',
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = travelmate.__init__:main',
        ],
    },
)
