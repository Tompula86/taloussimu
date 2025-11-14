# Taloussimulaattori – projektin suunnitelma

## 1. Visio ja päätavoite

Rakentaa agenttipohjainen, monitasoinen taloussimulaattori, joka tuottaa sekä mikro- että makrotason ilmiöitä modernista pankkikeskeisestä markkinataloudesta. Tavoitteena on malli, joka:

- kuvaa realistisesti kotitalouksien, yritysten, pankkien, valtion ja keskuspankin käyttäytymistä
- tuottaa tunnettuja “stylized facts” –ilmiöitä rahoitus- ja reaalitaloudessa
- mahdollistaa politiikkaskenaarioiden (verotus, rahapolitiikka, luottosäännöt) testaamisen
- on avoimesti dokumentoitu ja toistettavissa (konfiguroitava, siemenet, mittarit)

Lyhyesti: mahdollisimman uskottava agenttipohjainen talouslaboratorio, jossa voi kokeilla “mitä jos” –skenaarioita ja tutkia eriarvoisuutta, velkaantumista ja rahoitusmarkkinoiden dynamiikkaa.

---

## 2. Mitä simulaattori mallintaa

### 2.1 Talousympäristö

- Suljettu pieni avotalous (FI/EEA–tyyppinen instituutioympäristö)
- Yksi valuutta, pankkikeskeinen rahoitusjärjestelmä
- Keskuspankki asettaa ohjauskoron, liikepankit luovat luottoa endogeenisesti
- Markkinat: työmarkkina, hyödykemarkkinat, asuntomarkkina, rahoitusmarkkina (myöhemmin LOB)

### 2.2 Agentit

- **Kotitaloudet**: ikä, koulutus/taito, työllisyys, palkka, tase (käteinen, asunnot, yritysomistus, velat), kulutus/säästö, asuntolainat, riskinotto, perinnöt
- **Yritykset**: kassavirta, pääomakanta, työntekijät, velka, hinnoittelu, investoinnit, konkurssi
- **Pankit**: tase (talletukset, lainat, likviditeetti, oma pääoma), luotonanto, korkomarginaalit, riskisäännöt, endogeeninen rahanluonti
- **Valtio**: verotus (tulo, pääoma, kulutus), tulonsiirrot (tuet, eläkkeet), budjetti, velka
- **Keskuspankki**: ohjauskorko, yksinkertainen reaktiosääntö inflaatioon/työttömyyteen
- (Myöhemmin) **varainhoitajat, market makerit, CCP, repo-markkina, LOB-agentit**

### 2.3 Aikadynamiikka

- **Makro (kuukausi/kvartaali)**: työllisyys, palkat, verotus, tulonsiirrot, lainanhoito, kulutus, investoinnit, asuntomarkkina, valtion budjetti, rahapolitiikka
- **Meso (päivä/viikko)**: yritysten tuotanto/varastot, rahastojen rebalansointi, marginaalivaatimusten päivitys
- **Mikro (sekunti–minuutti)**: rahoitusmarkkinoiden limit order book –dynaamiikka (hinnat, spreadit, order flow) – lisätään myöhemmässä versiossa

---

## 3. Tutkittavat ilmiöt ja kysymykset

### 3.1 Varallisuuden ja tulojen jakautuminen

- Miten varallisuus jakautuu kotitalouksien välillä pitkällä aikavälillä?
- Miten elinkaari, perinnöt, asuntomarkkina ja yrittäjyys vaikuttavat eriarvoisuuteen?
- Miten velka (asuntolainat, kulutusluotot, yrityslainat) toimii vipuna ja riskinä?
- Tavoite: tuottaa realistinen Pareto-/lognormaali-häntä ja järkevät Gini-kertoimet.

### 3.2 Rahoitusjärjestelmä ja luottosykli

- Miten pankkien luotonanto, korkotaso ja marginaalit vaikuttavat talouden sykliin?
- Miten velkadeflaatio, pakkomyynnit ja konkurssit voivat syntyä endogeenisesti?
- Miten keskuspankin korkopolitiikka ja hätälikviditeetti vaikuttavat kriiseihin?

### 3.3 Asuntomarkkinat ja velkavipu

- Miten LTV/LTI-rajat, korkotaso ja tulokehitys vaikuttavat asuntojen hintoihin?
- Ketkä hyötyvät asuntomarkkinoiden arvonnoususta ja ketkä jäävät kyydistä?
- Minkälaista eriarvoisuutta syntyy, kun osa pääsee omistusasumiseen ja osa ei?

### 3.4 Työmarkkinat ja työllisyys

- Miten yritysten palkkaus/irtisanominen ja makrokysyntä luovat työttömyyttä?
- Miten työttömyyskorvaus ja minimietuudet vaikuttavat kulutukseen ja dynamiikkaan?

### 3.5 Politiikkakokeet

