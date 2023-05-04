# Importer moduler
import asyncio
import pygame
import webbrowser
"""
Overføre systemet til pygbag for nettbruk
*****************************************************************************
Når nå programmet virker sånn noenlunde, ønsker jeg å vise det fram på nett,
og benytter pygbag for å konvertere det til en nettressurs.
Trodde først jeg kunne la pandas få være med på reisen, men det er nok
feil, pygbag støtter sannsynligvis bare python core og pygame, så da
ble import av xlsx fila umulig.

Jeg fant en metode for å lese dataene inn i ei liste, men da måtte jeg 
først lagre fila som utf csv. Så denne innlesningen eliminerer bruk av
pandas.
"""

# Initier pygame (starter opp pygame)
pygame.init()

# Bredde og høyde til skjermen
B = 1280
H = 720

# Lag en klokke
klokke = pygame.time.Clock()
FPS = 60
# Sett opp skjermen og lag tittelen
skjerm = pygame.display.set_mode((B, H))  # Setter opp skjermen
pygame.display.set_caption(f"Periodesystemet i pygame, {B}x{H}px, {FPS}fps")  # Viser tittelen

# Standardtekst for info-boksen over midten av periodesystemet, fra snl.no
info_tekst = """I periodesystemet er grunnstoffene ordnet etter økende atomnummer i en tabell. 
De syv horisontale radene i tabellen kalles perioder, og de 18 vertikale kolonnene 
kalles grupper. Grunnstoffene i samme kolonne (gruppe) ligner på hverandre, og 
innen hver periode endrer grunnstoffenes egenskaper seg gradvis fra metaller 
i gruppe 1 til gasser i gruppe 18.
                                
Periodesystemet gir på en enkel måte en systematisk oversikt over samtlige kjente 
grunnstoffer, samt verdifulle opplysninger om deres innbyrdes likhet og ulikhet. 
Periodesystemet er en bærebjelke i undervisning i kjemi."""

mendeleev_tekst = """I 1869 lagde Mendeleev et periodesystem bygd på de 63 grunnstoffene som da var kjent. Han forbedret 
systemet flere ganger i årene framover. Han forutså også eksistensen av flere ukjente grunnstoffer. Et 
eksempel er grunnstoffet gallium. Først da grunnstoffene som Mendelejev hadde forutsett egenskapene 
til, ble oppdaget, begynte kjemikerne å ta periodesystemet på alvor. Det periodesystemet som han 
utviklet i 1872, ble brukt i lærebøker i nesten 80 år.

Mendelejevs periodesystem var basert på økende atommasser. I dette systemet framkom perioder (vannrett) 
der for eksempel grunnstoff nr. 1 i en periode liknet grunnstoff nr. 1 i de andre periodene. Slik oppsto 
det grupper (loddrett) av grunnstoffer som liknet hverandre i viktige kjemiske og fysiske egenskaper."""

# Bilde som bakgrunn for å tegne elektronskall
# elektronskall_bakgrunn = pygame.image.load("electrons.png")
# pygame.transform.scale_by(elektronskall_bakgrunn, 0.5)
el_skall_rect = pygame.Rect(0, 0, 263, 136)
# print("El-skall:", el_skall_rect)
el_skall_rect.topleft = (846, 15)  # Plassering på skjermen

# Bilde av Dimitri Mendelejev
# mendelejev = pygame.image.load("mendelejev.png")
men_rect = pygame.Rect(0, 0, 70, 110)
# print("Mendel: ", men_rect)
men_rect.topleft = (87, 43)

# Vi benytter Al Sweigarts Periodesystem-app som utgangspunkt, og oversetter
# hans csv fil til norsk. Man kan prøve det med excel, men online-csv editoren
# på https://www.convertcsv.com/csv-viewer-editor.htm er bedre til våre formål

# Brukte denne til å laste opp Sweigarts fil og laste ned xlsx, som jeg så kunne
# redigere nokså komfortabelt i Excel 365

# Her er det bare delvis oversatt. Vi bruker pandas til å lese inn filen og behandle den
# Merk at på noen systemer er pandas avhengig av modulen openpyxl for å virke ordentlig
# Så denne må da være installert på systemet du bruker
csvdata = []
delim = ';'
with open('assets/periodesystem_delvis_oversatt2.csv', 'r', encoding="utf8") as file:
    line_nr = 0
    for line in file:
        csvdata.append(line.rstrip('\n').rstrip('\r').split(delim))

