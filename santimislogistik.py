import itertools
import time
from geopy.geocoders import Nominatim
import requests

geolokaator = Nominatim(user_agent="santimislogistik") #Nominatin teenusele päringu tegemiseks


def koordinaatide_leidja(aadressid): #Muudab kasutaja poolt sisestatud aadressid koordinaatideks ning lisab need listi.

    koordinaadid = []
    for aadress in aadressid:
        asukoht = geolokaator.geocode(aadress)
        if asukoht:
            koordinaadid.append((aadress, asukoht.longitude, asukoht.latitude))
        else:
            print(f"Aadressi {aadress} ei leitud!")
        time.sleep(1.5) #Viivitus, et Nominatim ei blokeeriks IP-d (Nominatim limiteerib 1 päring sekundis)
    return koordinaadid


def asukohtade_vahemaad(koordinaadid): #OSRM kaarditeenuselt asukohtade vahemaa pärimine. Tagastab Vahemaa iga punkti vahel



def marsruudi_arvutaja(koordinaadid, vahemaad): #Leiab itertools mooduli permutatsioonide abil lühima marsruudi, katsetades kõik läbi. Tagastab õige aadresside järjestuse ning vahemaa.



def main(): #Programmi põhiosa (kasutaja sisestused, programmi vastused jms.
    #Esimene aadress, mis sisestatakse on alg ja lõpp punkt.
    kasutaja_aadressid = input() ### Kas võtta vastu kõik aadressid korraga, või küsida ükshaaval, või üldse tekstifailina