# Elokuvasuositukset
Tarkoituksena, että käyttäjät voivat lisätä omia elokuvasuosituksia sekä arvostella/kommentoida muiden lisäämiä elokuvasuosituksia.


## Toteutetut toiminnallisuudet:
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan elokuvasuosituksia.
- Käyttäjä näkee sovellukseen lisätyt elokuvat.
- Käyttäjä pystyy etsimään elokuvia/suosituksia hakusanalla.- Sovelluksessa on käyttäjäsivut, jotka näyttävät käyttäjän lisäämät elokuvat ja niiden määrän.
- Käyttäjä pystyy valitsemaan suosittelemalleen elokuvalle yhden tai useamman luokan (genre ja/tai ikäraja).
- Käyttäjä pystyy lähettämään toisen käyttäjän suosittelemaan elokuvaan kommentteja (arvostelu, arvosana)
- Käyttäjä pystyy lisäämään kuvia lisättyihin elokuviin
- Virheviestien näyttäminen yhtenäiseksi
- Virheviestit näytetään samalla sivulla, missä virhe tapahtuu
- Tunnuksen luonnin jälkeen ohjaus takaisin etusivulle/kirjautumissivulle

## Toteuttamattomat toiminnallisuudet:
- Jokaisesta elokuvasta näytetään keskimääräinen arvosana ja kommentit
- Kuvia voi lisätä jo elokuvan luonti/lisäämisvaiheessa
- Profiilikuvan lisääminen käyttäjälle
- Ulkoasu kaikille sivuille


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
