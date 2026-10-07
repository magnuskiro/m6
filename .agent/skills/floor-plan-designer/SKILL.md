---
name: floor-plan-designer
description: Use when designing floor plans, evaluating room layouts, creating space programs, conducting test-fit feasibility studies, or generating 2D SVG/Draw.io architectural layouts for houses and renovations.
---

# Floor Plan & Space Planning Designer

Bruk denne ferdigheten til å utvikle romprogrammer, gjennomføre arkitektoniske mulighetsstudier (test-fit), optimalisere sirkulasjon og sonering, samt generere teknisk presise 2D-plantegninger (SVG eller Draw.io).

Ferdigheten forener arkitektfaglig metodikk fra **AlpacaLabs Architecture Studio** (romprogrammering, feasibility, compliance-språk) med standardiserte konvensjoner for plantegninger og norsk byggeskikk ([`tek17-compliance-checker`](../tek17-compliance-checker/SKILL.md)).

---

## 1. Arkitektonisk Arbeidsflyt (Faser)

Følg alltid denne rekkefølgen ved utarbeidelse av nye eller reviderte planløsninger:

```
[1. Romprogram & Behov] ➔ [2. Test-Fit & Volum] ➔ [3. Sonering & Flyt] ➔ [4. 2D Drafting (SVG/Draw.io)] ➔ [5. TEK17 / Reguleringssjekk]
```

1. **Romprogram (Space Programming):** Kartlegg brukernes funksjonskrav, romtyper, nettoareal ($m^2$) og sirkulasjonsfaktor.
2. **Test-Fit Feasibility:** Undersøk om ønsket program lar seg realisere innenfor gitt yttervegg-geometri, bæresystem (f.eks. ståldragere/HEB) og sjakter.
3. **Sonering & Sirkulasjon:** Organiser rommene i 4 soner (ankomst, felles, privat, service) med logiske bevegelseslinjer.
4. **Plantegning Drafting:** Generer en målsatt 2D-vektortegning (SVG eller Draw.io) med standardiserte veggtykkelser, dørslag, vinduer og møblerbarhet.
5. **Kryssvalidering mot TEK17 & Kommuneplan:** Verifiser dagslysflater ($\ge 10\,\%$), takhøyder, rømningsveier, brannceller og %BYA.

---

## 2. Romprogram & Arealberegning (Space Programming)

Bygg alltid et strukturert romprogram med eksplisitt matematikk for å forhindre arealavvik og urealistiske forventninger:

### Standard Arealfordeling
* **Netto romareal (NRA):** Summen av alle faktiske oppholdsrom og bruksrom.
* **Sirkulasjonsareal:** Gang, trapper og korridorer. Standard boligtillegg er **10–15 %** av netto romareal.
* **Bruksareal (BRA):** Areal innenfor omsluttende yttervegger (NRA + sirkulasjon + innvendige vegger).
* **Konstruksjonsfaktor:** Veggtykkelse tar typisk **8–12 %** av bruttoarealet (BTA) i isolerte trehus.

### Mal for Romprogram-tabell

| Romtype | Sone | Mål (B × L) | Areal ($m^2$) | Minstekrav & Funksjon | Møbleringskrav |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Entré / Hall** | Ankomst | $2.2 \times 3.0\text{ m}$ | $6.6\text{ m}^2$ | Garderobeplass $1.2\text{ m}$, speil | Sittebenk, sko-/jakkegarderobe |
| **Stue / Spisestue** | Sosial/Felles | $4.5 \times 7.5\text{ m}$ | $33.8\text{ m}^2$ | Store lysflater, utsikt | Sofa, TV-vegg, spisebord (8 pers) |
| **Kjøkken** | Sosial/Felles | $3.6 \times 4.0\text{ m}$ | $14.4\text{ m}^2$ | Arbeidstrekant (vask, komfyr, kjøl) | Kjøkkenøy, høyskap, $60\text{ cm}$ benker |
| **Hovedsoverom** | Privat | $3.2 \times 4.2\text{ m}$ | $13.4\text{ m}^2$ | Plass til dobbeltseng m/gang rundt | Seng $180\times 200$, $2\times 60\text{ cm}$ skap |
| **Soverom 2** | Privat | $2.6 \times 3.5\text{ m}$ | $9.1\text{ m}^2$ | Rømningsvindu, dagslys $\ge 10\,\%$ | Seng $120\times 200$, skrivebord |
| **Hovedbad** | Privat/Service | $2.4 \times 3.0\text{ m}$ | $7.2\text{ m}^2$ | Snuareal $1.5\text{ m}$ sirkel, fall mot sluk | $90\times 90$ dusj, $120\text{ cm}$ servant, WC |
| **Vaskerom/Teknisk**| Service | $2.0 \times 2.8\text{ m}$ | $5.6\text{ m}^2$ | Varmtvann, ventilasjon, vask/tørk | Maskinsøyle, utslagsvask |
| **Gang / Sirkulasjon**| Sirkulasjon | - | $9.5\text{ m}^2$ | Bredde $\ge 1.0\text{ m}$ (hovedgang $1.2\text{ m}$) | Fri passasje |

