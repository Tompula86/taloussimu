Ehdotettu eteneminen (roadmap, versio 0.x)
Tämä on nimenomaan “mitä tehdään missä järjestyksessä Pythonilla”.

Projektirakenne ja perustyökalut (päivä 1–2)

Luo perusrakenne (voit tehdä käsin tai apply_patch):
core/ – kello ja simulaation runko
agents/ – kotitalous, yritys, pankki, valtio, keskuspankki
markets/ – hyödykemarkkina (myöhemmin LOB), asuntomarkkina
policy/ – verotus, tulonsiirrot, rahapolitiikan reaktiosääntö
io/ – tulosten tallennus (aluksi CSV, myöhemmin Parquet)
scripts/ – ajoskriptit, kokeet
Lisää pyproject.toml tai requirements.txt vähintään: mesa, numpy, pandas, matplotlib.
Sovi tyylisäännöt: yksinkertainen ruff/black tai vain pep8-henkinen tyyli.
Yksinkertainen Mesa-pohjainen makrosimulaation runko (v0.1)
Tavoite: yksi kuukausisykli ilman pankkirahaa, asuntoja tai LOB:ia.

Toteuta core/model.py:
EconomyModel(Mesa Model) joka pyörittää kuukausiaskelta.
Agentit (hyvin yksinkertaiset versiot):
HouseholdAgent: tila: ikä, työssä/työtön, palkka, käteinen. Päätökset: kuluta vs. säästä.
FirmAgent: tila: kasa palkkoja, työntekijät, hyödykkeen hinta. Päätökset: palkkaa/irtisano, tuota ja myy.
StateAgent: kerää tuloveron ja ALV:n, maksaa työttömyystukea ja eläkkeitä.
Yksinkertainen kuukausisykli (versio “minimal”):
Palkat ja verot
Tulonsiirrot (tuet, eläkkeet)
Kulutus & hyödykemarkkina (ei vielä dynaamista hintaa)
Firmojen voitot ja yksinkertainen investointipäätös.
Tallennus: jokaisesta kuukaudesta DataCollector: Gini varallisuudelle, työttömyys, valtion alijäämä.
Elinkaari, perinnöt ja taseet (v0.2)
Tavoite: kotitalouksista tulee “oikeita” taseagentteja.

Laajenna HouseholdAgent:
Tase: käteinen, reaaliomaisuus (placeholder), yritysomistus (placeholder), velat.
Ikääntyminen, kuolema, perintö (perillisten valinta yksinkertaisella säännöllä).
Lisää syntymät/nuoret agentit, jotka tulevat työmarkkinoille tietystä iästä eteenpäin.
Päivitä Gini-laskenta nettovarallisuudelle.
Pankit, velka ja endogeeninen raha (v0.3)
Tavoite: toteuttaa pankkijärjestelmä, jossa velka luo talletuksia.

Uusi agentti: BankAgent (v0.3a)
- Tase: talletukset, lainat, kassavarat, oma pääoma + erillinen "default bucket".
- Parametrit: talletus- ja lainakorot, korkomarginaali, min. pääomasuhde, likviditeettipuskuri, hyväksymissäännöt (LTV/LTI + maksukykyyn perustuva maksimiannuiteetti), maks. luottokanta per agentti.
- Prosessi: `request_loan(agent, amount, purpose, maturity_months)` → hyväksyntä kirjataan sekä lainasaamiseksi (aktiva) että talletusvastuuksi (passiva).

Luottosykli ja kuukausittaiset eventit (v0.3b)
- Kotitaloudet ja firmat tekevät lainahakemuksen ennen kulutus-/palkkapäätöksiä.
- BankAgent muodostaa annuiteettiaikataulun (korko + lyhennys) ja veloittaa maksun kuukausittain ennen kotitalouksien kulutusta; firmoille ennen palkkoja.
- Jos agentti ei pysty maksamaan, velka siirtyy default-tilaan ja pankin oma pääoma pienenee (luottotappio = jäljellä oleva lainapääoma).
- Likviditeettisääntö: jos oma pääoma / talletukset < pääomavaade → pankki siirtyy "stop lending" -tilaan, mikä muuttaa makrosykliä.

Rahamäärä ja mittarit (v0.3c)
- Money supply M1 = talletukset (pankkitalletukset ovat kotitalouksien käteinen) → kerätään DataCollectorilla.
- Muita mittareita: lainakanta, nettonostot (flow), default-aste, pankin pääomasuhde, korkokate, keskim. laina- ja talletuskorot.
- Lisää myös kotitalouksien taseisiin kentät `loan_balance` ja `debt_service_due` raportointia varten.

Työlista v0.3
1. Päivitä konfiguraatioon `banking`-lohko (korot, marginaalit, pääomavaatimus, stop-lending raja, default recovery).
2. Toteuta `agents/bank.py` jossa: taseen päivitys, lainapäätöksen logiikka, kuukausittainen velanhoito, tappioiden käsittely.
3. Kytke `BankAgent` `EconomyModel`-luokkaan: instanssi, referenssi kotitalouksiin/firmoihin, API-lisäykset household/firm steppeihin (lainahaku ja velanhoito ennen kulutusta/palkkoja).
4. Laajenna datankeruuta ja mittareita (M1, lainakanta, default rate, bank equity) + tulosta per step debug-yhteenveto `run_minimal.py`:ssa.
5. Kirjoita regressiotesti: aja 120 kk ja varmista, että ilman defaultteja talletukset ≈ lainat sekä korkokate näkyy pankin tuloksessa.
Asuntomarkkina ja asuntolainat (v0.4)
Tavoite: tuoda asuminen ja velkavipu.

