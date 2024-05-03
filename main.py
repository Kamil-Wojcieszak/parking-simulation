import json
import random
import time
from math import floor, ceil


def czyNaprawiony(MTTR, czas, czas_uszkodzenia):
    if czas_uszkodzenia+MTTR<czas:
        return True
    else:
        return False


def main():
    # wczytanie danych wejsciowych
    f = open('config.json')
    konfiguracja = json.load(f)

    wjazdy = []
    kasy = []
    wyjazdy = []

    for i in range(konfiguracja['kasy']['liczba']):
        wjazdy.append(
            {"do_awarii": konfiguracja['wjazdy']['MTTF'] * 1.3, "czas_nastepnego_wjazdu": 0, "uszkodzony": False, "czas_uszkodzenia": None})
    for i in range(konfiguracja['kasy']['liczba']):
        kasy.append(
            {"do_awarii": konfiguracja['kasy']['MTTF'] * 1.3, "czas_nastepnego_kasowania": 0, "uszkodzony": False, "czas_uszkodzenia": None})
    for i in range(konfiguracja['kasy']['liczba']):
        wyjazdy.append(
            {"do_awarii": konfiguracja['wyjazdy']['MTTF'] * 1.3, "czas_nastepnego_wyjazdu": 0, "uszkodzony": False, "czas_uszkodzenia": None})

    samochody_przed_wjazdem = 0
    samochody_przed_kasa = 0
    samochody_przed_wyjazdem = 0

    samochody_wjechaly = 0
    samochody_zaplacily = 0
    samochody_wyjechaly = 0

    # wszystkie godziny ktore sa sprawdzane w glownej petli.
    # jesli czas jest w tej tablicy to samochod jest przenoszony do wyjazdu
    godziny_wyjazdow = []

    czas = 0
    dni = 0
    samochody_razem = 0

    print(f"\nDzien 1")

    first = True
    
    display = False
    display = True

    while True:
        # sleep dla testow
        time.sleep(0.0002)
        hours, minutes, seconds = convert_seconds(czas)
        fill = "|"
        n = (samochody_przed_kasa + samochody_przed_wyjazdem) * 20 // konfiguracja["parametry"]["liczba_miejsc"]
        fill += '#' * n

        fill += '-' * (20 - n)
        fill += '|'

        if display:
            print(
            f"\r### przed_wj: {'{:3d}'.format(samochody_przed_wjazdem)}, wj: {'{:4d}'.format(samochody_wjechaly)}, przed_k: {'{:3d}'.format(samochody_przed_kasa)}, k: {'{:4d}'.format(samochody_zaplacily)}, przed_wyj: {'{:2d}'.format(samochody_przed_wyjazdem)}, wyj: {'{:4d}'.format(samochody_wyjechaly)}, {'{:0>2}'.format(hours + 6)}:{'{:0>2}'.format(minutes)}:{'{:0>2}'.format(seconds)}, {fill}",
            end='')

        if first or (minutes == 0 and seconds == 0):
            print("")
            first = False


        # reset parkingu na nowy dzien
        if czas == 60 * 60 * 17:
            czas = -1
            first = True
            dni += 1
            print(f"\nOd startu obsluzono samochodow: {samochody_razem}")
            print(f"\nDzien {dni + 1}")
            samochody_przed_wjazdem = 0
            samochody_przed_kasa = 0
            samochody_przed_wyjazdem = 0
            samochody_wjechaly = 0
            samochody_zaplacily = 0
            samochody_wyjechaly = 0
            godziny_wyjazdow = []
            for wjazd in wjazdy:
                wjazd["czas_nastepnego_wjazdu"] = 0
            for kasa in kasy:
                kasa["czas_nastepnego_kasowania"] = 0
            for wyjazd in wyjazdy:
                wyjazd["czas_nastepnego_wyjazdu"] = 0

        # dodajemy losowo samochody do kolejki
        div = (18 - abs(konfiguracja["parametry"]["godzina_szczytu"] - hours - 6))
        if div==0:
            div =1

        wskaznik_szczytu = pow(9 / div,2)
        if hours + 6 < 22 and czas < 60 * 60 * 16 and random.randrange(0, int(round(
                konfiguracja["parametry"]["sredni_czas_miedzy_przyjazdami"] * wskaznik_szczytu))) == 1:
            samochody_przed_wjazdem += 1

        for idx, wjazd in enumerate(wjazdy):
            if hours + 6 >= 22:
                continue

            if wjazd["uszkodzony"]:
                if czyNaprawiony(wjazd['MTTR'], czas, wjazd['czas_uszkodzenia']):
                    wjazd["uszkodzony"] = False
                    wjazd["czas_uszkodzenia"] = None
                else:
                    continue
            if  samochody_przed_wjazdem > 0 and wjazd["czas_nastepnego_wjazdu"] <= czas and (
                    samochody_przed_kasa + samochody_przed_wyjazdem) < konfiguracja["parametry"]["liczba_miejsc"]:
                samochody_wjechaly += 1
                min_time = konfiguracja["wjazdy"]["sredni_czas_przejazdu"] * 0.5
                max_time = konfiguracja["wjazdy"]["sredni_czas_przejazdu"] * 1.5
                wjazd["czas_nastepnego_wjazdu"] = czas + random.randrange(floor(min_time), ceil(max_time))

                max_time = konfiguracja["parametry"]["sredni_czas_pobytu"]
                max_time += czas
                if max_time > 60 * 60 * 16:
                    max_time = 60 * 60 * 16

                if czas < max_time:
                    godziny_wyjazdow.append(random.randrange(czas, max_time, 1))
                else:
                    godziny_wyjazdow.append(czas)

                samochody_przed_wjazdem -= 1
                samochody_przed_kasa += 1

                wjazd["do_awarii"] -= 1

                if wjazd["do_awarii"] < konfiguracja['wjazdy']['MTTF'] / 3 and random.randrange(0, wjazd["do_awarii"]) == 1:
                    awaria(dni, czas, "wjazd " + str(idx + 1), wjazd, samochody_razem)

        godziny_wyjazdow.sort()

        for idx, kasa in enumerate(kasy):
            if kasa["uszkodzony"]:
                if czyNaprawiony(kasa['MTTR'],czas,kasa['czas_uszkodzenia']):
                    kasa["uszkodzony"] = False
                    kasa["czas_uszkodzenia"] = None
                else:
                    continue
            if samochody_przed_kasa > 0 and kasa["czas_nastepnego_kasowania"] <= czas:
                samochody_zaplacily += 1
                min_time = konfiguracja["kasy"]["sredni_czas_kasowania"] * 0.5
                max_time = konfiguracja["kasy"]["sredni_czas_kasowania"] * 1.5
                kasa["czas_nastepnego_kasowania"] = czas + random.randrange(floor(min_time), ceil(max_time))

                if len(godziny_wyjazdow)>0 and godziny_wyjazdow[0] <= czas:
                    godziny_wyjazdow.pop(0)
                    samochody_przed_kasa -= 1
                    samochody_przed_wyjazdem += 1
                    kasa["do_awarii"] -= 1

                if kasa["do_awarii"] < konfiguracja['kasy']['MTTF'] / 3 and random.randrange(kasa["do_awarii"]) == 0:
                    awaria(dni, czas, "kasa " + str(idx + 1), kasa, samochody_razem)

        for idx, wyjazd in enumerate(wyjazdy):
            if wyjazd["uszkodzony"]:
                if czyNaprawiony(wyjazd['MTTR'],czas,wyjazd['czas_uszkodzenia']):
                    wyjazd["uszkodzony"] = False
                    wyjazd["czas_uszkodzenia"] = None
                else:
                    continue
            if samochody_przed_wyjazdem > 0 and wyjazd["czas_nastepnego_wyjazdu"] <= czas:
                samochody_wyjechaly += 1
                min_time = konfiguracja["wyjazdy"]["sredni_czas_przejazdu"] * 0.5
                max_time = konfiguracja["wyjazdy"]["sredni_czas_przejazdu"] * 1.5
                wyjazd["czas_nastepnego_wyjazdu"] = czas + random.randrange(floor(min_time), ceil(max_time))

                samochody_przed_wyjazdem -= 1
                samochody_razem += 1

                wyjazd["do_awarii"] -= 1

                if wyjazd["do_awarii"] < konfiguracja['wyjazdy']['MTTF'] / 3 and random.randrange(wyjazd["do_awarii"]) == 0:
                    awaria(dni, czas, "wyjazd " + str(idx + 1), wyjazd, samochody_razem)

        czas += 1


def awaria(days, time, component_name, component, samochody_razem):
    print(f"\n\nAWARIA: {component_name}")
    hours, minutes, seconds = convert_seconds(time)
    print(f"Czas bez awarii: {days} dni {hours} h, {minutes} min, {seconds} s")
    print(f"Od startu obsluzono samochodow: {samochody_razem}")
    component["uszkodzony"] = True
    component["czas_uszkodzenia"]=time

    # exit(0)


def convert_seconds(seconds):
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return hours, minutes, seconds


if __name__ == "__main__":
    main()
