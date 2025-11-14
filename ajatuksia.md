Paras ympäristö: Python
Paras ympäristö tämänkaltaiseen simulaatioon on ehdottomasti Python.

Miksi Python?
Helppokäyttöisyys ja nopea prototyypitys: Pythonilla on matala kynnys, ja voit luoda toimivan simulaation nopeasti.

Agenttipohjaisen mallinnuksen kirjastot: Pythonissa on erinomainen kirjasto nimeltä Mesa , joka on suunniteltu juuri agenttipohjaisten mallien rakentamiseen, analysointiin ja visualisointiin. Se tarjoaa valmiit työkalut agenttien, ruudukon (jos tarvitaan fyysistä ympäristöä) ja aikataulutuksen hallintaan.

Tieteen ja datan analysoinnin ekosysteemi: Tarvitset työkaluja simulaation tulosten analysointiin. Pythonin NumPy (laskenta), Pandas (datan käsittely) ja Matplotlib/Seaborn (visualisointi) ovat alan standardeja.

Visualisointi: Voit helposti luoda kaavioita, jotka näyttävät varallisuusjakautuman kehityksen (esim. Lorenzin käyrät tai Gini-kertoimen muutokset) ajan mittaan.

Tämä on erinomainen perusta! Esittämäsi suunnitelma on klassinen ja vahva lähtökohta agenttipohjaiselle talousmallille. Se kuvaa talouden perusmoottoria: työn ja pääoman välistä vuorovaikutusta.Jotta simulaattorista saadaan "mahdollisimman luotettava" ja asiaa voidaan tarkastella monipuolisemmin, meidän on lisättävä realismin kerroksia tämän perusrakenteen päälle. Tässä on yksityiskohtainen parannusehdotus, joka laajentaa alkuperäistä suunnitelmaasi.1. Agenttien syventäminen ja monipuolistaminenAlkuperäinen suunnitelmasi jakaa agentit kahteen luokkaan. Todellisuudessa rajat ovat häilyvämpiä ja agenttien sisällä on suurta vaihtelua (heterogeenisyyttä).Elinkaari ja demografia: Agenttien tulisi syntyä, vanheta, tehdä työtä, jäädä eläkkeelle ja kuolla.Vaikutus: Tämä pakottaa mallintamaan säästämistä eläkepäiviä varten (elinkaarihypoteesi) ja tuo malliin perinnöt. Varallisuuden siirtyminen sukupolvelta toiselle on yksi merkittävimmistä varallisuuden kasautumisen mekanismeista.Taito ja koulutus: "Työntekijä-agentit" eivät ole yhtenäinen ryhmä. Lisää heille koulutustaso tai taito-ominaisuus.Vaikutus: Tämä vaikuttaa suoraan heidän palkkaansa, työllistymisen todennäköisyyteen ja kykyyn säästää. Voit mallintaa palkkaeroja matala- ja korkeakoulutettujen välillä.Agenttien roolien muutos (sosiaalinen liikkuvuus):Vaikutus: Anna "Työntekijä-agentille" mahdollisuus sosiaaliseen nousuun. Jos hän säästää tarpeeksi, hän voi perustaa oman yrityksen ja siirtyä "Pääoma-agentiksi" (esim. pienyrittäjäksi). Vastaavasti "Pääoma-agentti" voi epäonnistua (konkurssi) ja palata "Työntekijäksi". Tämä tekee mallista dynaamisemman.2. Uusien kriittisten toimijoiden lisääminenTaloudessa on muitakin toimijoita kuin vain työntekijät ja yritysten omistajat. Kaksi tärkeintä puuttuvaa palaa ovat valtio ja rahoitusjärjestelmä.Valtio (Julkinen sektori)Tämä on ehdottoman välttämätöntä modernin talouden mallintamisessa. Valtio on suurin yksittäinen tulonsiirtäjä.Verotus (Rahan kerääminen):Tulovero: Valtio kerää työntekijöiltä progressiivisen tuloveron (mitä enemmän tienaat, sitä suurempi %-osuus).Pääomavero: Valtio kerää Pääoma-agenteilta veroa pääomatuloista (voitot, osingot).Kulutusvero (ALV): Aina kun agentti kuluttaa, osa rahasta menee valtiolle.Tulonsiirrot (Rahan jakaminen):Sosiaalituet: Työttömyyskorvaukset (jos agentti ei löydä työtä), lapsilisät, toimeentulotuki.Eläkkeet: Kun agentti siirtyy eläkkeelle, valtio (tai eläkerahasto) maksaa hänelle eläkettä.Vaikutus: Verotus hidastaa varallisuuden kasautumista huipulla, ja tulonsiirrot nostavat alimpien tuloluokkien elintasoa. Tämä on keskeinen mekanismi eriarvoisuuden tasaamisessa.Rahoitusjärjestelmä (Pankit)Agentit eivät säilytä rahaa "sukanvarressa". He käyttävät pankkeja, jotka luovat uusia mekanismeja.Säästötilit ja korot: Kun agentit säästävät, he tallettavat rahan pankkiin ja saavat sille korkoa. Tämä on passiivinen tapa kasvattaa varallisuutta.Lainat ja velka:Työntekijät: Voivat ottaa asuntolainaa ostaakseen asunnon (joka on myös varallisuuden muoto) tai kulutusluottoa. Laina pitää maksaa takaisin korojen kera.Pääoma-agentit: Voivat ottaa yrityslainaa investoidakseen ja kasvattaakseen tuotantokapasiteettiaan nopeammin kuin omat säästöt sallisivat.Vaikutus: Velka voi olla "vipu" (leverage) varallisuuden nopeaan kasvattamiseen, mutta se lisää myös riskiä (konkurssiriski, henkilökohtainen velkaantuminen). Velkaantuminen on valtava tekijä kotitalouksien varallisuudessa (usein negatiivinen).3. Mekanismien ja markkinoiden hienosäätöAlkuperäisessä mallissa raha "vain liikkuu". Luotettavampi malli tarvitsee todelliset markkinat, joissa hinnat määräytyvät kysynnän ja tarjonnan mukaan.Dynaamiset työmarkkinat:Sen sijaan, että työ vain "tapahtuu", luo työmarkkinat.Pääoma-agentit (yritykset) luovat työpaikkoja tuotantotarpeensa mukaan.Työntekijä-agentit hakevat töitä.Vaikutus: Tämä luo malliin orgaanisesti työttömyyden. Jos työpaikkoja on vähemmän kuin työntekijöitä, palkat voivat laskea (tai pysyä matalina). Jos on työvoimapula, palkat nousevat.Dynaamiset hyödykemarkkinat:Yritykset tuottavat hyödykkeitä (esim. "ruokaa" tai "kulutustavaroita").Agentit (työntekijät JA pääoma-agentit) ostavat näitä hyödykkeitä kuluttaakseen.Vaikutus: Voit mallintaa kysynnän ja tarjonnan. Jos yritykset tuottavat liikaa, hinnat laskevat. Jos kysyntä ylittää tarjonnan, syntyy inflaatiota (hintojen nousua), mikä syö säästöjen arvoa.Älykkäämpi investointipäätös:Sen sijaan, että Pääoma-agentti säästää/investoi kiinteän osan, tee siitä dynaaminen päätös. Agentti investoi vain, jos hän odottaa saavansa voittoa. Odotuksiin vaikuttaa esim. korkotaso (lainarahan hinta) ja kulutuskysynnän tila.4. Luotettavuuden varmistaminen (Validointi ja kalibrointi)Tämä on kriittisin askel "luotettavan" simulaattorin tekemisessä. Miten tiedät, ettei mallisi ole vain fantasiaa?Kalibrointi (Calibration): Älä keksi parametrejä (kuten säästöaste tai palkkataso) tyhjästä. Käytä oikean maailman dataa niiden asettamiseen. Esimerkiksi Tilastokeskuksen dataa tulo- ja varallisuusjakaumista, veroprosenteista ja säästämisasteista Suomessa.Validointi (Validation): Kun simulaatio on kalibroitu, aja sitä ja katso, tuottaako se tunnettuja talouden ilmiöitä ("stylized facts"), joita et suoraan syöttänyt malliin.Tuottaako malli realistisen varallisuusjakauman? Varallisuus on todellisuudessa paljon epätasaisemmin jakautunut kuin tulot (esim. Pareton jakauma tai log-normaali jakauma).Mittaa Gini-kerrointa: Pystytkö laskemaan mallisi tuottaman varallisuuden Gini-kertoimen? Vastaako se todellisuutta?Testaa politiikkamuutoksia: Mitä tapahtuu Gini-kertoimelle, jos nostat pääomaverotusta tai korotat sosiaalitukia? Toimiiko malli odotetulla tavalla?Herkkyysanalyysi (Sensitivity Analysis): Testaa, kuinka herkkä mallisi on pienille muutoksille lähtöparametreissa. Jos pieni koronmuutos romahduttaa koko talouden, mallisi on luultavasti epävakaa.Yhteenveto parannuksista:Alkuperäinen suunnitelmaParanneltu malli (lisäykset)Agentit: Työntekijä, PääomaAgentit: Työntekijä (eri taitotasot), Pääoma (eri kokoiset), Valtio, PankitKäyttäytyminen: Työ, Kulutus, SäästöKäyttäytyminen: Elinkaari (syntymä, eläke, kuolema), Perintö, Kouluttautuminen, LainanottoMekanismit: Rahan siirtoMekanismit: Dynaamiset työmarkkinat (työttömyys), Hyödykemarkkinat (inflaatio)Tavoite: $r > g$Tavoite: $r > g$ + Verotuksen ja tulonsiirtojen vaikutus, Velkaantumisen rooli, Sosiaalinen liikkuvuusLuotettavuus: -Luotettavuus: Kalibrointi (data), Validointi (Gini-kerroin, jakaumat)Tämä laajennettu malli antaa paljon tarkemman ja luotettavamman kuvan varallisuuden muodostumisesta, koska se ottaa huomioon ne instituutiot (valtio, pankit) ja mekanismit (verotus, perintö, velka), jotka todellisuudessa ohjaavat sitä.Mistä näistä parannuksista haluaisit keskustella tarkemmin? Voisimme esimerkiksi syventyä siihen, miten valtio ja verotus kannattaisi käytännössä mallintaa, tai miten pankkijärjestelmä ja velka vaikuttavat varallisuuden kasautumiseen.