> **Trade-off regel:** Hvis ett rom forstørres innenfor et låst bygningsomriss, må det alltid angis eksplisitt hvilket naborom eller sirkulasjonsareal som reduseres tilsvarende.

---

## 3. Test-Fit Feasibility & Romproporsjoner

Et romprogram er ikke gjennomførbart bare fordi arealsummen stemmer. Sjekk disse geometriske tersklene:

1. **Proporsjoner (Dybde vs. Bredde):**
   * Unngå rom med sideforhold smalere enn $1:2.2$.
   * Soverom for dobbeltseng krever en absolutt minste bredde på **$2.40\text{ m}$** (helst $\ge 2.80\text{ m}$) for å gi fri passasje ($\ge 60\text{–}70\text{ cm}$) på begge sider av sengen.
   * Enkeltseng / barnerom krever minste bredde på **$2.10\text{ m}$**.
2. **Passasje- og Sirkulasjonsbredder:**
   * Hovedgang / entré: $\ge 1.20\text{–}1.40\text{ m}$.
   * Sekundærkorridor: $\ge 1.00\text{ m}$ (absolutt minimum $0.90\text{ m}$).
   * Mellom kjøkkenbenk og kjøkkenøy: Minimum **$1.10\text{–}1.20\text{ m}$** for at to personer kan jobbe og skuffer/oppvaskmaskin kan åpnes helt.
3. **Konstruktive Bærelinjer & Sjakter:**
   * Identifiser bærevegger og ståldragere (f.eks. **HEB 220**). Bærende spenn bør normalt ikke overstige $4.5\text{–}6.0\text{ m}$ i trekonstruksjoner uten understøttelse eller stål.
   * Plasser våtrom (bad, vaskerom, kjøkken) rygg-mot-rygg eller vertikalt over hverandre for å samle rørføringer og avløpsstammer.

---

## 4. Sonering & Arkitektonisk Flyt

Plasser rommene etter de 4 funksjonelle sonene:

1. **Ankomstsone (Offentlig / Semi-offentlig):**
   * Vindfang, entré, gjestetoalett, garderobe for yttertøy og sko.
   * Direkte adkomst uten innsyn til private soverom.
2. **Sosial Sone (Felles / Dagssone):**
   * Stue, spisestue og kjøkken.
   * Optimaliseres mot syd og vest for maksimalt dagslys og kveldssol.
   * Åpen eller halvåpen kontakt mellom kjøkken og spiseplass.
3. **Privat Sone (Natt / Hvile):**
   * Soverom, walk-in closet, hovedbad.
   * Skjermet fra stue/inngangsparti.
   * Soverom plasseres gjerne mot nord eller øst for kjøligere temperatur og morgensol.
4. **Servicesone (Teknisk / Støtende):**
   * Vaskerom, teknisk rom, bod, matbod.
   * Bør fungere som en **akustisk buffersone** mellom oppholdsrom og støyende kilder (som garasje, tekniske installasjoner eller nabo).

---

## 5. Målestokk og Konvensjoner for 2D Plantegning (SVG / Draw.io)

Bruk faste målestokker og stylingregler ved generering av plantegninger:

### Målestokk & Måleenheter
* **Standard SVG / Draw.io-skala:** $1\text{ px} = 1\text{ cm}$ (dvs. $100\text{ px} = 1\text{ meter}$).
* **Yttervegger:** Tykkelse **$20\text{–}35\text{ px}$** ($20\text{–}35\text{ cm}$ isolert vegg). Fylles med mørk grå eller diagonal skravur.
* **Innervegger:** Tykkelse **$10\text{–}15\text{ px}$** ($10\text{–}15\text{ cm}$ stendervegg). Fylles med nøytral grå eller sort strek.
* **Dører:** Lysåpning **$80\text{–}90\text{ px}$**. Tegnes med åpen dørfløy ($90^\circ$ vinkel) og en stiplet kvartsirkelbue som indikerer dørslag og svingradius.
* **Vinduer:** Tegnes i yttervegg som tre parallelle linjer (glass + karm) eller hvit utsparing med dobbel blå/grå strek.
* **Møbler & Utstyr (Stensiler i målestokk):**
  * Dobbeltseng: $180 \times 200\text{ px}$
  * Enkeltseng: $90 \times 200\text{ px}$
  * Garderobeskap: Dybde $60\text{ px}$, bredde $60\text{–}180\text{ px}$
  * Kjøkkenbenk: Dybde $60\text{ px}$
  * Spisebord: $90 \times 180\text{ px}$ (6 pers) eller $100 \times 240\text{ px}$ (8–10 pers)
  * Toalett: $40 \times 65\text{ px}$
  * Dusjnisje: $90 \times 90\text{ px}$

### Eksempel: Frittstående SVG-Plantegning (Struktur)

