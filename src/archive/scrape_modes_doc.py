"""

"""
import requests

login = "https://www.modes.org.uk/site/login.html"
url = 'https://www.modes.org.uk/members/user-guides.html'
# url = 'https://www.modes.org.uk'
url = 'https://www.modes.org.uk/assets/files/complete/Setting%20up%20grids.pdf'
payload = {
    'username': 'mike.gleen@heathrobinsonmuseum.org',
    'password': 'Kestrel,49'
}


# with requests.Session() as session:
#     post = session.post(login, data=payload)
#     print(post)
#     page = session.get(url, verify=False)
#     print(len(page.content))

page = requests.get(url)
print(len(page.content))
