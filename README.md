# Leffakone
Tarkoituksena, että käyttäjät voivat lisätä elokuvia sekä arvostella sivustolle jo lisättyjä elokuvia.

## Sovelluksen toiminnot:
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan elokuvia.
- Käyttäjä pystyy lisäämään kuvia elokuviinsa.
- Käyttäjä näkee sovellukseen lisätyt elokuvat.
- Käyttäjä pystyy etsimään elokuvia/suosituksia hakusanalla.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät käyttäjän lisäämät elokuvat ja niiden määrän sekä profiilikuvan.
- Käyttäjä pystyy valitsemaan suosittelemalleen elokuvalle yhden tai useamman luokan (genre ja/tai ikäraja).
- Käyttäjä pystyy lähettämään toisen käyttäjän lisäämään elokuvaan arvostelun.
- Jokaisesta elokuvasta näytetään keskimääräinen arvosana ja kommentit.


## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää luokat:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Käynnistä sovellus:

```
$ flask run
```


## Sovelluksen käyttö suurella tietomäärällä
- Elokuvien määrän ollessa 100000 ja arvostelujen määrän ollessa 10000 sovellus toimi suhteellisen hyvin, ainoa sivusto jolla kesti vähän yli sekunnin verran ladata oli Etsi elokuva -sivusto monimutkaisten etsimisvaihtoehtojen takia
- Kaikki sivustot toimivat moitteettomasti kun elokuvien määrä oli 10000 ja arvostelujen määrän ollessa 1000