# Dette leser inn
# atom nummer, symbol, navn, gruppe, info, periode, atom masse, type, fasetilstand, elektron-oppbygning, elektronskall

# Foreløpig er den korte infoen ikke oversatt
# print(periodesystemet_lite)


# Men det er en del rusk i dataene. Først er gruppenummeret et desimaltall,
# og atom-massen er oppgitt med mye ekstra i tillegg til selve desimaltallet.
# Så vi måtte renske dataene før vi mate mate dem inn i spriten og sprite-gruppa

# Klasser

class GrunnstoffBlad(pygame.sprite.Sprite):
    # Reduser minnebruk
    __slots__ = ["nummer", "symbol", "navn", "info", "gruppe", "periode",
                 "masse", "sort", "fase", "elektron_konfig", "elektronskall", "info_ark"]

    # Klasse for å lage alle grunsntoff-bladene som skal vises
    def __init__(self, nummer, symbol, navn, info, gruppe, periode,
                 masse, sort, fase, elektron_konfig, elektronskall, info_ark):
        super().__init__()
        # Gjør om tekstlige tall til tall i am. tallformat
        number = ""
        for i in nummer:
            if i == ",":
                number += "."
            else:
                number += i

        mass = ""
        for i in masse:
            if i == ",":
                mass += "."
            else:
                mass += i

        gru = ""
        for i in gruppe:
            if i == ",":
                gru += "."
            else:
                gru += i

        per = ""
        for i in periode:
            if i == ",":
                per += "."
            else:
                per += i
        self.nummer = int(number)
        self.navn = navn
        self.info = info
        self.symbol = symbol
        self.fase = fase
        self.periode = int(per)
        self.gruppe = int(gru)
        self.masse = float(mass)
        self.type = sort
        self.elektron_konfig = elektron_konfig
        self.elektronskall = elektronskall
        self.info_ark = info_ark

        self.pos = ((B // 20 + 5) * self.gruppe - 48, 25 + (H // 18 + 25) * self.periode)  # Kun for testing
        # self.sirkel_pos = ((B // 20 + 5) * gruppe - 40, 53 + (H // 18 + 25) * periode)
        self.mouse_pos = (0, 0)
        self.hovered = False
        self.clicked = False
        self.wiki_start = "https://no.wikipedia.org/wiki/"  # Lenke til norsk wikipedia,
        # man bare legger til grunnstoff-navnet
        self.wiki_artikkel = self.wiki_start + self.navn

        # Opprett først en overflate som er bakgrunnen til hvert blad
        self.image = pygame.Surface((B // 20, H // 12))
        self.rect = self.image.get_rect()
        self.rect.topleft = self.pos  # Rektanglets plassering på skjermen
        self.sym_font = pygame.font.SysFont("Arial", 28, bold=True)

        # Tekst for elektron-konfigurasjon
        self.el_konfig_font = pygame.font.SysFont("Arial", 12, bold=True)
        self.el_konfig_flate = self.el_konfig_font.render(self.elektron_konfig, True, "red3")
        self.el_konfig_rect = self.el_konfig_flate.get_rect()
        self.el_konfig_rect.topleft = (950, 21)

        # Hente ut elektronskall-info, som er en tekst der tallene
        # er separert med mellomrom, vi kan få ut ei liste ved å splitte
        # Men ser ut som pandas tror dette er tall ...
        self.elektroner = str(self.elektronskall)
        self.elek_liste = self.elektroner.split(" ")
        self.elektron_font = pygame.font.SysFont("Arial", 18, bold=True)
        boble = 0
        boble_x = []
        boble_avstand = 27
        boble_plass = 926
        for bobler in range(7):
            boble_x.append(boble_plass)
            boble_plass += boble_avstand
        self.elek_dict = {}
        for elek in self.elek_liste:
            elektron_tall = self.elektron_font.render(elek, True, "black")
            elektron_rect = elektron_tall.get_rect()
            elektron_rect.top = 88
            elektron_rect.left = boble_x[boble] - elektron_rect.width // 2
            self.elek_dict[str(boble)] = [elektron_tall, elektron_rect]
            boble += 1

        # Lewis diagrammer
        if int(elek) < 9:
            self.lewis_name = "lewis" + elek + ".png"
        else:
            self.lewis_name = "lewis1.png"
        self.lewis = pygame.image.load("assets/" + self.lewis_name)
        self.lewis = pygame.transform.scale(self.lewis, (76, 76))
        self.lewis_rect = self.lewis.get_rect()
        self.lewis_rect.topleft = (1113, 75)
        # Symbol til lewis-diagram
        self.lewis_symbol = self.sym_font.render(self.symbol, True, "slategray")
        self.lewis_sym_rect = self.lewis_symbol.get_rect()
        self.lewis_sym_rect.topleft = (1153 - self.lewis_symbol.get_width() // 2, 130 - self.lewis_symbol.get_height())

        # Elektronskall-modell
        self.elektron_flate = self.elektron_font.render(self.elektroner, True, "black")
        pygame.transform.scale(self.elektron_flate, (25, 30))
        self.electron_rect = self.elektron_flate.get_rect()
        self.electron_rect.topleft = (922, 85)

        # Protoner og nøytroner
        protoner = self.nummer
        neutroner = round(float(self.masse) - float(self.nummer))  # Bare avrunding, kan ikke vise alle isotoper
        core_font = pygame.font.SysFont("Arial", 18, bold=True)
        self.pro_flate = core_font.render(str(protoner), True, "black")
        self.pro_rect = self.pro_flate.get_rect()
        self.pro_rect.left = 877 - self.pro_flate.get_width() // 2
        self.pro_rect.top = 75
        self.neu_flate = core_font.render(str(neutroner), True, "black")
        self.neu_rect = self.pro_flate.get_rect()
        self.neu_rect.left = 877 - self.neu_flate.get_width() // 2
        self.neu_rect.top = 105

    def update(self):
        if self.hovered:
            # Tegn rektangel rundt grunnstoff-blad
            pygame.draw.rect(skjerm, "#006400", self.rect, 2)
            info1.navn = self.navn

            # Elektron-konfigurasjon
            # skjerm.blit(self.el_konfig_flate, self.el_konfig_rect)
            # Elektroner i skallene
            for ele, vals in self.elek_dict.items():
                skjerm.blit(vals[0], vals[1])

            # Protoner og nøytoner
            skjerm.blit(self.pro_flate, self.pro_rect)
            skjerm.blit(self.neu_flate, self.neu_rect)

            # Lewis-diagram
            skjerm.blit(self.lewis, self.lewis_rect)
            skjerm.blit(self.lewis_symbol, self.lewis_sym_rect)

        if self.clicked:
            if self.navn == "Bor":
                self.wiki_artikkel = "https://no.wikipedia.org/wiki/Bor_(grunnstoff)"
            elif self.navn == "Tinn":
                self.wiki_artikkel = "https://no.wikipedia.org/wiki/Tinn_(grunnstoff)"
            elif self.navn == "Titan":
                self.wiki_artikkel = "https://no.wikipedia.org/wiki/Titan_(grunnstoff)"
            # Åpne wikipedia artikkel
            webbrowser.open(self.wiki_artikkel)
            print("You clicked on: " + self.navn)
            self.clicked = False


class InfoArk:  # Arver ikke
    # Viser et info-ark om grunnstoffet, midt over systemet
    def __init__(self, name, info):
        self.name = name
        self.info = info
        self.type = ""
        self.fase = ""
        # Opprett først en overflate som er bakgrunnen til hvert blad
        self.ark = pygame.Surface((B // 2 + 45, H // 4 + 10))
        self.ark.fill("ivory")
        self.ark_rect = self.ark.get_rect()
        self.ark_rect.topleft = (B // 20 * 3 - 33, 25 + (H // 18 + 25))  # Rektanglets plassering på skjermen
        # Bokser for tekst - først 'overskrifta' i en boks som er lilla
        self.rect_surface = pygame.Surface((B // 2 + 175, H // 20))
        self.rect_surface.fill("lavender")
        self.name_font = pygame.font.SysFont("Arial", 25, bold=True)
        self.name_surface = self.name_font.render(self.name, True, "midnightblue")
        self.name_rect = self.name_surface.get_rect()
        self.name_rect.left = 10
        self.rect_surface.blit(self.name_surface, self.name_rect)
        self.rect_surf_rect = self.rect_surface.get_rect()
        # Så info-teksten
        self.rect2_surface = pygame.Surface((B // 2 + 165, H // 4 + 10))
        self.rect2_surface.fill("whitesmoke")
        self.rect2_rect = self.rect2_surface.get_rect()
        self.info_font = pygame.font.SysFont("None", 16)
        self.info_surface = self.info_font.render(self.info, True, "black")
        self.info_rect = self.info_surface.get_rect()
        self.info_rect.left = 10
        self.info_rect.top = 40
        self.rect2_surface.blit(self.info_surface, self.info_rect)
        self.rect2_surf_rect = self.rect2_surface.get_rect()

        # Blit til arket
        self.ark.blit(self.rect_surface, self.rect_surf_rect)
        self.ark.blit(self.rect2_surface, self.rect2_surf_rect)

    def draw(self, navn, info):
        self.name = navn
        self.info = info
        # Finn mer info fra grunnstoff-gruppen
        nummer = 3
        if self.name == "Periodesystemet":
            nummer = 0
        elif self.name == "Dimitri":
            nummer = -1
        else:
            nummer = 2
        self.rect_surface.fill("lavender")
        self.name_font = pygame.font.SysFont("Arial", 25, bold=True)
        if nummer == 2:
            found = False
            for grunnstoff in grunnstoff_gruppen:
                if grunnstoff.navn == self.name:
                    self.name = grunnstoff.navn
                    nummer = grunnstoff.nummer
                    symbol = grunnstoff.symbol
                    self.type = grunnstoff.type
                    self.name_surface = self.name_font.render(self.name, True, "midnightblue")
                    found = True
                    break
                if found:
                    break

        if nummer == 0:
            self.name = "Periodesystemet"
            self.info = info_tekst
            self.name_surface = self.name_font.render(self.name, True, "midnightblue")

        if nummer == -1:
            self.name = navn + " Mendeleev, Russisk kjemiker (1834 - 1909)"
            self.info = info
            self.name_surface = self.name_font.render(self.name, True, "midnightblue")

        self.name_rect = self.name_surface.get_rect()
        self.name_rect.left = 10
        self.name_rect.top = 5
        self.rect_surface.blit(self.name_surface, self.name_rect)
        self.name_surf_rect = self.rect_surface.get_rect()
        # Info
        self.rect2_surface.fill("whitesmoke")
        info_liste = self.info.splitlines()
        if len(info_liste) == 1:
            self.info_surface = self.info_font.render(self.info, True, "midnightblue")
            self.info_rect = self.info_surface.get_rect()
            self.info_rect.left = 10
            self.info_rect.top = 43
            self.rect2_surface.blit(self.info_surface, self.info_rect)
        else:
            # Del i flere linjer
            linje_nr = 0
            for linje in info_liste:
                linje_tekst = self.info_font.render(linje, True, "midnightblue")
                linje_rect = linje_tekst.get_rect()
                linje_rect.left = 10
                linje_rect.top = 43 + linje_nr * (linje_tekst.get_height())
                self.rect2_surface.blit(linje_tekst, linje_rect)
                linje_nr += 1

        self.rect2_surf_rect = self.rect2_surface.get_rect()

        # Blit til arket

        self.ark.blit(self.rect2_surface, self.rect2_surf_rect)
        self.ark.blit(self.rect_surface, self.name_surf_rect)

        skjerm.blit(self.ark, self.ark_rect)
        # Rektangel rundt
        pygame.draw.rect(skjerm, "lightblue4", self.ark_rect, 1)


# Fonter


# Lyd og musikk

# Bilder


# Appens testverdier
hydrogen_info = """Hydrogen er det letteste grunnstoffet, og den vanligste isotopen består av kun ett proton og ett elektron. 
Under STP danner hydrogen en to-atomig gass, H2, med et kokepunkt på bare 20,27 K og et smeltepunkt på 
14,02 K. Under ekstremt høyt trykk, som finnes i sentrum av gasskjemper, går hydrogen over til å bli et flytende 
metall (se metallisk hydrogen). Under det ekstremt lave trykket man finner i verdensrommet, har hydrogen en 
tendens til å eksistere som enkeltatomer siden det rett og slett ikke er mulig for dem å gå sammen.

Dette grunnstoffet spiller en viktig rolle ved å tilføre universet energi gjennom proton-proton-reaksjon og 
karbon-nitrogen-syklusen. (Dette er kjernefusjon-prosesser som avgir enorme mengder energi ved å kombinere 
to hydrogenkjerner til én heliumkjerne.)"""
info1 = InfoArk("Hydrogen: H, gass (stp)", hydrogen_info)  # Et teste-info-ark

# Det er på tide å mate disse dataene inn i grunnstoffblad
grunnstoff_liste = csvdata[1:119]
grunnstoff_gruppen = pygame.sprite.Group()
# def __init__(self, nummer, symbol, navn, masse, periode, gruppe, info_ark):
# names=["Nummer", "Symbol", "Navn", "Info", "Gruppe", "Periode", "Masse"]
for grunnstoff in grunnstoff_liste:
    element = GrunnstoffBlad(grunnstoff[0], grunnstoff[1], grunnstoff[2], grunnstoff[3],
                             grunnstoff[4], grunnstoff[5], grunnstoff[6], grunnstoff[7],
                             grunnstoff[8], grunnstoff[9], grunnstoff[10], info1)
    grunnstoff_gruppen.add(element)

# Legg inn et bilde som bakgrunn, dette sparte rundt 100mB minne
bakgrunn = pygame.image.load("assets/system_bakgrunn.png")
bakgrunn_rect = bakgrunn.get_rect()
bakgrunn_rect.topleft = (8, 5)

async def main():
    # Spill/App løkke - kjører appen til vinduet lukkes, eller ESC trykkes
    kjorer = True  # Kjøre-variabel, brukes til å hoppe ut av løkka
    while kjorer:
        # Se hvilke hendelser som ligger i hendelses-løkka (tastatur, mus osv)
        for event in pygame.event.get():
            # Avslutt løkka hvis hviduet lukkes
            if event.type == pygame.QUIT:  # X-en på vinduet trykkes
                kjorer = False
            # Avslutt løkka hvis ESC trykkes på tastaturet
            elif event.type == pygame.KEYDOWN:  # KEYDOWN = sjekk hvilken tast som trykkes
                if event.key == pygame.K_ESCAPE:  # ESC er trykket
                    kjorer = False
            # Når musa er over et grunnstoffblad, skal riktig info-ark vises
            # sjekk for musa over grunnstoffbladet
            mouse_over = False
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = (event.pos[0], event.pos[1])

                if men_rect.collidepoint(mouse_pos):
                    info1.name = "Dimitri"
                    info1.info = mendeleev_tekst
                    hovered = True
                    mouse_over = True

                # Vis grunnstoff info når musa er over
                for element in grunnstoff_gruppen:
                    if element.rect.collidepoint(mouse_pos):
                        element.hovered = True
                        info1.name = element.navn
                        info1.info = element.info
                        mouse_over = True
                        break
                    else:
                        element.hovered = False

                if not mouse_over:
                    info1.name = "Periodesystemet"
                    info1.info = info_tekst

            if event.type == pygame.MOUSEBUTTONUP:
                for stoff in grunnstoff_gruppen:
                    if stoff.rect.collidepoint(mouse_pos):
                        stoff.clicked = True

        # Endre app-variable
        # Rensk skjermen, her med tistel-farge (lys lilla)
        skjerm.fill("#add8e6")
        # Blit bakgrunnen på skjermen
        skjerm.blit(bakgrunn, bakgrunn_rect)

        # Tegn og oppdater grunnstoffer og info
        # grunnstoff_gruppen.draw(skjerm)
        grunnstoff_gruppen.update()
        info1.draw(info1.name, info1.info)

        # Vis det som er tegnet på skjermen
        pygame.display.flip()
        # Sett klokka til FPS rammer per sekund
        # Det er den miste tida det vil ta for denne løkka
        # å kjøre, selv om maskinen din kan gjøre det raskere
        klokke.tick(FPS)
        await asyncio.sleep(0)  # Must always be there, and always 0

    # Avslutt pygame
    pygame.quit()


asyncio.run(main())