- Verotus: miten progressiivisuus, pääomaverotus ja ALV vaikuttavat eriarvoisuuteen ja kasvuun?
- Rahapolitiikka: miten korkotason muutos vaikuttaa velanhallintaan, asuntohintoihin ja investointeihin?
- Luottosäännöt: miten LTV/LTI-rajojen kiristäminen tai löysentäminen vaikuttaa velkavipuun ja kriisiherkkyyteen?

---

## 4. Tavoitellut "stylized facts" ja validointikriteerit

Simulaatio ei ole pelkkä lelu, vaan sen tulisi toistaa tiettyjä tunnettuja ilmiöitä:

- Pörssituottojen paksuhäntäisyys ja volatiliteetin klusteroituminen (LOB-vaiheessa)
- Volyymin ja volatiliteetin positiivinen korrelaatio
- Luottosyklin prosyklisyys: hyvien aikojen luotonlaajeneminen, kriiseissä kiristyminen
- Varallisuuden vahvasti vinoutunut jakauma (raskas häntä)
- Asuntojen “boom–bust” –syklit, joissa velkavipu voimistaa liikkeitä
- Työttömyyden hidas keskiarvoon palautuminen ja suhdanneherkkyys

Validointi tehdään vertaamalla mallin tuottamia jakaumia ja momentteja (esim. Gini, volatiliteetti, kurtosis, default-asteet) oikean maailman tilastoihin (esim. Tilastokeskus, keskuspankki, pörssidata).

---

## 5. Tekniset tavoitteet

- **Kieli ja kirjastot**: Python, Mesa agenttipohjaiseen mallinnukseen. NumPy/Pandas laskentaan ja datan käsittelyyn, Matplotlib/Seaborn visualisointiin.
- **Arkkitehtuuri**:
  - `core/` – simulaation kello ja scheduler
  - `agents/` – eri agenttiluokat (kotitalous, yritys, pankki, valtio, keskuspankki, myöhemmin rahastot/market makerit)
  - `markets/` – hyödykemarkkinat, asuntomarkkinat, myöhemmin LOB
  - `policy/` – verotus-, tuki- ja rahapolitiikkasäännöt
  - `io/` – datan tallennus ja mittarit
  - `scripts/` – ajoskriptit ja kokeet
- **Suorituskyky**: perusversio Python+Mesa, tarvittaessa kriittiset osat Numba/Cython/Rust-moduuleiksi.
- **Toistettavuus**: konfiguraatiotiedostot (esim. YAML/JSON), satunnaissiemenet, vakioitu mittarilista.
- **Testattavuus**: yksikkötestit keskeisille osille (esim. verotus, velanhoito, asuntokauppa, LOB-matcher), integraatiotestit tärkeille ketjuille (luotto → pakkomyynti → hinta).

---

## 6. Projektin päävaiheet (versiot 0.1–0.9)

Yksityiskohtainen roadmap on `roadmap.md`-tiedostossa; tässä tiivistetty näkymä:

- **v0.1** – Yksinkertainen Mesa-pohjainen makromalli (kotitaloudet, yritykset, valtio; palkat, verot, tulonsiirrot, kulutus, perusmittarit).
- **v0.2** – Elinkaari, taseet ja perinnöt kotitalouksille.
- **v0.3** – Pankit, velka ja endogeeninen raha (lainat, talletukset, M1-dynamiikka).
- **v0.4** – Asuntomarkkina ja asuntolainat (LTV/LTI, hintadynamiikka).
- **v0.5** – Yrittäjyys, yrityslainat ja konkurssiprosessi.
- **v0.6** – Realistisempi verotus, tulonsiirrot ja valtion budjetti/velka.
- **v0.7** – Makrotilastot, mittaripaketti ja validointityökalut.
- **v0.8** – Rahoitusmarkkinoiden LOB-mikrorakenne ja stylized facts –testit.
- **v0.9** – Kalibrointi, herkkyysanalyysi ja perus-dashboard.

Tavoite näille vaiheille on toimiva, analysoitava versio 0.9, joka kattaa sekä reaalitalouden että rahoitusmarkkinat riittävällä tarkkuudella tutkimus- ja kokeilukäyttöön.

---

## 7. Mihin projektilla pyritään käytännössä

- Rakentaa avoin “talouslaboratorio”, jossa voi:
  - testata eri politiikkasääntöjä ja sääntelyä
  - tutkia eriarvoisuuden ja velkaantumisen dynamiikkaa
  - simuloida kriisiskenaarioita (korkoshokki, asuntokuplan puhkeaminen, pankkikriisi)
- Tarjota alusta jatkokehitykselle:
  - lisäagentit (rahastot, HFT, CCP)
  - uudet markkinat ja instrumentit
  - eri maiden parametrisaatiot (FI, EU, US…) konfiguraatioiden kautta
