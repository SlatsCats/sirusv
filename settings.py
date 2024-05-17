"""
Configuration dictionary for MMOTop automation script.

Contains the following keys:
- vote_url (str): The URL of the voting page.
- user_name (str): The username for login, fetched from environment variable 'mmotop_login'.
- user_password (str): The password for login, fetched from environment variable 'mmotop_password'.
- server_rate (str): The server rate to vote for.
- sirus_account_name (str): The account name used for voting, fetched from environment 
  variable 'sirus_account_name'.
"""

import os


config = {
    "vote_url": "https://wow.mmotop.ru/servers/5130/votes/new",
    "user_name": os.getenv("mmotop_login", ""),
    "user_password": os.getenv("mmotop_password", ""),
    "server_rate": "x2",
    "sirus_account_name": os.getenv("sirus_account_name", ""),
    "browser": "chrome",
}
