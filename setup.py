from setuptools import setup, find_packages

setup(
    name='logo_telebot',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        # list your project's dependencies here
        # e.g., 'requests >= 2.19.1',
    ],
    package_dir={""},
    entry_points={
    'console_scripts': [
            'logo_telebot=my_package.gui:main',
        ],
    },
    # Additional metadata about your project
    author="Yusuf Karaca",
    author_email="yusuf.karaca@logo.com.tr",
    description="Logo telebot demo",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  # This is important for README.md,
    python_requires=">=3.11"
)