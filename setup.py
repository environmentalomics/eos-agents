if __name__ == "__main__":

    from setuptools import setup

    with open("README.md") as f:
        README = f.read()

    requires = [
        "requests >= 2.5.1",    # For calling vCloud API
        "setproctitle",         # To show the running agent in process table
    ]

    setup(
        name='eos-agents',
        version='0.0.3',
        author='B. Collier',
        author_email='bmcollier@gmail.com',
        packages=['eos_agents', 'eos_agents.test'],
        keywords=['vCloud', 'VMware', 'API', 'Director', 'Air', 'Cloudhands', 'EOS'],
        license='LICENSE.md',
        description='Agents for administering a vCloud instance within the Cloudhands environment - EOS portal version.',
        long_description=README,
        install_requires=requires,
        test_suite="eos_agents.test",
    )