Tämä on aivan keskeinen havainto. Mallista tulee luotettava vasta, kun ymmärrämme, että modernissa taloudessa pankit luovat suurimman osan rahasta tyhjästä myöntäessään lainoja (tätä kutsutaan "endogeeniseksi rahaksi").Raha ei ole vain staattinen kasa kultaa, jota kierrätetään, vaan se on velkasuhde. Kun otat asuntolainan, pankki ei siirrä sinulle muiden talletuksia, vaan se kirjaa tilillesi 100 000 euroa (luoden uuden talletuksen) ja itselleen 100 000 euron saamisen (lainan). Rahaa syntyi. Kun maksat lainaa takaisin, rahaa tuhoutuu.Tässä on suunnitelma, joka toteuttaa tämän "nyky-yhteiskunnan" mallin.1. 🏛️ Valtio (Julkinen sektori)Pidetään valtio "yksinkertaisena" agenttina, jolla on budjetti. Se ei yritä maksimoida voittoa, vaan se noudattaa sääntöjä (lakia).Ominaisuudet:Kassavarat (sen "tili" pankissa)Budjettialijäämä / -ylijäämä (seuraa tuloja vs. menoja)Toiminnot (joka simulaation kierroksella):A. Rahan keräys (Tulot):Valtio kerää veroja automaattisesti, kun tietyt tapahtumat tapahtuvat:Kulutusvero (ALV): Kun agentti X ostaa hyödykkeen agentilta Y (esim. Työntekijä ostaa kulutustavaran Pääoma-agentin yritykseltä), 24 % (tai jokin mallin parametri) maksusta siirtyy suoraan valtion Kassavaroihin. Tämä on tehokas tapa mallintaa jatkuva verokertymä.Tulovero: Kun Pääoma-agentti maksaa palkkaa Työntekijä-agentille, x % palkasta siirtyy suoraan valtiolle. Tämän voi tehdä progressiiviseksi: agentin Vuositulot-muuttujan perusteella määritellään veroprosentti (if tulo < 20k, vero = 10%, if tulo > 20k, vero = 25%, jne.).Pääomavero: Kun Pääoma-agentti saa "voittoa" (esim. kierroksen lopussa laskettu tuotto pääomalle), x % voitosta siirtyy valtiolle.B. Rahan jakelu (Menot):Valtio siirtää rahaa takaisin agenteille:Tulonsiirrot (Passiiviset):Eläkkeet: Jos agentin Ikä > 65, valtio maksaa sille peruseläkkeen X euroa/kierros.Työttömyyskorvaus: Jos agentin Tila = Työtön, valtio maksaa sille peruskorvauksen Y euroa/kierros.Julkinen kulutus (Aktiiviset): Tämä on se mainitsemasi "hävittäminen". Se ei häviä, vaan valtio ostaa asioita. Yksinkertaisin tapa: Valtio ostaa joka kierros tietyn määrän hyödykkeitä yrityksiltä (Pääoma-agenteilta). Tämä simuloi teiden, koulujen, sairaaloiden jne. ylläpitoa ja edustaa rahan palautumista kiertoon yritysten kautta.C. Budjetti ja Velka:Kierroksen lopussa valtio laskee: Tulos = Tulot - Menot.Jos Tulos < 0 (alijäämä), valtion Kassavarat vähenevät. Jos kassavarat menevät negatiiviseksi, valtio automaattisesti ottaa lainaa kattamaan vajeen.Tämä luo valtionvelan.2. 🏦 Pankkijärjestelmä (Rahanluoja ja Keskittäjä)Tarvitsemme kaksi uutta agenttityyppiä: Keskuspankki (asettaa säännöt) ja Liikepankki (tekee työn).A. Keskuspankki (EKP, "Politiikka-agentti")Tämä on "God mode" -agentti. Se ei ole vuorovaikutuksessa muiden kanssa suoraan, vaan se asettaa yhden globaalin muuttujan:Ohjauskorko: Tämä on rahan hinta. Se on mallin tärkein säädin.B. Liikepankki ("Pankki-agentti")Tämä on dynaaminen agentti, joka pyrkii tekemään voittoa. Kaikki muiden agenttien Raha on todellisuudessa talletus tämän Pankki-agentin taseessa.Toiminnot:Korkojen asettaminen: Pankki asettaa omat korkonsa Ohjauskoron perusteella:Talletuskorko = Ohjauskorko - 0.5% (Miksi pitäisit rahaa, jos et saa korkoa?)Lainakorko = Ohjauskorko + 2.0% (Pankin riskimarginaali ja voitonlähde)Pankin voitto tulee korkokatteesta (Lainakorko - Talletuskorko).Talletusten hallinta: Joka kierros pankki maksaa kaikille agenteille Talletuskoron heidän Raha-summastaan. (Tämä on passiivinen tapa kasvattaa varallisuutta).Lainan myöntäminen (Rahan luominen):Agentti (Työntekijä tai Pääoma) pyytää lainaa Pankilta (esim. "haluan asuntolainan" tai "haluan investointilainan").Pankki arvioi riskin: Onko agentilla tuloja? Onko hänellä vakuuksia (esim. asunto itse)? Jos agentin Tulot tai Varallisuus ovat liian matalat, pankki hylkää lainahakemuksen.Jos hakemus hyväksytään:Pankki luo Laina-objektin (esim. Laina(summa=100k, korko=3%, agentti=X)).Pankki lisää agentin X Raha-muuttujaan +100k. (Tässä kohtaa rahan määrä simulaatiossa kasvoi!)Agentilla X on nyt myös Velka-muuttuja, jossa lukee 100k.3. 💳 Velka (Mekaniikka ja Kierto)Velka ei ole agentti, vaan ominaisuus (muuttuja) agenteilla (Työntekijä.Velka, Pääoma.Velka, Valtio.Velka).Miten velka vaikuttaa kiertoon?Joka simulaation kierros (esim. kuukausi), ennen kuin agentit voivat kuluttaa:Koronmaksu: Agentti maksaa Pankille Velka * Lainakorko / 12. Tämä on Pankin tuloa.Lyhennys: Agentti maksaa Pankille pakollisen lyhennyksen (esim. 1/300-osa lainan pääomasta).Rahan tuhoutuminen: Kun lyhennys maksetaan, agentin Raha vähenee JA agentin Velka vähenee. Pankin taseessa sekä saamiset että talletukset supistuvat. Rahaa tuhoutuu kierrosta.Miksi velkaa otetaan?Tämä on mallin ydin. Velkaa ei oteta huvin vuoksi, vaan varallisuuden hankkimiseksi.Työntekijä-agentti: Ei voi ostaa asuntoa palkallaan. Hän ottaa asuntolainan pankista. Nyt hänellä on Velka = 100k mutta myös Varallisuus = 100k (Asunto). Hänen nettovarallisuutensa on 0, mutta hänellä on omaisuus, jonka arvo voi nousta (jos malliin lisätään asuntomarkkinat).Pääoma-agentti: Haluaa kasvattaa tuotantoaan, mutta Kassavarat eivät riitä. Hän ottaa investointilainan ja ostaa lisää "pääomaa" (koneita tms.). Hän tekee vipuvaikutusta: jos lainan korko on 3 % mutta pääoman tuotto ($r$) on 8 %, hän tekee 5 % voittoa "ilmaisella" rahalla. Tämä kiihdyttää varallisuuden kasautumista valtavasti.Tällä mallilla saat aikaan dynaamisen kierron, jossa rahan määrä elää (kasvaa ja supistuu) talouden aktiviteetin (lainanoton) mukaan, ja valtio toimii tulojen ja varallisuuden tasaajana (tai alijäämällään kiihdyttäjänä).Tämä lisää malliin huomattavasti monimutkaisuutta. Erityisesti asuntomarkkinoiden lisääminen on iso askel.Haluatko seuraavaksi, että suunnittelemme tarkemmin, miten asuntomarkkinat ja asuntolainat mallinnetaan? Se on useimmille ihmisille suurin yksittäinen varallisuuden (ja velan) erä.

