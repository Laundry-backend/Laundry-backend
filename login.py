from ewelink import EWeLink

# INSERISCI QUI LE TUE CREDENZIALI
EMAIL = "mattia.millebolle@gmail.com"
PASSWORD = "Millebolle.1"
REGION = "eu"   # Europa

# Crea client
ewelink = EWeLink(
    email=EMAIL,
    password=PASSWORD,
    region=REGION
)

# Login
response = ewelink.login()

print("LOGIN RESPONSE:")
print(response)