- Pitkällä aikavälillä: riittävän uskottava malli, jota voi käyttää sekä opetuksessa että tutkimus-/konsultointityyppisissä skenaarioanalyyseissa.

---

## 8. Seuraavat konkreettiset stepit

1. Viimeistellään hakemistorakenne (`core/`, `agents/`, `markets/`, `policy/`, `io/`, `scripts/`).
2. Lisätään riippuvuustiedosto (`pyproject.toml` tai `requirements.txt`) ja asennetaan vähintään: `mesa`, `numpy`, `pandas`, `matplotlib`.
3. Toteutetaan v0.1: `EconomyModel` + `HouseholdAgent`, `FirmAgent`, `StateAgent` ja yksinkertainen kuukausisykli.
4. Ajetaan ensimmäinen 100–200 kuukauden simulaatio ja kerätään perusmittarit (Gini, työttömyys, budjettitasapaino) todistamaan, että runko toimii.

Tämän suunnitelman tarkoitus on antaa kirkas kokonaiskuva: mitä rakennetaan, miksi, ja miten vaiheistus etenee siitä kohti “maailman parasta agenttipohjaista taloussimulaatiota”.

---

## 9. v0.3 pankkijärjestelmän tarkennus

### 9.1 Arkkitehtuuri

- `BankAgent` hallitsee koko luottopoolia: tasekentät (cash, deposits, performing_loans, defaulted_loans, equity).
- Kotitalouksilla ja yrityksillä on viittaus pankkiin; lainat kirjataan agentin `loan_book`-rakenteeseen (lista yksittäisiä lainoja tai aggregoitu saldo + jaksotusaikataulu).
- Ekonomimalli ajaa pankkia omana stepinään heti valtion jälkeen, jotta lainanhoito ehtii vaikuttaa kotitalouksien kulutuskykyyn.

### 9.2 Prosessit kuukausitasolla

1. **Velanhoito**: Pankki laskee korko- ja lyhennysvaateen jokaiselle avoimelle lainalle (annuiteetti tai interest-only + balloon). Summa veloitetaan agentilta ennen tämän muita päätöksiä.
2. **Default-handling**: jos agentin kassavarat eivät riitä velanhoitoon, kirjataan maksamatta jäänyt osa default-bucketiin ja pienennetään pankin omaa pääomaa. Agentin velka nollaantuu tai siirtyy "collections"-tilaan.
3. **Lainahaut**: kotitaloudet hakevat kulutus-/siltalainaa (konfiguroitava enimmäisosuus palkasta) ja firmat käyttöpääomalainaa ennen palkkoja. Pankki arvioi hakemukset käyttämällä LTV/LTI-rajoja sekä kassavirtaestimaattia.
4. **Talletuskorko**: pankki maksaa talletuskorkoa kotitalouksien kassalle (osuuden voi ohjata vain positiiviseen saldoon) ja kirjaa kulun omaan tuloslaskelmaansa.

### 9.3 Säännöt ja parametrit

- Konfiguraatiossa `banking`-blokki: `deposit_rate`, `loan_rate_base`, `risk_spread_household`, `risk_spread_firm`, `capital_ratio_min`, `liquidity_buffer_months`, `max_loan_to_income`, `max_loan_to_deposit_multiple`, `default_recovery_rate`.
- Lainapäätösmalli: hyväksytään, jos (a) uusi velka ≤ `max_loan_to_income * annual_income` ja (b) pankin kokonaispääomasuhde pysyy rajan yläpuolella. Muussa tapauksessa hakemus hylätään.
- Likviditeettikuri: jos käteisvarat < `liquidity_buffer_months * talletusulosvirta`, pankki lopettaa uusien lainojen myöntämisen, mutta palvelee olemassa olevat.

### 9.4 Mittarit ja diagnostiikka

- `M1 = Σ kotitalouksien cash` (sis. talletukset) → raportoidaan kuukausittain.
- `total_loans`, `performing_share`, `default_rate_12m`, `bank_equity_ratio`, `net_interest_margin`.
- Debug-lokit: pankki tulostaa kuukausittain (vaihtoehtoisesti tallennetaan DataCollectorin kautta) korkokatteensa ja luottotappionsa, jotta regressiotestit voidaan kirjoittaa.

### 9.5 Toteutusjärjestys

1. Lisää uusi `BankAgent`-luokka ja yksinkertainen luottokirja.
2. Päivitä kotitaloudet/yritykset tukemaan `loan_balance`, `monthly_debt_service`, `request_loan` APIa.
3. Kytke pankin step EconomyModelin sykliin: `state -> bank -> firms -> households`.
4. Laajenna DataCollector ja mittarit.
5. Kirjoita savutesti-skenaario (esim. 24 kk) joka varmistaa, että talletusten määrä kasvaa lainojen mukana ja defaultit näkyvät pääomassa.
