from setuptools import setup
import os

requirements = ['clihelper', 'requests']

scripts = ['github_issue_autoresponder=github_issue_autoresponder:main']

# Build the path to install the support files
base_path = '/usr/share/github_issue_autoresponder'
data_files = dict()
data_paths = ['etc']
for data_path in data_paths:
    for dir_path, dir_names, file_names in os.walk(data_path):
        install_path = '%s/%s' % (base_path, dir_path)
        if install_path not in data_files:
            data_files[install_path] = list()
        for file_name in file_names:
            data_files[install_path].append('%s/%s' % (dir_path, file_name))
with open('MANIFEST.in', 'w') as handle:
    for path in data_files:
        for filename in data_files[path]:
            handle.write('include %s\n' % filename)

setup(name='github_issue_autoresponder',
      version='1.0.2',
      author='Gavin M. Roy',
      author_email='gavinmroy@gmail.com',
      py_modules=['github_issue_autoresponder'],
      url='https://github.com/gmr/github_issue_autoresponder',
      install_requires=requirements,
      data_files=[(key, data_files[key]) for key in data_files.keys()],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Topic :: Utilities'],
      entry_points={'console_scripts': scripts},
      zip_safe=True)