Luo markets/housing.py:
HousingMarket -luokka, joka omistaa listan Dwelling-olioita (ID, arvo, omistaja, myynnissä-lippu).
Laajenna HouseholdAgent:
“Tarve ostaa asunto” -sääntö (ikä, työssäolo, käsiraha).
Asunnon osto- ja myyntisäännöt.
Pankin asuntolaina-logiikka (LTV/LTI, stressitesti).
Markkinamekanismi: yksinkertainen kysyntä–tarjonta-hintapäivitys per kuukausi:
jos ostajien määrä > myytävien määrä → hinnat +Δ; muuten −Δ.
Mittarit: asuntojen hintaindeksi, asuntolainojen LTV-jakauma.
Yrittäjyys ja yrityksen perustaminen/konkurssi (v0.5)
Tavoite: sosiaalinen liikkuvuus ja pääoma-agentiksi nouseminen.

Laajenna FirmAgent → erillinen “entrepreneurial firm”:
Tilat: kassavarat, pääomakanta, työntekijät, velat.
Sääntö: kotitalous voi tietyllä todennäköisyydellä perustaa yrityksen, jos tase riittää.
Pankin yrityslainat (korkeampi korko, tiukempi kriteeri).
Konkurssi: negatiivinen kassavirta + ei rahoitusta → yritys poistuu, työntekijät työttömiksi, velka ja tappiot pankille.
Verotus, tulonsiirrot ja politiikkasäännöt “oikeasti” (v0.6)
Tavoite: tehdä valtio-osasta realistisempi.

Progressiiviset tuloverotaulukot, pääomaverot, ALV:n kiinnitys hyödykemarkkinaan.
Tulonsiirrot: eläkkeet, työttömyys, minimiturva.
Valtion budjetti ja velka:
jos alijäämä → valtio ottaa lainaa (vähintään kirjanpidollisesti) pankilta.
Mittarit: valtion velka/BKT-proxy, alijäämä, nettotulonsiirrot tulodesiileittäin.
Makrotilastot ja validointityökalut (v0.7)
Tavoite: kunnollinen mittaripaketti analyysia varten.

io/metrics.py:
Gini (tulot, varallisuus), työttömyysaste, palkkataso, asuntoindeksi, luottokanta, M1, valtion alijäämä.
scripts/run_scenario.py:
aja simulaatio N kuukautta, tallenna mittarit CSV/Parquet-muotoon ja tee pari peruskuvaa (Gini vs. aika, asuntoindeksi vs. aika).
LOB ja markkinamikrorakenne erillisenä moduulina (v0.8)
Tavoite: kytkeä mukaan pörssimarkkina, mutta vasta kun makrokerros on pystyssä.

markets/lob.py:
LOB-rakenne (hintatasot, määrä, FIFO).
Yksinkertainen “market maker + momentum trader” -kokoonpano.
Aikataajuus: aloita yhdellä “päivän sisäisellä” loopilla per kuukausi (esim. 100 micro-stepiä).
Mittarit: tuottojen jakauma, volatiliteetin klusteroituminen, spread.
Kalibrointi ja herkkyysanalyysi (v0.9)

calibration/-moduuli, jossa:
Parametrien perussetti (FI-tyylinen): säästöaste, verot, korkotasot → kovakoodattuna tai yksinkertaisessa YAML/JSON-konfigissa.
SMM-tyylinen looppi: aja simulaatio, laske momentit, vertaile referenssilukuihin, tee karkea haku.
Herkkyys: yksinkertaiset grid-sweep-skenaariot (korko ylös/alas, verot ylös/alas, asuntomarkkinashokki).
Käytännön ensimmäiset konkreettiset askeleet tänään

Ehdotan, että aloitetaan aivan käytännöstä:

Luo hakemistorakenne core/, agents/, markets/, policy/, io/, scripts/ taloussimu -kansioon.
Teen sinulle luonnoksen seuraavista tiedostoista (voit pyytää ne yksitellen tai pakettina):
core/model.py: yksinkertainen EconomyModel + kuukausiaskel (Mesa-runko).
agents/household.py, agents/firm.py, agents/state.py, agents/bank.py (tyhjät rungot, v0.1-v0.3 mielessä).
scripts/run_minimal.py: aja 120 kuukautta ja tulosta pari mittaria.
Sen jälkeen ajetaan ensimmäinen superyksinkertainen simulaatio (ei pankkia, ei asuntoja) ja katsotaan, että looppi toimii.
Jos haluat, voin seuraavaksi ehdottaa tarkkaa Python-moduulirakennetta (tiedostojen nimet + luokkien nimet ja tärkeimmät metodit) ja sitten alkaa täyttää niistä ensimmäisen version (EconomyModel + HouseholdAgent + FirmAgent + StateAgent + ajoskripti).