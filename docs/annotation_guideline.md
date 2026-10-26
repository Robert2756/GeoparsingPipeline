# Annotation guideline v1

Goal: mark every geographic place name (toponym) in the text.

## Annotate
- Countries, regions/states/provinces/counties, cities/towns/villages,
  continents, islands, mountains, rivers, lakes, seas/oceans.
- Informal named regions (Middle East, East Coast): annotate, flag |unsure.
- Historical places (Sowjetunion): annotate, flag |hist.

## Span rules
- Mark only the name: no article, no preposition, no possessive 's.
  "Pakistan's headquarters" -> [[Pakistan]]'s headquarters
- Keep generic words that belong to the name: [[Lake Victoria]], [[DeKalb County]].
- Hierarchies get separate spans: [[Tupelo]], [[Mississippi]].
- No overlapping or nested spans.

## Do NOT annotate
- Demonyms and adjectives: pakistanischen, thailändischen, Czech, German.
- Place names inside names of organizations, events, teams, works, people:
  Cabinet of South Africa, Minnesota Vikings, Bank of England, EU.
- Streets, buildings, stations, stadiums, airports.
- Fictional places.
- Words that do not reference the place but the name itself: similarity between the names of  "Swaziland" and "Switzerland".
- Place names inside phrases: "Viva España!" (Long live Spain!)

## Flags (after a pipe inside the brackets)
- |fig    name stands for a government, team, or population, not the territory
          ("Berlin entschied")
- |unsure you are not sure the span follows these rules
- |hist   historical entity
- Combine with commas: [[Berlin|fig,unsure]]

## Status per line
- + reviewed (also if the text contains no place name!)
- x excluded (junk, boilerplate, not a sentence)
- - not yet reviewed
Never edit text outside the [[ ]] markup.