# Verbesserte Version
* Serielle Schnittstelle ist richtig konfiguriert
  * 2400 Baud, Gerade Parität (Fehlt im original Projekt noch immer)
  * Timeout auf 30 Sekunden
  * Serielle Schnittstelle wird exklusiv verwendet
* Es ist sichergestellt, dass nur vollständig empfangene Packete decodiert werden.
* Synchronisiert sich mit dem Stromzähler, so dass alle Packete lückenlos empfangen werden.
* Erkennt diverse Fehler
  * Falscher Schlüssel
  * Leere Nachricht vom Stromzähler

# Ursprünglicher Autor
https://www.michaelreitbauer.at/blog


# SmartMeterEVN
Dieses Projekt ermöglicht es den Smartmeter der EVN (Netz Niederösterreich) über die Kundenschnittstelle auszulesen.
Smart Meter werden von der Netz NÖ GmbH eingebaut, auf Basis der gesetzlichen Forderungen.

## Getting Started
### Voraussetzungen Hardware


* Passwort für die Kundenschnittstelle
  * Alle folgenden Informationen sind aus dem Folder der EVN. (https://www.netz-noe.at/Download-(1)/Smart-Meter/218_9_SmartMeter_Kundenschnittstelle_lektoriert_14.aspx)
  * Wenn bereits ein Smart Meter in der Kundenanlage eingebaut ist, kann hier das der Schlüssel angefordert werden: smartmeter@netz-noe.at
    * Kundennummer oder Vertragskontonummer
    * Zählernummer
    * Handynummer




### Zähler Hersteller
* Kaifa Drehstromzähler MA309


## License

This project is licensed under the GNU General Public License v3.0 License - see the LICENSE.md file for details
