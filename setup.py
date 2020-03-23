from setuptools import setup, find_packages
# more information at
# https://setuptools.readthedocs.io/en/latest/setuptools.html

setup(
  name='rocketchat_over_telegram',
  version="0.0.1",
  packages=find_packages(),

  author="Arthur Flam",
  author_email="arthur.flam@gmail.com",
  description="RocketChat client using a Telegram bot.",
  license="MIT",

  python_requires='>=3.6',
  install_requires=[
    'httpx',
    'websockets',
    'click',
  ],

  entry_points='''
      [console_scripts]
      rocketchat_over_telegram=rocketchat_over_telegram.bot:start_bot
  ''',
)
