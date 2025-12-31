from ewelink import EWeLink

# INSERISCI QUI LE TUE CREDENZIALI
EMAIL = "la_tua_email@email.com"
PASSWORD = "la_tua_password"
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
