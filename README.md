# Geo-Pipeline

Dieses Projekt evaluiert ein lokales Ollama Model (llama3.1:8b), geografische Orte aus Texten zu filtern. Um die Performance zu bewerten, werden die Resultate gegen einen eigenen menschlich gelabelten Datensatz verglichen.

## Dataset Übersicht

Artikel wurden hierbei anhand von Paragraphen getrennt und für jeden Paragraphen formen drei zufällige Sätze ein Dokument.

<img src="docs/docMining.png" alt="Document Fetching and Labeling Pipeline" width="500">

Es werden zwei Datensätze in vier Zellen verwendet:

- wikimedia/wikipedia in [Deutsch, Englisch]
- Fumika/Wikinews-multilingual [Deutsch, Englisch]

## Händisches Labeling

Diese vier Zellen wurden händisch gelabelt (40 Dokumente pro Zelle):

| Dataset | Documents | Excluded | Gold Spans | No Place | Figurative | Unsure | Historical |
|:--|--:|--:|--:|--:|--:|--:|--:|
| de/news | 40 | 0 | 67 | 16 | 6 | 0 | 0 |
| de/wikipedia | 40 | 0 | 36 | 23 | 8 | 2 | 0 |
| en/news | 40 | 0 | 63 | 18 | 0 | 1 | 0 |
| en/wikipedia | 40 | 0 | 56 | 21 | 7 | 1 | 3 |
| **Total** | **160** | **0** | **222** | **78** | **21** | **4** | **3** |

Mit:
- Gold Spans (Anzahl an gefundenen Orten im Text)
- No Place (Dokumente ohne gefundenen Ort)
- Figurative (Ort gehört zu Regierung, Mannschaft, ...)
- Unsicher über Erfüllung der Kriterien
- Historische Orte

Die Guidelines nach denen händisch gelabelt wurden liegen unter ./docs/annotation_guideline.md

## LLM Prediction

Die Vorhersage des Ollama Models (llama3.1:8b) erfolgt auf zwei verschiedenen Wegen, die verglichen werden. Erstens mit Zugabe von Regeln:

<img src="docs/LLM_Rules.png" alt="LLM Vorhersage" width="500">

Die Regeln spiegeln dabei die händische labeling guideline wieder:

```text
Extract all geographic place names (toponyms) from the text. \
Answer as JSON: {"places": [...]} with each place name exactly as written in the text. \
Use an empty list if there are none.

Rules:
- Include countries, regions, states, provinces, counties, cities, towns, villages, continents, islands, mountains, rivers, lakes, seas and oceans.
- Include informal named regions (Middle East, East Coast) and historical places (Yugoslavia).
- Include short forms such as US or UK when they mean the country.
- Include a country or city that stands for its government, team or population ("Berlin decided", "lost 0:1 against Spain").
- Give only the name: no article, preposition or possessive 's ("Canada's capital" -> "Canada").
- Keep generic words that belong to the name ("Lake Victoria", "Orange County").
- List nested places separately ("Tupelo, Mississippi" -> "Tupelo" and "Mississippi").
- Do NOT include demonyms or adjectives (German, schweizerisch, Czech).
- Do NOT include place names that are part of the name of an organization, party, team, event, work, title or person (Bank of England, Boston Celtics, Washington Irving). The EU is an organization, not a place.
- Do NOT include streets, buildings, stations, stadiums, airports or named facilities such as mines, ranches or hotels.
- Do NOT include currency codes such as US$ or fictional places.
- Do NOT include a word that is only mentioned as a word and not as the place ("Swaziland" and "Switzerland" sound alike).
- Do NOT include place names inside fixed phrases or exclamations ("Viva España!").
- Only list places that are literally written in the text. Never add places that are merely implied.
```

Zweitens, ohne Zugabe von Regeln:

<img src="docs/LLM_NoRules.png" alt="LLM Vorhersage" width="500">

Der Prompt hat nun keine Regeln:

```text
Extract all geographic place names (toponyms) from the text. \
Answer as JSON: {"places": [...]} with each place name exactly as written in the text. \
Use an empty list if there are none.
```


## Evaluation

In der Evaluations-Pipeline werden auf Grundlage der händisch gelabelten Ground Truth, Precision, Recall und F1-Score für jede Zelle und Art des Vergleichs berechnet:

<img src="docs/EvalPipeline.png" alt="Evaluation Pipeline" width="500">

## Ergebnisse Mit Regeln

Bei der Vorhersage des Modells kommt es sechs mal zu einer unendlichen Wiederholung von Orten in der Antwort, diese werden als ungültig gewertet.

### strict (strenger Vergleich)

| Dataset | Documents | Gold Spans | Precision | Recall | F1 |
|:--|--:|--:|--:|--:|--:|
| **All** | **160** | **222** | **0.45** | **0.90** | **0.60** |
| de/news | 40 | 67 | 0.46 | 0.93 | 0.62 |
| de/wikipedia | 40 | 36 | 0.27 | 0.81 | 0.41 |
| en/news | 40 | 63 | 0.54 | 0.87 | 0.67 |
| en/wikipedia | 40 | 56 | 0.54 | 0.96 | 0.69 |

