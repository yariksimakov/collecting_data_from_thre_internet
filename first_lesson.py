import requests as rqt
import pprint as pp
import json

user_name= 'yariksimakov'
url = 'https://api.github.com/users/' + user_name

data = rqt.get(url)
dict_data = data.json()
# I received general information about user
pp.pprint(dict_data)

# repos_url = 'https://api.github.com/users/yariksimakov/repos'
dict_repos = rqt.get(dict_data['repos_url']).json()
# pp.pprint(dict_repos)

repos_names = []
for value in dict_repos:
    repos_names.append(value['name'])

print(repos_names)

# Save got format json in file
with open('repos_dict.json', 'w') as file:
    json.dump(dict_repos, file)