Loistava suunta! Juuri nämä elementit – asunto-omistus ja yrittäjyys – ovat ne kaksi pääasiallista moottoria, jotka erottavat varakkuuden (wealth) pelkistä tuloista (income).Näin ne toimivat nyky-yhteiskunnassa ja näin rakennamme ne simulaatioon.1. 💰 Varallisuuden uudelleenmäärittely (Assets vs. Income)Ensiksi, meidän on tarkennettava agentin taloutta. Agentilla ei ole vain Rahaa, vaan hänellä on tase:Varat (Assets):Käteisvarat (Raha pankkitilillä)Reaaliomaisuus (Lista omistetuista asunnoista ja niiden markkina-arvo)Yritysomistus (Lista omistetuista yrityksistä ja niiden arvo)Velat (Liabilities):Asuntolainat (Lista lainoista)Yrityslainat (Lista lainoista)Agentin Nettovarallisuus (Net Worth), jota me tutkimme, on:Nettovarallisuus = (Käteisvarat + Reaaliomaisuuden arvo + Yritysomistusten arvo) - (Asuntolainat + Yrityslainat)Tämä on kriittinen ero, koska suurin osa varallisuuden kasvusta ei tule palkasta säästämällä, vaan omistettujen varojen (asuntojen ja yritysten) arvon noususta.2. 🏡 Asuntomarkkinat ja AsuntolainatUseimmille ihmisille asunto on suurin yksittäinen varallisuuden ja velan erä.Miten se toimii nyt?Tarve: Agentti haluaa ostaa asunnon (esim. ikä 25-40, vakituinen työ).Oma pääoma: Agentilla on oltava säästössä 5-15 % asunnon hinnasta (käsiraha).Lainahakemus: Agentti menee pankkiin. Pankki tarkistaa agentin Tulot (palkka) ja Säästöt (oma pääoma) ja laskee stressitestatun maksukyvyn.Lainan myöntö: Pankki luo tyhjästä 25 vuoden asuntolainan, joka kattaa 85-95 % hinnasta.Kauppa: Agentti ostaa asunnon. Hänen taseensa muuttuu: Käteisvarat laskevat käsirahan verran, Reaaliomaisuus kasvaa asunnon arvon verran, ja Velat kasvavat lainan verran.Seuraukset: Agentti maksaa seuraavat 300 kierrosta (25 vuotta) lainaa takaisin (lyhennys + korko), mikä vähentää hänen kulutuskykyään. Samalla hän kuitenkin omistaa asunnon.Miten mallinnetaan simulaatiossa?A. Uudet objektit: "Asunto"Simulaatioon on luotava joukko Asunto-objekteja.Ominaisuudet: ID, Markkina-arvo, Omistaja (agentti X), Myynnissä (kyllä/ei).Kehittynyt malli: Asunnoilla voi olla Sijainti (esim. "Keskusta", "Lähiö"), joka vaikuttaa hinnan kehitykseen.B. Asuntomarkkinat (Mekaniikka)Tämä on oma "aliprosessinsa" joka kierroksella:Tarjonta: Agentit asettavat asuntojaan myyntiin (esim. jos agentti kuolee -> perikunta myy; jos agentti haluaa "päivittää" isompaan; jos agentti joutuu työttömäksi eikä pysty maksamaan lainaa).Kysyntä: Agentit, joilla ei ole asuntoa mutta on työpaikka ja riittävästi Käteisvaroja käsirahaan, yrittävät ostaa asunnon.Hinnanmuodostus (Tärkein!): Hinta ei ole kiinteä. Asunnon Markkina-arvo päivittyy joka kierros perustuen kysyntään ja tarjontaan.Jos Kysyntä > Tarjonta -> Kaikkien asuntojen Markkina-arvo nousee (esim. +0.5 % tällä kierroksella).Jos Tarjonta > Kysyntä -> Markkina-arvo laskee.C. Lainanotto-prosessi (Agentin näkökulma)Agentti A haluaa ostaa asunnon H (hinta 100 000):A tarkistaa säästönsä. Jos A.Käteisvarat < 10 000 -> Osto epäonnistuu.A pyytää lainaa Pankilta.Pankki tarkistaa: Onko A.Tulot > (Lainan kuukausierä * 3)?Jos OK, Pankki luo Asuntolaina-objektin (summa 90 000).Agentin A tase päivittyy:Käteisvarat: -10 000 (maksaa käsirahan)Reaaliomaisuus: +100 000 (saa asunnon)Velat: +90 000 (saa lainan)Nettovarallisuus: 0 (ei muutu ostohetkellä, mutta hän on nyt mukana markkinassa).Vaikutus varallisuuteen:Vipu (Leverage): Agentti hallitsee 100 000 euron arvoista omaisuutta vain 10 000 euron sijoituksella.Arvonnousu: Jos asuntomarkkinat nousevat 5 %, agentin Reaaliomaisuus on 105 000. Hänen Nettovarallisuutensa on nyt 5 000 (koska velka pysyi samana). Hän "tienasi" 5 000, mikä on 50 % tuotto hänen alkuperäiselle 10 000 euron sijoitukselleen.Eriarvoisuus: Ne, jotka pääsevät markkinoille (on työpaikka, saa säästettyä käsirahan), hyötyvät arvonnoususta. Ne, jotka eivät pääse, jäävät jälkeen, koska heidän säästöjensä arvoa syö inflaatio.3. 📈 Yrittäjyys ja OmistajuusTämä on mekanismi, jolla siirrytään "Työntekijä-agentista" "Pääoma-agentiksi".Miten se toimii nyt?Idea & Pääoma: Agentilla on idea tai taito. Hän tarvitsee alkupääoman.Rahoitus: Hän käyttää omia säästöjään tai (todennäköisemmin) hakee yrityslainaa pankista.Riski: Yrityslaina on paljon riskisempi pankille kuin asuntolaina (koska vakuutena on vain idea, ei konkreettista asuntoa). Siksi sen korko on korkeampi ja saanti vaikeampaa.Perustaminen: Agentti perustaa Yritys-agentin. Hän siirtää lainarahat ja säästönsä yrityksen Kassavaroiksi ja ostaa niillä "Pääomaa" (koneita, laitteita, toimisto).Toiminta: Yritys palkkaa työntekijöitä (muita agentteja), tuottaa, myy ja saa voittoa.Tuotto: Kierroksen lopussa yrityksen Voitto siirretään omistaja-agentin Käteisvaroihin (osinkona) tai pidetään yrityksen Kassavaroissa (kasvattaa yrityksen arvoa).Miten mallinnetaan simulaatiossa?A. Sosiaalinen liikkuvuus (Agentin päätös)Työntekijä-agentilla, jolla on korkea Taito ja/tai riittävästi Käteisvaroja (säästöjä), on tietty todennäköisyys (esim. 1 % / vuosi) yrittää perustaa yritys.B. "Yritys"-agentti (Tarkempi malli)Luodaan uusi agenttityyppi: Yritys.Ominaisuudet: Omistaja (agentti Y), Arvo, Kassavarat, Pääoma (koneiden määrä/arvo), Työntekijät (lista agenteista), Lainat.Toiminta:Yritys laskee, kuinka monta työntekijää se tarvitsee Pääomansa käyttöasteen perusteella.Se palkkaa työntekijöitä työmarkkinoilta (kuten aiemmin suunniteltu).Se tuottaa hyödykkeitä ja myy ne (kuluttaja-agenteille tai valtiolle).Se maksaa palkat työntekijöille ja korot/lyhennykset pankille.Lopuksi lasketaan Voitto = Tulot - Menot.Yrityksen Arvo päivittyy (esim. Arvo = 10 * Vuosivoitto).C. Rahoitus ja RiskiYrittäjäksi ryhtyvä agentti Y hakee Pankilta 50 000 euron yrityslainaa.Pankki arvioi riskin (korkeampi korko, esim. 8 %).Jos onnistuu, agentille Y tulee Velat: +50 000 ja hänelle syntyy Yritysomistus: +50 000.D. Konkurssi (Epäonnistuminen)Tämä on elintärkeää realismille!Jos Yrityksen Kassavarat menevät negatiiviseksi, eikä se saa enää lainaa pankista, se ajautuu konkurssiin.Yritys-agentti poistetaan simulaatiosta.Sen työntekijät saavat potkut (siirtyvät Tila = Työtön).Omistaja-agentti Y menettää kaiken Yritysomistus-varallisuutensa. Jos laina oli henkilökohtaisesti taattu, hän on nyt 50 000 euroa velkaa pankille ilman yritystä.Tämä agentti putoaa takaisin Työntekijä-luokkaan (tai työttömäksi) ja hänen Nettovarallisuutensa on rajusti negatiivinen.Yhteenveto: Agenttien taseetNäillä lisäyksillä agenttien taseet muuttuvat dynaamisiksi ja realistisiksi:AgenttityyppiTyypilliset Varat (Assets)Tyypilliset Velat (Liabilities)Varallisuuden kasvuNuori TyöntekijäKäteisvarat (vähän)Ei velkaaHitaasti (säästämällä palkasta)Asunnon-omistajaKäteisvarat, Reaaliomaisuus (Asunto)Asuntolaina (paljon)Nopeasti (jos asuntojen hinnat nousevat)YrittäjäKäteisvarat, Yritysomistus, ReaaliomaisuusAsuntolaina, YrityslainaRäjähdysmäisesti (jos yritys menestyy)VelkaantunutKäteisvarat (vähän)Kulutusluotto / KonkurssivelkaNegatiivinen (korot syövät tulot)Tämä malli kuvaa, kuinka velan (vipu) avulla hankittu omaisuus (asunnot, yritykset) on nyky-yhteiskunnassa ylivoimaisesti tehokkain tapa kasvattaa varallisuutta, mutta se sisältää myös merkittävän riskin.Nyt meillä on kasassa kaikki ydinpalikat: Valtio (verotus/tulonsiirto), Pankit (rahanluonti/laina), Asuntomarkkinat (varallisuus/velka) ja Yritykset (pääomatulo/riski).