Ved leveranse av plantegninger som SVG i Markdown eller som HTML-visning, bruk standard SVG-komponenter:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 800" width="100%" height="auto" style="background:#fcfbf9; font-family:sans-serif;">
  <defs>
    <pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse">
      <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#ebe8e1" stroke-width="1"/>
    </pattern>
  </defs>
  
  <!-- 1. Bakgrunnsnett (100px = 1m rutenett) -->
  <rect width="100%" height="100%" fill="url(#grid)" />

  <!-- 2. Romsoner & Areal-fyll -->
  <rect x="100" y="100" width="400" height="500" fill="#f4f6f8" stroke="none" />
  <text x="300" y="320" font-size="16" font-weight="bold" text-anchor="middle" fill="#2d3748">STUE / KJØKKEN</text>
  <text x="300" y="345" font-size="13" text-anchor="middle" fill="#718096">20.0 m² (4.0m × 5.0m)</text>

  <!-- 3. Yttervegger (30px / 30cm) -->
  <path d="M 85 85 L 915 85 L 915 715 L 85 715 Z" fill="none" stroke="#2d3748" stroke-width="30" stroke-linejoin="miter"/>

  <!-- 4. Innervegger (12px / 12cm) -->
  <line x1="500" y1="100" x2="500" y2="700" stroke="#4a5568" stroke-width="12" />

  <!-- 5. Døråpning med dørslag (90cm) -->
  <g transform="translate(500, 250)">
    <!-- Dørblad i 90 grader -->
    <line x1="0" y1="0" x2="0" y2="90" stroke="#a0aec0" stroke-width="3" />
    <!-- Svingradius bue -->
    <path d="M 0 90 A 90 90 0 0 1 90 0" fill="none" stroke="#cbd5e0" stroke-dasharray="4,4" stroke-width="1.5" />
  </g>

  <!-- 6. Vindu (Dobbel glasslinje) -->
  <line x1="200" y1="85" x2="350" y2="85" stroke="#3182ce" stroke-width="8" />
  <text x="275" y="65" font-size="11" text-anchor="middle" fill="#4a5568">150 × 120 (Lysåpning)</text>

  <!-- 7. Målestokk & Nordpil -->
  <path d="M 920 150 L 930 110 L 940 150 Z" fill="#2d3748" />
  <text x="930" y="100" font-size="14" font-weight="bold" text-anchor="middle">N</text>
  <line x1="820" y1="750" x2="920" y2="750" stroke="#2d3748" stroke-width="3" />
  <text x="870" y="770" font-size="11" text-anchor="middle">1 Meter</text>
</svg>
```

---

## 6. Integrasjon mot TEK17 & Reguleringskrav

Enhver foreslått planløsning må kryssjekkes mot prosjektets standardkrav:

1. **Dagslyskontroll ([`tek17-compliance-checker`](../tek17-compliance-checker/SKILL.md) § 13-7):**
   * Oppholdsrom (stue, kjøkken, soverom) skal ha tilstrekkelig dagslys.
   * Beregningsregel: Effektiv glassflate i fasade skal utgjøre **minimum 10 % av rommets bruksareal**.
2. **Romhøyde (§ 13-4):**
   * Minimum **$2.40\text{ m}$** fri takhøyde i rom for varig opphold.
3. **Rømningsveier (§ 11-12, § 11-14):**
   * Hvert soverom må ha tilgang til rømningsvei (dør direkte ut på terreng eller godkjent rømningsvindu).
   * Rømningsvindu: Fri lysåpning med sum av høyde + bredde $\ge 1.50\text{ m}$ (høyde min. $0.60\text{ m}$, bredde min. $0.50\text{ m}$).
4. **Brannskille (§ 11-8):**
   * Skillevegg mot integrert garasje eller sekundærleilighet skal utgjøre branncelle i klasse **EI 60**.
   * Bærende ståldrager (f.eks. HEB 220) skal brannisoleres til **R 60** (f.eks. $2\times 13\text{ mm}$ Protect F).
5. **Tomteutnyttelse ([`muni-zoning-analyzer`](../muni-zoning-analyzer/SKILL.md)):**
   * Sjekk at samlet bebygd areal etter tilbygg eller utvidelse ikke overskrider tillatt **%BYA** (f.eks. maks 25 % i Tønsberg).
   * Hold minimum **$4.0\text{ m}$** avstand til nabogrense.

---

## 7. Arkitektonisk Språkbruk & Forbehold (Professional Disclaimer)

I tråd med profesjonell arkitektpraksis (fra AlpacaLabs-retningslinjene) skal vurderinger formuleres presist:

* **Språkstil:**
  * Skriv: *"Basert på fremlagt skisse fremstår planløsningen konsistent med TEK17 § 13-7 (dagslys)..."*
  * Unngå: *"Dette oppfyller loven garantert"* eller *"Planen er 100 % feilfri"*.
  * Tydeliggjør alltid skillet mellom **brukerens designønsker** og **konstruktive/forskriftsmessige rammer**.

Avslutt formelle vurderingsrapporter eller plananalyser med standard forbeholdsnotat:

> **Disclaimer:** Dette er et AI-assistert skisse- og forprosjekt til bruk for overordnet planlegging. Endelige konstruksjonstegninger, bæreberegninger og dispensasjonssøknader må verifiseres og godkjennes av ansvarlig prosjekterende fagperson (arkitekt / rådgivende ingeniør) før innsending til kommunal byggesaksbehandling eller byggestart.
