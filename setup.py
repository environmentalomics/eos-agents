from distutils.core import setup

setup(
    name='eos-agents',
    version='0.0.2.1',
    author='B. Collier',
    author_email='bmcollier@gmail.com',
    packages=['eos_agents', 'eos_agents.test'],
    keywords=['vCloud', 'VMware', 'API', 'Director', 'Air', 'Cloudhands', 'EOS'],
    license='LICENSE.md',
    description='Agents for administering a vCloud instance within the Cloudhands environment - EOS portal version.',
    long_description=open('README.md').read(),
    install_requires=[
        "requests >= 2.5.1"
    ],
)