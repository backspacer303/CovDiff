# *CovDiff* - alat za generisanje i prikaz razlika u pokrivenosti koda testovima 

Alat generiše html stranice sa izveštajima o pokrivenosti kod celog projekta nakon pokretanja dva testa. Izveštaji se generišu za svaku izvornu datoteku posebno. Na stranicama se nalaze različite uporedne informacije o pokrivenosti koda testovima pa je tako moguće videti u kojim datotekama i na kojim linijama postoje razlike.

## Opis 

Klasa `ProjectCodeCoverage` reprezentuje izveštaj o pokrivenosti koda celog projekta tj. svake izvorne datoteke, nakon pokretanja jednog testa i obavlja sledeće operacije:
- čisti diretorijum u kome je izgrađen projekat od prethodnih korišćenja koda odnosno briše sve datoteke formata `.gcda` koje postoje
- pokreće zadati test zadatom komandom nakon čega se formiraju datoteke formata `.gcda` 

- radi rekurzivni obilazak zadatog direktorijuma u kome je izgrađen projekat i za svaku pronađenu datoteku formata `.gcda`:
  - pokreće alat `gcov` i generiše izveštaj o pokrivenosti koda u formatu `json` 
  - parsira izveštaj iz datoteke formata `json`  i pamti rezultate za odgovarajuću izvorne datoteke

Klasa `HtmlReportDisplay` koristi informacije o pokrivenosti izvornih datoteka iz prethodne klase kako bi generisala izveštaj u formatu `html`  o pokrivenosti koda testovima. U okviru ove klase generišu se sledeći prikazi:
- Početna strana na kojoj se nalazi:
  - **<span style="color:orange"> Izveštaj "Mini report" </span>** - sadrži sumarne informacije o pokrivenosti projekta testom, za oba testa, sa sledećim informacijama
    -  broj obrađenih datoteka formata `.gcda` 
    -  ukupan broj obrađenih izveštaja (ima ih više od broja  datoteka formata `.gcda` jer jedna takva datoteka može sadržati više od jednog izveštaja)
    -  broj jedinstvenih izvornih datoteka pogođenih testom (bez izvornih datoteka sa 0% pokrivenosti)
    -  ukupan broj obrađenih jedinstvenih izvornih datoteka (sa izvornim datotekama sa 0% pokrivenosti) 
    -  ekstenzije izvornih datoteka pogođenih testom
    -  brojač za svaku ekstenziju
  -  **<span style="color:orange"> Listu sa svim izvornim datotekama pogođenim nekim od testova </span>** koja sadrži sledeće kolone
     -  naziv izvorne datoteke koji je ujedno link sa kojim je moguće otići na stranicu sa detaljnim izveštajem 
     -  procentualnu pokrivenost izvorne datoteke prvim testom, pored koga može stajati oznaka `diff` što znači da postoje linije izvorne datoteke pokrivene prvim testom a da nisu pokrivene drugim testom
     -  procentualnu pokrivenost izvorne datoteke drugim testom, pored koga može stajati oznaka `diff` što znači da postoje linije izvorne datoteke pokrivene drugim testom a da nisu pokrivene prvim testom
     -  polje za pretragu naziva izvornih datoteka
     
  -  **<span style="color:orange"> Listu sa svim izvornim datotekama u kojima postoje razlike u pokrivenosti jednim testom u odnosu na drugi </span>**
     - lista sadrži spisak onih izvornih datoteka iz prethodne liste koje imaju makar jednu `diff` oznakau a ima iste kolone kao prethodna lista

