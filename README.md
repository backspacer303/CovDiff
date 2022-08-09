# Skripta za generisanje razlika u pokrivenosti koda testovima

## Opis 

Klasa `CodeCoverage` reprezentuje izveštaj o pokrivenosti koda nakon pokretanja jednog testa i obavlje sledeće operacije:
- pronalazi `.gcno` datoteku koja odgovara zadatoj izvornoj datoteci
- pokreće zadati test zadatom komandom nakon čega se formira `.gcda` datoteka
- pokreće `gcov` alat i generiše izveštaj o pokrivenosti koda u `json` formatu
- izveštaj pamti u poseboj datoteci na zadatoj lokaciji

Klasa `HtmlReport` koristi informacije iz prethodne klase kako bi generisala html izveštaj o pokrivenosti koda testovima. U okviru ove klase generišu se sledeći prikazi:
- <span style="color:orange"> Zbirni izveštaj ("Summary Report") </span> - predstavlja uniju linija pokrivenih svim zadatim testovima. Predstavljen je tabelom sa kolonama
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
- <span style="color:orange"> Izveštaj o funkcijama ("Functions Report")</span> - sadrži informacije o tome koliko je puta izvršena svaka od funkcija, zbirno po svim testovima. Kolone su sledeće
  - `Function name` - ime funkcije
  - `Number of hits` - ukupan broj izvršavanja
- <span style="color:orange"> Izveštaj o razlikama ("Coverage Diff") </span> - sadrži linije koje su pokrivene prvim a nisu pokrivene drugim testom i obrnuto, linije koje su pokrivene drugim a nisu pokrivene prvim testom. Kolone su sledće
  - `Line number` - broj linije u izvornoj datoteci
  - `<test1_name> BUT NOT <test2_name>` - linija izvornog koda koja može biti obojena
    - žuto - ukoliko je linija pokrivena prvim testom a nije pokrivena drugim testom
    - belo (ne obojena) - inače
  - `Line number` - još jednom broj linije u izvornoj datoteci
  - `<test2_name> BUT NOT <test1_name>` - linija izvornog koda koja može biti obojena
    - narandžasto - ukoliko je linija pokrivena drugim testom a nije pokrivena prvim testom
    - belo (ne obojena) - inače
- <span style="color:orange"> Uporedni prikaz pokrivenih linija ("Side By Side Comparison")</span> - sadrži linije pokrivene prvim testom i do njih linije pokrivene drugim testom zarad lašeg vizuelnog poređenja. Kolone su sledeće
  - `Line number` - broj linije u izvornoj datoteci
  - `<test1_name>` - linija izvornog koda koja može biti obojena
    - zeleno - ukoliko prvi test pokriva liniju
    - belo (ne obojena) - inače 
  -  `Line number` - još jednom broj linije u izvornoj datoteci
  - `<test2_name>` - linija izvornog koda koja može biti obojena
    - zeleno - ukoliko drugi test pokriva liniju
    - belo (ne obojena) - inače

## Upotreba

```
python3 TestCodeCoverage.py [-h] [--object-path object_path] source_file test1 test2 coverage_dest command [command_arg [command_arg ...]]
```
### Obavezni argumenti
`source_file` - putanja do izvorne datoteke

`test1` - putanja do datoteke sa kodom prvog testa

`test2` - putanja do datoteke sa kodom drugog testa

`coverage_dest` - direktorijum u kojem će biti smeštene izlazne datoteke (gcno/gcda datoteke, json dtoteke, html prikaz)

`command` - željena komanda za pokretanje testova, nakon čega se može naći nula ili više argumenata komande (`command_arg`) zadatih bez minusa ispred (minusevi se dodaju naknadno u kodu)   
format pokretanja komande iz koda je sledeći   
`command test1 -command_arg -command_arg ...`   
ukoliko je jedan od argumenata komande opcija `o` sledećem u nizu argumenata neće biti dodat minus kako ime izlazne datoteke komande ne bi sadržalo minus na početku 

### Opcioni argumenti
`-h`, `--help` - prikaz uputstva za korišćenje

`--object-path` - opcija koja se navodi ukoliko se objektna datoteka (a samim tim i gcno/gcda datoteke) nalaze u razlučitom direktorijumu od direktorijuma u kojem je izvorna daotetka, nakon ove opcije se navodi `object_path` koji predstavlja putanju do direktorijuma objekte datoteke

## Zavisnosti

Za generisanje html prikaza korišćen je paket [Airium](https://pypi.org/project/airium/). Paket je moguće instalirati pozivom komande
```bash
pip install airium
```

