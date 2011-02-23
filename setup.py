try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='friendfund',
    version='0.1',
    description='',
    author='',
    author_email='',
    url='',
    install_requires=[
        "Pylons>=0.9.7",
        "PIL>=1.1.7",
        "multiprocessing>=2.6.2.1",
        "pylibmc>=1.1.1",
        "FormEncode>1.2.2",
        "pyodbc>=2.1.8",
        "DBUtils>=1.0",
        "Babel==0.9.5"
    ],
    setup_requires=["PasteScript>=1.6.3"],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    package_data={'friendfund': ['i18n/*/LC_MESSAGES/*.mo']},
    message_extractors={'friendfund': [
            ('**.py', 'python', None),
            ('templates/**.html', 'mako', {'input_encoding': 'utf-8'}),
            ('partners/**.html', 'mako', {'input_encoding': 'utf-8'}),
            ('templates_partner/**.html', 'mako', {'input_encoding': 'utf-8'}),
            ('templates_free_form/**.html', 'mako', {'input_encoding': 'utf-8'}),
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