Kyllä, nyt sidotaan kaikki yhteen! Tämä on se hetki, jolloin yksittäisistä säännöistä syntyy monimutkainen, "emergentti" järjestelmä, jossa tulokset voivat olla yllättäviä.

Tässä on hahmotelma siitä, miten yksi simulaatiokierros (esim. 1 kuukausi) voisi edetä. Järjestys on äärimmäisen tärkeä, koska se määrittää, mihin tietoon agentit perustavat päätöksensä.

🏛️ Vaihe 0: Alkutoimet (Valmistelu)
Keskuspankki päättää: Keskuspankki-agentti asettaa Ohjauskoron (esim. ulkoisen datan tai sisäisen inflaatiotavoitteen perusteella).

Pankit reagoi: Liikepankit päivittävät omat Lainakorot ja Talletuskorot suhteessa ohjauskorkoon.

Agenttien ikääntyminen: Kaikki agentit vanhenevat +1 kuukausi.

Syntymät: Luodaan uusia agentteja (esim. 25 %:lle 20-40-vuotiaista agenteista syntyy lapsi-agentti, joka on aluksi vanhempiensa talouden "riesa" (kuluttaa) mutta ei tee päätöksiä).

Kuolemat: Agenteilla on ikään perustuva kuolemanriski. Kun agentti kuolee, hänen koko nettovarallisuutensa (Varat - Velat) siirtyy perintönä hänen perillisilleen (esim. lapsi-agenteille). Tämä on valtava varallisuuspiikki perijöille.

