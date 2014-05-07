from setuptools import setup, find_packages

setup(
    name='friendfund',
    version='2.3.1_rc2',
    description='',
    author='',
    author_email='',
    url='',
    install_requires=[
        "pyodbc>=2.1.8",
        "Pylons==1.0.1",
        "pastedeploy", 
        "pastescript", 
        "PIL>=1.1.7",
        "FormEncode>=1.2.2",
        "DBUtils>=1.0",
        "httplib2",
        "Babel",
        "dnspython",
        "ZSI",
        "markupsafe",
        "BeautifulSoup>=3.2.0",
        "lxml",
        "celery"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'friendfund': ['i18n/*/LC_MESSAGES/*.mo']},
    message_extractors={'friendfund': [
            ('**.py', 'python', None),
            ('templates/**.html', 'mako', {'input_encoding': 'utf-8'}),
            ('public/**', 'ignore', None)]},
    zip_safe=False,
    paster_plugins=['PasteScript', 'Pylons'],
    entry_points="""
    [paste.app_factory]
    main = friendfund.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller
    """,
)