### lenient (nachsichtiger Vergleich)

| Dataset | Documents | Gold Spans | Precision | Recall | F1 |
|:--|--:|--:|--:|--:|--:|
| **All** | **160** | **222** | **0.47** | **0.94** | **0.63** |
| de/news | 40 | 67 | 0.47 | 0.94 | 0.63 |
| de/wikipedia | 40 | 36 | 0.32 | 0.94 | 0.48 |
| en/news | 40 | 63 | 0.55 | 0.89 | 0.68 |
| en/wikipedia | 40 | 56 | 0.56 | 1.00 | 0.72 |

## Ergebnisse Ohne Regeln

Im Gegensatz zum Prompt mit Regeln, kommt es ohne Zugabe von Regeln zu keinen unendlichen Wiederholungen in den Antworten.

### strict (strenger Vergleich)

| Dataset | Documents | Gold Spans | Precision | Recall | F1 |
|:--|--:|--:|--:|--:|--:|
| **All** | **160** | **222** | **0.59** | **0.95** | **0.73** |
| de/news | 40 | 67 | 0.71 | 0.93 | 0.81 |
| de/wikipedia | 40 | 36 | 0.42 | 0.97 | 0.59 |
| en/news | 40 | 63 | 0.65 | 0.97 | 0.78 |
| en/wikipedia | 40 | 56 | 0.56 | 0.96 | 0.71 |

### lenient (nachsichtiger Vergleich)

| Dataset | Documents | Gold Spans | Precision | Recall | F1 |
|:--|--:|--:|--:|--:|--:|
| **All** | **160** | **222** | **0.60** | **0.98** | **0.74** |
| de/news | 40 | 67 | 0.72 | 0.94 | 0.82 |
| de/wikipedia | 40 | 36 | 0.43 | 1.00 | 0.61 |
| en/news | 40 | 63 | 0.66 | 0.98 | 0.79 |
| en/wikipedia | 40 | 56 | 0.58 | 1.00 | 0.73 |

## Auswertung
### Regeln verursachten eine geringere Genauigkeit des Modells.

Der längere Prompt destabilisiert das 8B Modell. Bei Ausgang von ca acht Orten in den sechs Artikeln, welche unendliche Antwortschleifen verursachten, ist das ein großer Faktor für eine geringere Genauigkeit, da die Antwortschleifen als ungültig gewertet werden.

### Hoher Recall, geringe Precision.

Es lässt sich feststellen, dass für alle vier Resultate der Recall tendenziell höher ist, während Precision vergleichsweise niedriger ist. Das bedeutet, dass das 8B Modell relativ verlässlich die richtigen Orte findet, aber auch viele falsche Orte detektiert. Hierbei werden weniger falsche Orte ohne Regeln gefunden, was sich in Teilen auf die Ungültigkeit der Antwortschleifen zurückführen lässt.

### Nachsichtiger Vergleich hat leicht höhere Genauigkeit.

Das war zu erwarten, da der der Nachsichtige Vergleich auch Überschneidungen der Ortsnamen zulässt. Während also beim strengen Vergleich "New York" und "York City" nicht als richtig gewertet werden, ist es beim nachsichtigem Vergleich ein Treffer da sich "York" überschneidet. Das Problem kann hierbei jedoch sein, dass selbst Überschneidungen von nur einem Buchstaben als Treffer gelten, was auch aus Zufall passieren könnte.

### Unterschiede der Datensätze.
Unterschiede in der Anzahl an validen Orten für jede Zelle machen Vergleiche schwierig. Für die de/wikipedia Zelle mit nur 36 validen Orten wird ein Modell, welches sich Orte ausdenkt, stärker betraft in der Precision Metrik, als in de/news, da dort die Wahrscheinlichkeit höher liegt, dass ein Modell mit hohem Recall sich weniger Orte ausdenkt.

### Hypothese für die Regeln.
Die lange Liste an Regeln könnte das kleine 8B Modell überladen und es eventuell aktiv prompten das zu tun was nicht gefordert wird. Diese Vermutung obliegt jedoch Spekulation.

## Beispiele der Modellvorhersagen

### Mit Regeln
Artikel: "de-news-0008"
Truth: "Türkei"
Prediction: "Novemer", "Türkei"

Artikel: "de-news-0015"
Truth: Nothing
Prediction: "Weltall", "Sonnenwind", "Magnetfeld", "Erde", "Magnetosphäre", "Brücken", "Flugzeuglandebahnen", "NASA"

### Ohne Regeln
Artikel: "de-news-0008"
Truth: "Türkei"
Prediction: "Novemer", "Türkei"

Artikel: "de-news-0015"
Truth: Nothing
Prediction: "Weltall", "Erde", "Erde", "Magnetosphäre", "Erde", "NASA"