- Stranice za svaku pojedinačnu izvornu datoteku na kojima se nalaze:
  
  - **<span style="color:orange"> Zbirni izveštaj ("Summary Report") </span>** - predstavlja uniju linija pokrivenih svim zadatim testovima. Predstavljen je tabelom sa kolonama
    - `Line number` - broj linije u izvornoj datoteci
    - `Line` - konkretna linija izvornog koda koja može biti obojena
      - zeleno - ukoliko je linija pokrivena bilo kojim testom
      - crveno - ukoliko linija nije pokrivena ni sa jednim testom
      - belo (ne obojena) - ukoliko linije nije od interesa
    - `Number of hits` - broj izvršavanja svake linije, može sadržati vrednosti
      - nula - za crvene linije
      - pozitivan ceo broj - za zelene linije
      - "----" - za linije koje nisu od interesa
    - `Tests that cover line` - lista imena testova koje pokrivaju liniju (samo za zelene linije)
  - **<span style="color:orange"> Izveštaj o funkcijama ("Functions Report")</span>** - sadrži informacije o tome koliko je puta izvršena svaka od funkcija, zbirno po svim testovima. Kolone su sledeće
    - `Function name` - ime funkcije
    - `Number of hits` - ukupan broj izvršavanja
  - **<span style="color:orange"> Izveštaj o razlikama ("Coverage Diff") </span>** - sadrži linije koje su pokrivene prvim a nisu pokrivene drugim testom i obrnuto, linije koje su pokrivene drugim a nisu pokrivene prvim testom. Kolone su sledće:
    - `Line number` - broj linije u izvornoj datoteci
    - `<test1_name> BUT NOT <test2_name>` - linija izvornog koda koja može biti obojena
      - žuto - ukoliko je linija pokrivena prvim testom a nije pokrivena drugim testom
      - belo (ne obojena) - inače
    - `Line number` - još jednom broj linije u izvornoj datoteci
    - `<test2_name> BUT NOT <test1_name>` - linija izvornog koda koja može biti obojena
      - narandžasto - ukoliko je linija pokrivena drugim testom a nije pokrivena prvim testom
      - belo (ne obojena) - inače
  - **<span style="color:orange"> Uporedni prikaz pokrivenih linija ("Side By Side Comparison")</span>** - sadrži linije pokrivene prvim testom i do njih linije pokrivene drugim testom zarad lašeg vizuelnog poređenja. Kolone su sledeće
    - `Line number` - broj linije u izvornoj datoteci
    - `<test1_name>` - linija izvornog koda koja može biti obojena
      - zeleno - ukoliko prvi test pokriva liniju
      - belo (ne obojena) - inače
    - `Number of hits` - broj izvršavanja svake linije, može sadržati vrednosti
      - nula - za neizvršene linije
      - pozitivan ceo broj - za izvršene linije
      - "----" - za linije koje nisu od interesa
    -  `Line number` - još jednom broj linije u izvornoj datoteci
    - `<test2_name>` - linija izvornog koda koja može biti obojena
      - zeleno - ukoliko drugi test pokriva liniju
      - belo (ne obojena) - inače
    - `Number of hits` - broj izvršavanja svake linije, može sadržati vrednosti
      - nula - za neizvršene linije
      - pozitivan ceo broj - za izvršene linije
      - "----" - za linije koje nisu od interesa

## Upotreba

```
python3 covdiff.py [-h] 
[--source-file source_file] [--object-path object_path]
directory_path test1 test2 coverage_dest 
command [command_arg [command_arg ...]]
```
### Obavezni argumenti
`directory_path` - putanja do direktorijuma u kome je izgrađen projekat

`test1` - putanja do datoteke sa kodom prvog testa ili ime prvog testa

`test2` - putanja do datoteke sa kodom drugog testa ili ime drugog testa

`coverage_dest` - direktorijum u kojem će biti smešteni html prikazi

`command` - željena komanda za pokretanje testova, nakon čega se može naći nula ili više argumenata komande (`command_arg`) zadatih bez minusa ispred (minusevi se dodaju naknadno u kodu)   
format pokretanja komande iz koda je sledeći   
`command test1 -command_arg -command_arg ...`   
ukoliko je jedan od argumenata komande opcija `o` sledećem u nizu argumenata neće biti dodat minus kako ime izlazne datoteke komande ne bi sadržalo minus na početku 

### Opcioni argumenti
`-h`, `--help` - prikaz uputstva za korišćenje

`--source-file` - opcija kojom korisnim može zadati ime izvorne datoteke od interesa, u tom slučaju se generiše izveštaj samo za nju

`--object-path` - opcija koja se mođe navesti uz `--source-file` a koja označava putanju do objektne datoteke koja odgovara izvornoj datoteci od interesa. Tada se ne vrši rekurzivni obilazak celog build direktorijuma već se direktno pristupa zadatoj lokaciji pa se i rezultat dobija brže.

`--report-formats` - opcija kojom se zadaje lista formata izveštaja koje je potrebno generisati. Prilikom navođenja, formati se razdvajaju zarezom. Ukoliko se ne navede ova opcija, podrazumevano se generiše prikaz u formatu `html`.

`--summary-reports` - opcija kojom se zadaju lista sumarnih izveštaja koje je potrebno generisati. Prilikom navođenja, sumarni izveštaji se razdvajaju zarezom. Ukoliko se ne navede ova opcija, podrazumevano se generiše sumarni izveštaj `MiniReport`.

## Primeri pokretanja alata
Primere pokretanja alata *CovDiff* moguće je pogledati u okviru dirktorijuma [Examples](./Examples/). Tu su dostupni i rezultati pokretanja alata nad jednostavnim projektom ali i rezultai pokretanja nad projektom *LLVM*.

<br>

## Zavisnosti

Za generisanje html prikaza korišćen je paket [Airium](https://pypi.org/project/airium/). Paket je moguće instalirati pozivom komande:

```bash
pip install airium
```
Aplikacija koristi alat `GCC gcov` za generisanje izveštaja o pokrivenosti koda pa je potrebno imati taj alat instaliran na sistemu.

Aplikacija pretpostavlja da je projekat nad kojim se pokreće obrada preveden uz zadavanje opcija `-ftest-coverage` i `-fprofile-arcs`. Ove opcije je moguće zadati npr. programskom prevodiocu `GCC`.
