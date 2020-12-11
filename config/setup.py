from setuptools import setup

setup(
    name='code_clinics',
    version='0.1.0',
    packages=['code_clinics', 'booking','view_calendar', 'volunteer','cancel_volunteering'],
    entry_points={
        'console_scripts': [
            'code_clinics = code_clinics.__main__:main'
        ]
    }
)
