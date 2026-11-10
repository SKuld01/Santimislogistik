"""
Santimislogistik
Töö autorid: Sten Kuld, Meelika Kaarna

Programmi käivitamiseks on vaja järgnevaid teeke: geopy, requests, (itertools, time peaksid püütoniga kaasas olema)
Alfa versioonis piisab programmi käivitamisest ning shellis andmete sisestamisest. Vaja läheb internetiühendust.
Programmi töö võib natuke aega võtta päringute ning arvutuste tegemiseks.
"""


import itertools
import time
from geopy.geocoders import Nominatim
import requests


geolokaator = Nominatim(user_agent="santimislogistik") #Nominatin teenusele päringute tegemiseks


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


def asukohtade_vahemaad(koordinaadid): #OSRM kaarditeenuselt asukohtade vahemaa pärimine. Tagastab vahemaa iga punkti vahel
    koordinaadid_tekst = ""
    for i in koordinaadid:
        longitude = i[1]
        latitude = i[2]
        koordinaadid_tekst = koordinaadid_tekst + str(longitude) + "," + str(latitude) + ";"
    koordinaadid_tekst = koordinaadid_tekst[:-1]
    url = f"http://router.project-osrm.org/table/v1/driving/{koordinaadid_tekst}?sources=all&destinations=all&annotations=distance"

    osrm_vastus = requests.get(url)

    if osrm_vastus.status_code == 200: #Kontrollib, kas OSRM HTTP vastab korrektselt
        osrm_andmed = osrm_vastus.json()
        if "distances" in osrm_andmed:
            return osrm_andmed["distances"]
    raise Exception("OSRM lehelt ei saanud vastust.")


def marsruudi_arvutaja(koordinaadid, vahemaad): #Leiab itertools mooduli permutatsioonide abil lühima marsruudi, katsetades kõik läbi. Tagastab õige aadresside järjestuse ning vahemaa.
    if len(koordinaadid) < 2:
        return koordinaadid, 0

    leitavad_aadressid = [] #Jätab välja startpunkti arvutusteks
    for i in range(1, len(koordinaadid)):
        leitavad_aadressid.append(i)

    parim_marsruut = []
    vähim_vahemaa = float("inf") #Parim moodus, mis ma leidsin, et esialgne väärtus oleks võimalikult "suur"

    for permutatsioon in itertools.permutations(leitavad_aadressid): #Võtab läbi iga asukoha järjestuse varjandid
        marsruut = [0]
        for asukoha_indeks in permutatsioon: #Loob uue ajutise järjendi, võttes algus- ja lõpp-punktiks esimese sisestatud aadressi
            marsruut.append(asukoha_indeks)
        marsruut.append(0)

        hetke_vahemaa = 0
        for i in range(len(marsruut) - 1): #Kasutades OSRM-lt saadud vahemaade maatriksi leiab antud marsruudi vahemaad. range(len() - 1) teeb kindlaks, et lõpp-punktile ei hakata veel omakorda paarilist otsima, mis viskaks veateate.
            kust = marsruut[i]
            kuhu = marsruut[i + 1]
            hetke_vahemaa = hetke_vahemaa + vahemaad[kust][kuhu]

        if hetke_vahemaa < vähim_vahemaa:
            vähim_vahemaa = hetke_vahemaa
            parim_marsruut = marsruut

    parimad_koordinaadid = []
    for i in parim_marsruut:
        parimad_koordinaadid.append(koordinaadid[i])

    return parimad_koordinaadid, vähim_vahemaa


def main(): #Programmi põhiosa (kasutaja sisestused, programmi vastused jms.

    #Esimene aadress, mis sisestatakse on alg ja lõpp punkt.
    kasutaja_aadressid = ["Raekoja plats 1, Tartu",
        "Ülikooli 18, Tartu",
        "Vanemuise 46, Tartu",
        "Narva mnt 27, Tartu", "Ringtee 75, Tartu"]

    koordinaadid = koordinaatide_leidja(kasutaja_aadressid)
    vahemaad = asukohtade_vahemaad(koordinaadid)
    parimad_koordinaadid, vähim_vahemaa = marsruudi_arvutaja(koordinaadid, vahemaad)
    print(parimad_koordinaadid)
    print(vähim_vahemaa)

main()