🏭 Vaihe 1: Tuotanto & Työmarkkinat
Yritykset päättää: Yritys-agentit arvioivat edellisen kuun myynnin ja nykyisen Pääoman (koneet yms.) perusteella, kuinka monta työntekijää ne tarvitsevat. Ne joko luovat uusia työpaikkoja tai irtisanovat ylimääräisiä.

Työmarkkinat:

Työntekijä-agentit, joiden Tila = Työtön (sekä uudet työmarkkinoille tulevat nuoret agentit), hakevat avoimia työpaikkoja.

Yritykset palkkaavat hakijoista (esim. Taito-ominaisuuden perusteella).

Agenttien Tila päivittyy: Työtön -> Työssä, tai Työssä -> Työtön.

Tämä vaihe määrittää kuukauden työttömyysasteen.

💸 Vaihe 2: Tulot & Pakolliset Menot
Palkanmaksu:

Yritys-agentit maksavat palkat kaikille Työssä-tilassa oleville työntekijöilleen.

Samalla hetkellä Valtio ottaa palkasta suoraan progressiivisen tuloveron.

Tulonsiirrot:

Valtio maksaa eläkkeet (agenteille joiden Ikä > 65) ja työttömyyskorvaukset (agenteille joiden Tila = Työtön).

Velanhoito (Kriittinen vaihe):

Ennen kuin agentit voivat kuluttaa, heidän on pakko maksaa velkansa.

Kaikki agentit (myös Yritykset ja Valtio), joilla on Velka, maksavat Pankki-agentille kuukausittaisen lyhennyksen + koron.

Rahan tuhoutuminen: Lyhennyksen osuus poistuu kierrosta (agentin Käteisvarat vähenee, agentin Velka vähenee).

Pankin tulo: Koron osuus on Pankki-agentin tuloa.

🛒 Vaihe 3: Kulutus & Säästäminen (Hyödykemarkkinat)
Kulutuspäätös: Agentit laskevat Käytettävissä olevat varat (Palkka/Tuki - Verot - Lainamenot).

He päättävät säästöasteensa (esim. 10 %) ja käyttävät loput kulutukseen (esim. 90 %).

Hyödykemarkkinat:

Agentit ostavat hyödykkeitä Yritys-agenteilta. Raha siirtyy kuluttajilta yritysten Kassavaroihin.

