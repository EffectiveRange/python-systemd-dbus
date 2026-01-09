from setuptools import setup


setup(
    name='python-systemd-dbus',
    description='Python dbus interface library for systemd',
    author='Ferenc Nandor Janky & Attila Gombos',
    author_email='info@effective-range.com',
    packages=['systemd_dbus'],
    package_data={'systemd_dbus': ['py.typed']},
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=['dbus-python',
                      'python-context-logger@git+https://github.com/EffectiveRange/python-context-logger.git@latest']
)
