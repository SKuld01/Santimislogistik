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


def google_maps_link(parimad_koordinaadid): #Võtab parima marsruudi koordinaadid ning annab google maps marsruudi
    koordinaadid = []
    for i in parimad_koordinaadid:
        longitude = i[1]
        latitude = i[2]
        koordinaadid.append(f"{latitude},{longitude}")

    teekond = "/".join(koordinaadid)
    return f"https://www.google.com/maps/dir/{teekond}"


def main(): #Programmi põhiosa (kasutaja sisestused, programmi vastused jms).
    
    kodu_aadress = input("Sisesta aadress, kust santimist alustad ja lõpetad kujul tänav, majanumber, linn (nt Riia 2, Tartu): ")
    kodu = geolokaator.geocode(kodu_aadress)
    if not kodu:
        print("Sisestatud aadressi ei leitud.")
        return
        
        
    aadressid = []
    
    
    print("Maksimaalne aadresside arv on 8!")
    while True:
        aadress_sisend = input("Sisesta aadress kujul tänav, majanumber, linn (nt Riia 1, Tartu), lõpetamiseks kirjuta 'lõpp': ")

        if aadress_sisend.lower() == "lõpp": #lower teeb kasutaja sisestatud sõna väiketähtedega sõnaks
            print("Leian marsruudi...")
            break
        
        aadressid.append(aadress_sisend)

        if len(aadressid) == 8:
            print("Leian marsruudi...")
            break
    
    if len(aadressid) == 0:
        print("Ühtegi külastatavat aadressi ei sisestatud.")
        return

    aadressid.insert(0, kodu_aadress) #lisab koduaadressi listi algusesse
    

    koordinaadid = koordinaatide_leidja(aadressid)
    vahemaad = asukohtade_vahemaad(koordinaadid)

    parimad_koordinaadid, vähim_vahemaa = marsruudi_arvutaja(koordinaadid,vahemaad)

    print("\nParim marsruut ligikaudsete vahemaadega:")
    print("-" * 40) #kriipsude rida vahele

    for i in range(len(parimad_koordinaadid)):

        print(f"{i + 1}. {parimad_koordinaadid[i][0]}") #prindib aadressi


        if i < len(parimad_koordinaadid) - 1: #kontrollib, kas tegu on viimase punktiga

            indeks1 = koordinaadid.index(parimad_koordinaadid[i])
            indeks2 = koordinaadid.index(parimad_koordinaadid[i + 1])

            vahemaa = round(vahemaad[indeks1][indeks2])

            if vahemaa > 1000:
                vahemaa /= 1000
                vahemaa = round(vahemaa, 1)
                print(f"   ↓ {vahemaa} km")
            else:
                vahemaa = int(round(vahemaa / 50) * 50)
                print(f"   ↓ {vahemaa} m") #prindib järgmise punktini mineku vahemaa

    print("-" * 40)
    if vähim_vahemaa > 1000:
        vähim_vahemaa /= 1000
        print(f"Kogu marsruudi pikkus: {round(vähim_vahemaa)} km")
    else:
        print(f"Kogu marsruudi pikkus: {round(vähim_vahemaa)} m")

    print(f"Marsruut Google Mapsis: {google_maps_link(parimad_koordinaadid)}")
    
if __name__ == "__main__":
    main()
    
    