ALV: Joka ostoksesta Valtio kerää automaattisesti 24 % (tai asetettu %) itselleen.

Tämä vaihe tuottaa Yritys-agenteille niiden kuukauden liikevaihdon.

🏦 Vaihe 4: Varallisuusmarkkinat & Investoinnit
Nyt agentit katsovat Käteisvarojaan (mitä jäi säästöön) ja päättävät, mitä tekevät.

Asuntomarkkinat:

Tietyt agentit asettavat asuntojaan myyntiin (perikunnat, muuttajat, velkaongelmaiset).

Agentit, joilla ei ole asuntoa mutta on riittävästi säästöjä käsirahaan, yrittävät ostaa.

Lainaneuvottelu: Ostoa yrittävä agentti hakee Pankilta asuntolainaa. Pankki joko hyväksyy (luo uutta rahaa) tai hylkää (riskiarvion perusteella).

Jos laina ja käsiraha OK, kauppa tapahtuu. Asunto-objektin omistaja vaihtuu.

Hinnan päivitys: Markkinamekanismi päivittää kaikkien asuntojen arvoa kysynnän ja tarjonnan perusteella.

Yrittäjyys:

Agentti, jolla on riittävästi säästöjä (tai Taito-taso), voi päättää ryhtyä yrittäjäksi.

Hän hakee Pankilta yrityslainaa.

Jos laina myönnetään, simulaatioon luodaan uusi Yritys-agentti, jonka Omistaja on tämä agentti.

Yritysten investoinnit:

Yritys-agentit laskevat kuun tuloksen (Liikevaihto - Palkat - Lainamenot).

Jos tulos on positiivinen (voitto), ne voivat päättää investoida: ostaa lisää Pääomaa (koneita) kasvattaakseen tuotantoaan ensi kuussa. Tämä voi vaatia uuden yrityslainan.

📊 Vaihe 5: Kierroksen Päättely & Taseet
Tarkistukset:

Yritys-agentit, joiden Kassavarat ovat pysyvästi negatiiviset, ajautuvat konkurssiin (poistuvat pelistä, työntekijät irti).

Työntekijä-agentit, joiden Käteisvarat menevät negatiiviseksi eivätkä saa enää lainaa, ajautuvat henkilökohtaiseen konkurssiin (varat myydään, siirtyy takaisin "nollapisteeseen" minimituelle).

Datan keräys: Simulaattori tallentaa tästä kuukaudesta kaiken datan:

Koko talouden varallisuus- ja tulojakauma (Gini-kertoimet).

Työttömyysaste.

Asuntojen hintaindeksi.

Rahan määrä taloudessa (M1).

Valtion budjetin tila (ali-/ylijäämä).

...ja sitten: siirry seuraavaan kuukauteen (Vaihe 0).

Tämä malli luo dynaamisen järjestelmän, jossa varallisuus kasautuu niille, jotka omistavat (asuntoja, yrityksiä) ja pystyvät käyttämään lainavipua hyväkseen, samalla kun riski (työttömyys, konkurssi) ja elinkaari (perintö) luovat jatkuvaa liikettä ja epätasa-arvoa.

Miltä tämä kuukausisykli vaikuttaa? Onko jokin vaihe, jota haluaisit erityisesti hienosäätää tai tutkia tarkemmin?



Rakentaa agenttipohjainen, monitaajuuksinen simulaattori, joka tuottaa mikro- ja makrotason ilmiöitä rahoitus- ja reaalitaloudesta: hinnanmuodostus (limit order book), luotonlaajeneminen ja -kiristyminen, varallisuuden kasautuminen, työllisyys, asuntomarkkinat sekä politiikkatoimet (verotus, rahapolitiikka). Lähtökohtana on aiempi suunnitelma, jossa on jo valtion, pankkien, asuntomarkkinoiden ja yrittäjyyden rakenteet; laajennamme sen markkinamikrorakenteeseen, riskiverkostoihin ja kalibrointiputkeen.


1) Mallin ydinvalinnat
1.1 Aikadynamiikka (monitaajuus)

Mikroaika (sekunti–minuutti): arvopaperimarkkinoiden tilausten syöttö ja matcher (limit order book, LOB), toteutukset, spreadit, order flow, likviditeetin syvyys.
Meso (päivä/viikko): varainhoitajien allokaatio, yritysten tuotanto- ja varastopäätökset, repo/marginaalien päivitys, lainasalkkujen luottoluokitukset.
Makro (kuukausi/kvartaali): työllisyys, palkat, verotus ja tulonsiirrot, investoinnit, asuntomarkkinan hintapäivitys, luottosyklin tila, rahapolitiikka ja finanssipolitiikka. Aiemmassa suunnitelmassa määritelty kuukausisykli toimii tämän makrotason rungon pohjana.
1.2 Talousympäristö

Suljettu pieni avotalous (esim. FI/EEA-tyyppiset instituutiot): yksi valuutta, pankkikeskeinen rahoitus, keskuspankki asettaa ohjauskoron; liikepankit luovat luottoa endogeenisesti (lainasta syntyy talletus).
Markkinat: osakkeet/ETF:t, yrityslainat, valtion velkakirjat, repo, asuntomarkkina (reaaliomaisuus), työmarkkina ja hyödykemarkkinat.
1.3 Tavoite-ilmiöt ("stylized facts"), joita simulaation tulee tuottaa
1) Pörssituottojen paksuhäntäisyys ja volatiliteetin klusteroituminen. 2) Hintojen palautuminen ja tilauskirjan epäsymmetria (buy/sell pressure). 3) Luottosyklin prosyklisyys (marginaalien kiristyminen kriiseissä), fire sale -dynamiikka. 4) Varallisuuden epätasainen jakauma (tulot vs. varallisuus, Gini), ja perintöjen merkitys.


2) Agentit ja tilamuuttujat
2.1 Kotitaloudet (heterogeeniset)

Tilat: ikä, koulutus/taito, työllisyys, palkka, talletukset, asuntopositio(t), asuntolaina(t), kulutus/säästöaste, riskinottoaste, varallisuus- ja tulohistoria.
Päätökset: kulutus vs. säästö, asunnon osto/myynti (käsiraha + asuntolaina), allokaatio (osakkeet/rahasto, talletukset, velan lyhennys), ura/koulutus.
Rajoitteet: luottokelpoisuus, LTV/LTI, stressitesti; velan hoito ennen kulutusta (aiempi malli).
2.2 Yritykset

