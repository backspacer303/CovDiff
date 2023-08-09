# *CovDiff* - alat za generisanje i prikaz razlika u pokrivenosti koda testovima 

Alat generiše html stranice sa izveštajima o pokrivenosti kod celog build-a nakon pokretanja dva testa. Izveštaji se generišu za svaku kompilacionu jedinicu posebno. Na stranicama se nalaze različite uporedne informacije o pokrivenosti koda testovima pa je tako moguće videti u kojim datotekama i na kojim linijama postoje razlike.

## Opis 

Klasa `ProjectCodeCoverage` reprezentuje izveštaj o pokrivenosti koda celog build-a tj. svake kompilacione jedinice nakon pokretanja jednog testa i obavlje sledeće operacije:
- čisti build direktorijum od prethodnih korišćenja koda odnosno briše sve `.gcda` datoteke koje postoje
- pokreće zadati test zadatom komandom nakon čega se formiraju `.gcda` datoteke
- radi rekurzivni obilazak zadatog build direktorijuma i za svaku pronađenu `.gcda` datoteku:

  - pokreće `gcov` alat i generiše izveštaj o pokrivenosti koda u `json` formatu
  - parsira izveštaj iz `json` datoteke i pamti rezultate za odgovarajuću kompilacionu jedinicu

Klasa `HtmlReport` koristi informacije o pokrivenosti kompilacionih jedinica iz prethodne klase kako bi generisala html izveštaj o pokrivenosti koda testovima. U okviru ove klase generišu se sledeći prikazi:
- Početna strana na kojoj se nalazi:
  - **<span style="color:orange"> Izveštaj "Mini report" </span>** - sadrži sumarne informacije o pokrivenosti build-a testom, za oba testa, sa sledećim informacijama
    -  broj obrađenih `.gcda` datoteka
    -  ukupan broj obrađenih izveštaja (ima ih više od broja gcda datoteka jer jedna gcda datoteka može sadržati više od jednog izveštaja)
    -  broj jedinstvenih kompilacionih jedinica pogođenih testom (bez komilacionih jedinica sa 0% pokrivenosti)
    -  ukupan broj obrađenih jedinstvenih kompilacionih jedinica (sa komilacionim jedinicama sa 0% pokrivenosti) 
    -  ekstenzije datoteka kompilacionih jedinica pogođenih testom
    -  brojač za svaku ekstenziju
  -  **<span style="color:orange"> Listu sa svim kompilacionin jedinicama pogođenim nekim od testova </span>** koja sadrži sledeće kolone
     -  naziv kompilacione jedinice koji je ujedno link sa kojim je moguće otići na stranicu sa detaljnim izveštajem 
     -  procentualnu pokrivenost kompilacione jedinice prvim testom, pored koga može stajati oznaka `diff` što znači da postoje linije kompilacione jedinice pokrivene prvim testom a da nisu pokrivene drugim testom
     -  procentualnu pokrivenost kompilacione jedinice drugim testom, pored koga može stajati oznaka `diff` što znači da postoje linije kompilacione jedinice pokrivene drugim testom a da nisu pokrivene prvim testom
     -  polje za pretragu kompilacionih jedinica
     
  -  **<span style="color:orange"> Listu sa svim kompilacionin jedinicama u kojima postoje razlike u pokrivenosti jednim testom u odnosu na drugi </span>**
     - lista sadrži spisak onih kompilacionih jedinica iz prethodne liste koje imaju makar jednu `diff` oznakau a ima iste kolone kao prethodna lista

- Stranice za svaku pojedinačnu kompilacionu jedinicu na kojima se nalaze:
  
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
  - **<span style="color:orange"> Izveštaj o razlikama ("Coverage Diff") </span>** - sadrži linije koje su pokrivene prvim a nisu pokrivene drugim testom i obrnuto, linije koje su pokrivene drugim a nisu pokrivene prvim testom. Kolone su sledće
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
    -  `Line number` - još jednom broj linije u izvornoj datoteci
    - `<test2_name>` - linija izvornog koda koja može biti obojena
      - zeleno - ukoliko drugi test pokriva liniju
      - belo (ne obojena) - inače

## Upotreba

```
python3 covdiff.py [-h] 
[--source-file source_file] [--object-path object_path]
directory_path test1 test2 coverage_dest 
command [command_arg [command_arg ...]]
```
### Obavezni argumenti
`directory_path` - putanja do build direktorijuma

`test1` - putanja do datoteke sa kodom prvog testa ili ime prvog testa

`test2` - putanja do datoteke sa kodom drugog testa ili ime drugog

`coverage_dest` - direktorijum u kojem će biti smešteni html prikazi

`command` - željena komanda za pokretanje testova, nakon čega se može naći nula ili više argumenata komande (`command_arg`) zadatih bez minusa ispred (minusevi se dodaju naknadno u kodu)   
format pokretanja komande iz koda je sledeći   
`command test1 -command_arg -command_arg ...`   
ukoliko je jedan od argumenata komande opcija `o` sledećem u nizu argumenata neće biti dodat minus kako ime izlazne datoteke komande ne bi sadržalo minus na početku 

### Opcioni argumenti
`-h`, `--help` - prikaz uputstva za korišćenje

`--source-file` - opcija kojom korisnim može zadati ime kompilacione jedinice od interesa, u tom slučaju se generiše izveštaj samo za nju

`--object-path` - opcija koja se mođe navesti uz `--source-file` a koja označava putanju do objektne datoteke kompilacione jedinice od interesa (a samim tim i gcno/gcda datoteke). Tada se ne vrši rekurzivni obilazak celog build direktorijuma već se direktno pristupa zadatoj lokaciji pa se i rezultat dobija brže

### Primer pokretanja
Primer 1 - Pokretanje alata ukoliko su testovi sami po sebi izvršne datoteke
```bash
python3 covdiff.py ~/Desktop/lib_build/ ~/Desktop/lib_test/test1 ~/Desktop/lib_test/test2 ./results ./
```
Primer 2 - Pokretanje alata nad projektom *LLVM*
```bash
python3 covdiff.py ~/Desktop/ClangCoverageBuild ./bbi-70612_typed.ll ./bbi-70612_typed_no_llvmdbg.ll ./results ~/Desktop/ClangCoverageBuild/bin/opt opaque-pointers=0 O2 S o opt_out.ll
```
<br>

---
> Rezultati pokretanja alata nad projektom *LLVM* komandom iz primera 2, mogu se preuzeti na [ovoj adresi](https://drive.google.com/drive/folders/1vGo_d2THwaoFHrfzuAzkI46bw06fiHqn?usp=share_link). Tu su dostupni i izvorni kodovi testova koji su tom prilikom pokrenuti.
---

<br>

## Zavisnosti

Za generisanje html prikaza korišćen je paket [Airium](https://pypi.org/project/airium/). Paket je moguće instalirati pozivom komande

```bash
pip install airium
```
Aplikacija koristi `GCC gcov` alat za generisanje izveštaja o pokrivenosti koda pa je potrebno imati taj alat instaliran na sistemu.

Aplikacija pretpostavlja da je build direktorijum dobijen uz zadate opcije `-ftest-coverage` i `-fprofile-arcs` pri prevođenju izvornog koda. Ove opcije je moguće zadati npr. `GCC` kompajleru.
