from ewelink import EWeLink

email = "mattia.millebolle@gmail.com"
password = "Millebolle.1"
region = "eu"  # per Europa

ewelink = EWeLink(email, password, region)

response = ewelink.login()
print(response)