Tilat: kassavarat, pääomakanta, tilauskanta/varasto, työntekijät, velka/yrityslainat, riskiluokitus.
Päätökset: palkkaus/irtisanominen, hinnan- ja tuotannon määritys, investoinnit (omalla kassalla vs. lainalla), osingot/rahastointi.
Konkurssi: maksukyvyttömyys → likvidointi, irtisanomiset, tappio lainanantajille (aiemman mallin periaate).
2.3 Varainhoitajat / sijoitusrahastot / eläkerahastot

Tilat: AUM, sallittu velkavipu, likviditeettibudjetti, redemptio-isku (lunastukset), VaR- ja margin-vaateet.
Strategiat:Fundamentaalit: arvoperusteinen, tulosennusteet, korko/luottomarginaali.
Tekniset: momentum, mean reversion, trend following.
Passiiviset: indeksiflow, säännöllinen rebalansointi.
2.4 Markkinatakaajat / HFT-agentit

Tilat: inventaario, hintasyöttösäännöt (quote-kertoimet), latenssi, riskirajat.
Päätökset: bid/ask-quotejen asetus LOB:iin, spreadin säätö volatiliteetin ja inventaarion mukaan.
2.5 Pankit (liikepankit)

Tilat: tase (talletukset, lainat, likviditeetti, oma pääoma), riskimarginaalit, luotonannon säännöt, vakuus- ja hair-cut -taulukot.
Päätökset: talletus- ja lainakorot (ohjauskoron spread), luottopäätökset (PD/LGD-heuristiikka), luoton hinnoittelu, marginaalivaatimusten päivitys, repo-rahoitus.
Rahanluonti: hyväksytty laina kasvattaa talletuksia (endogeeninen raha; aiempi malli).
2.6 Keskuspankki

Tilat: ohjauskorko, QE/QT-säännöt, hätälikviditeetin ikkunat.
Päätökset: reaktiosääntö (esim. Taylor-tyyppinen) inflaatioon ja työttömyyteen; markkinastressissä repo- ja vakuuspolitiikan väljentäminen.
2.7 Valtio

Tilat: budjetti, velka, verotaulukot, tulonsiirto-ohjelmat.
Päätökset: verotuksen taso, julkinen kulutus, automaattiset stabilisaattorit (työttömyyskorvaus, eläkkeet). Aiemman mallin verot ja tulonsiirrot toimivat pohjana.
2.8 CCP/clearing, välittäjät ja repo-markkina

Tilat: vakuuspoolit, hair-cut -matriisi, margin call -logiikka.
Päätökset: päivittäinen variaatiomarginaali, default waterfall, netotus.


3) Markkinamikrorakenne (Limit Order Book, LOB)
3.1 Tilauskirja

Kaksoishuutokauppa jatkuvalla kaupankäynnillä.
Tietorakenne: monitasoinen bid/ask-puu (hintataso → määrä, aikaleimat), FIFO prioriteetti tasolla.
3.2 Agenttien interaktio LOB:ssa

Order-tyypit: limit, market, cancel/replace, iceberg.
Order flow -generointi: jokaiselle agenttiluokalle stohastinen prosessi, jonka intensiteetti riippuu volatiliteetista, uutisshokeista ja omasta inventaariosta.
3.3 Toteutus ja hinnanmuodostus

Matcheda transaktiot määräävät last price; midprice = (best bid + best ask)/2; spread ja syvyys syntyvät endogeenisesti.
Hintavaikutusfunktiot (permanentti vs. tilapäinen), jotka riippuvat order flow’n epätasapainosta ja kirjan syvyydestä.
3.4 Aukot, likviditeettikato ja flash-liikkeet

Likviditeettishokit (esim. rahastolunastukset) aiheuttavat myyntiaallon → spread laajenee → toteutukset syövät syvyyden → hinnat hyppäävät; mahdolliset "fire sale" -ketjut repo-/marginaalikanavan kautta.


4) Luotto- ja vakuuskanava (vipu ja pakkomyynnit)
1) Kotitalouksien asuntolainat: LTV/LTI, stressitesti, lyhennys + korko ennen kulutusta (aiempi malli). 2) Yrityslainat: korko = ohjauskorko + riskimarginaali; default → tappiot pankille; konkurssi poistaa yritysagentin (aiempi malli). 3) Sijoittajien repo/marginaalit: hair-cut kasvaa volatiliteetin noustessa → vipu pakittuu → pakkomyyntejä → hintojen lasku → lisää marginaaleja (negatiivinen kehä). 4) Pankkien likviditeetti: tukkumarkkina ja keskuspankin hätärahoitus; likviditeettilimiitit ohjaavat luotonantoa.


5) Tapahtumasarja per aika-askel
5.1 Mikro (sekunti–minuutti)

Uutis-/signaalishokit (makrodata, yritysuutiset)
Order flow -generointi agenttiluokittain
Order matching LOB:ssa (toteutukset, hinnat, spread)
Inventaarion ja riskirajojen päivitys (market makerit kiristävät leveys/spread)
5.2 Päivä/viikko

Rahastojen rebalansointi, lunastukset/subskriptiot
Repo- ja marginaalipäivitykset, margin callit → mahdolliset pakkomyynnit
Pankkien tukkurahoitus ja sisäinen likviditeettisiirto
5.3 Kuukausi/kvartaali

Palkat, verot ja tulonsiirrot; velanhoito ennen kulutusta (aiempi malli)
Kulutus, hyödykemarkkinat ja ALV (aiempi malli)
Asuntomarkkinat: ostot, myynnit, hintapäivitys; uudet asuntolainat (aiempi malli)
Yritysten investoinnit ja mahdolliset konkurssit (aiempi malli)
Pankkien voitot/tappiot, pääomavaatimukset; valtion budjettitasapaino
Keskuspankin korkopäätös (reaktiosääntö)


6) Kalibrointi, validointi ja herkkyysanalyysi
6.1 Parametrien kalibrointi

Menetelmät: Simulated Method of Moments (SMM) + Approximate Bayesian Computation (ABC).
Tavoitemomentit:finanssimarkkinoissa: tuottojen kurtosis, Hurst/vola-klusterointi, spread-jakauma, order flow -autokorrelaatio, price impact -käyrä.
reaalitaloudessa: työttömyysasteen taso ja volatiliteetti, säästöaste, asuntolainojen LTV-jakauma, asuntojen hintaindeksin volatiliteetti.
6.2 Validointi (stylized facts)

Tarkista, että malli toistaa: paksuhäntäiset tuotot; volan klusterointi; volyymi–volatiliteetti -korrelaatio; luottomarginaalien prosyklisyys; varallisuuden Pareto-häntä.
6.3 Herkkyys (robustiuden varmistus)

Global SA: Sobol/FAST.
Stressiskenaariot: korkoshokki, likviditeettipako (rahastolunastus), asuntomarkkinan 20–30 % lasku, pankin vakavaraisuussokki.


7) Implementaatiokehikko
7.1 Teknologia

Kieli: Python (prototyypit) → suorituskykykriittiset osat Numba/Cython tai Rust-moduuli.
ABM-framework: Mesa (agentit, stepperi), oma LOB-moduuli (C++/Rust sidoksilla tarvittaessa).
Tieto: Parquet/Arrow, konfiguraatio YAML; satunnaissiemenet; Monte Carlo -eräajo.
Lokitus & audit trail: jokainen toteutus, tilaus, marginaalikutsu, konkurssi.
7.2 Moduulirakenne

core/clock.py — monitaajuuskello ja scheduler
agents/ — kotitalous, yritys, rahasto, market maker, pankki, valtio, keskuspankki, CCP
markets/lob.py — limit order book ja matcher
credit/ — luotonanto, PD/LGD-heuristiikka, repo & marginaalit
macro/ — työmarkkinat, hyödykemarkkinat, asuntomarkkina
policy/ — raha- ja finanssipolitiikka
calibration/ — SMM/ABC, momenttien laskenta
io/ — datadumpit, mittarit, visualisoinnit
7.3 Tilasarjat ja mittarit (automatisoitu raportointi)

Markkina: hintasarjat, spread, depth, turnover, order imbalance.
Luotto: lainakanta, LTV/LTI, default-aste, marginaalihaircutit.
Makro: työttömyys, palkkataso, Gini (tulo/varallisuus), inflaatio-proxy (hyödykeindeksi), julkisen talouden alijäämä.


8) Päätössäännöt (esimerkit)
8.1 Kotitalous, kulutus–säästö
käytettävissä = palkka + tulonsiirrot − verot − (korko+lyhennys)
kulutus = min(kulutus_kiinteä + MPC * (käytettävissä − kulutus_kiinteä), käytettävissä)
säästö = käytettävissä − kulutus


8.2 Asunnon osto
if ei_asuntoa and käsiraha ≥ LTV_min * hinta and stressitesti_ok:
    hae_laina(hinta − käsiraha)
    osta_asunto()


8.3 Rahaston rebalansointi
if drift_portfoliossa > kynnys:
    toteuta_markET/limit tilauksia riskibudjetin puitteissa


8.4 Market maker -spreadin säätö
spread = base + α*volatiliteetti + β*|inventaario|
quote_size = min(max_size, γ * kirjan_syvyys)




9) Datan ja kalibraation lähteet (FI-konteksti)

Makro ja tulonjakotilastot: tilastovirasto/viranomaislähteet.
Pankkikorko- ja luottokannat: keskuspankkijulkaisut.
Pörssidata: pörssi/markkinatakaajadata (tasot: transaktio/quote, jos saatavilla).
Asuntoindeksi: viranomais- tai rekisteripohjainen.
(Tarkat linkit voidaan lisätä, kun päätät ensimmäisen kohdemarkkinan ja saatavuuden.)


10) Testausstrategia

Yksikkötestit: LOB-matcher (hintataso, FIFO), marginaalikutsu, verolaskenta.
Integraatiotestit: luotto → LOB → marginaali → pakkomyynti -ketju.
Backtest-skenaariot: korkopiikki, PMI-shokki, likviditeettipako.
Replikoitavat kokeet: kiinteä siemen, kiinteä konfiguraatio, Monte Carlo -toistot (≥100).


11) Projektin tiekartta (12–14 viikkoa, prototyyppi → versio 0.9)

V1 (viikot 1–2): Core-scheduler + LOB-minimi + market maker; perusmittarit.
V2 (viikot 3–4): Rahastot (momentum/fundamental), volatiliteetti-ilmiöt.
V3 (viikot 5–6): Pankit + luotonanto + repo/marginaalit.
V4 (viikot 7–8): Makro-kerros: palkat, verot, tulonsiirrot; kulutus/ALV.
V5 (viikot 9–10): Asuntomarkkina + kotitalouksien elinkaari + perintö.
V6 (viikot 11–12): Kalibrointi (SMM/ABC), herkkyysanalyysi, dashboard.
Hardening (viikot 13–14): suorituskyky, testikattavuus, dokumentaatio.


12) Dokumentointi ja läpinäkyvyys

Kaikki säännöt ja parametrit julkiseen MODEL_CARD.md -tiedostoon: tarkoitus, oletukset, rajoitteet, intended use / out of scope.
Versioidut konfiguraatiot (configs/), kokeet experiments/.


13) Riskit ja rajoitteet

Ylisovitus hetken markkinarakenteeseen (hedge: SMM/ABC + out-of-sample).
LOB:n laskennallinen kuorma (hedge: event-driven simulaattori, aggressiivinen profilointi, Numba/Rust).
Datan saatavuus: varasuunnitelma syntettiselle order flow’lle, kunnes historiadata varmistuu.


14) Seuraavat konkreettiset askeleet

Valitse ensimmäinen kohdemarkkina (esim. 3–5 likvideintä osaketta) ja aikataajuus (100 ms / 1 s / 1 min).
Lukitse agenttivalikoima v0.1: market maker + momentum + fundamental + passiivinen rahasto.
Määritä parametri-perussetti (spread-basis, order-intensiteetit, riskirajat) ja mittarit (spread, depth, kurtosis, vol-klusterointi).
Toteuta V1–V2 ja aja 100× Monte Carlo; tarkista, syntyykö haluttuja stylized facteja.
Kun mikrotaso toimii, kytke luotto- ja makrokerros (V3–V4) ja tuo asuntomarkkina (V5).


Miten tämä vastaa aiempaa suunnitelmaasi?

Säilytimme valtion, pankkien, elinkaaren, perinnön, asuntolainat ja yrittäjyyden keskeisen dynamiikan ja nostimme ne monitaajuiseen kehikkoon.
Lisäsimme LOB-pohjaisen hinnanmuodostuksen, repo/marginaalikanavan, CCP:n ja varainhoitajien käyttäytymisen, jotta rahoitusmarkkinoiden mikroilmiöt syntyvät endogeenisesti.
Haluatko, että teen seuraavaksi configs/v0.1.yaml -luonnoksen ja LOB-matcherin pseudokoodin, jotta pääset heti toteutukseen?
