# CARE Score

<!-- Generated from definitions/care.yaml; do not edit directly. -->

The CARE Principles reflect the crucial role of data in advancing Indigenous innovation and self-determination. They ensure that data movements like the open data movement, whatever they’re advocating and pursuing, respect the people and purpose behind the data.

The CARE Principles complement the existing [FAIR](https://www.go-fair.org/fair-principles/) Principles, which require data to be findable, accessible, interoperable and reusable. While the FAIR Principles are about making it easier to share and reuse data, the CARE Principles ensure that data is used ethically.

Read more on [GIDA](https://www.gida-global.org/careprinciples)'s page about the CARE principles.

Definition version: `0.5.0`

## Score summary

| Score | Description | Maximum | Depends on |
|---|---|---:|---|
| C | Data ecosystems shall be designed and function in ways that enable Indigenous Peoples to derive benefit from the data. | 10 | — |
| C1 | For inclusive development and innovation | 3 | — |
| C2 | For improved government and citizen engagement | 4 | C1 |
| C3 | For inclusive development and innovation | 3 | C2 |
| A | Indigenous Peoples' rights and interests in Indigenous data must be recognised and their authority to control such data be empowered. | 7 | — |
| A1 | Recognizing rights and interests | 3 | — |
| A2 | Data for governance | 2 | A1 |
| A3 | Governance of data | 2 | A2 |
| R | Those working with Indigenous data have a responsibility to share how those data are used to support Indigenous Peoples' self-determination and collective benefit. | 11 | — |
| R1 | For positive relationships | 3 | — |
| R2 | For expanding capability and capacity | 2 | R1 |
| R3 | For Indigenous languages and worldviews | 6 | C3, R1 |
| E | Indigenous Peoples' rights and wellbeing should be the primary concern at all stages of the data life cycle and across the data ecosystem. | 8 | — |
| E1 | For minimising harm and maximising benefit | 3 | A1, C3 |
| E2 | For justice | 3 | A3, E1 |
| E3 | For future use | 2 | E1, R3 |

## C — Collective Benefit

Data ecosystems shall be designed and function in ways that enable Indigenous Peoples to derive benefit from the data.

Maximum score: **10**

### C1 — C1

For inclusive development and innovation

Maximum score: **3**

Requirements:

1. **Metadata is discoverable (persistently identified)** — 1 point(s)

   ```sparql
   ASK { ?iri ?p ?o }
   ```
2. **The data has been assigned one or more Indigeneity terms** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:keywords ?indigeneity }
   ```
3. **Data has Access Rights described** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:usageInfo ?accessRights }
   ```

### C2 — C2

For improved government and citizen engagement

Maximum score: **4**

Prerequisites:

- c1 = maximum

Requirements:

1. **Metadata is discoverable via the internet (i.e. IRI resolves)** — 1 point(s)
   - The resource IRI must resolve
2. **Data title exists** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:name ?title }
   ```
3. **Data description exists** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:description ?description }
   ```
4. **Custodian (Role) Agent information in database has indigeneity = “Indigenous Persons Organisation” OR “Owned By Indigenous Persons” OR “Run By Indigenous Persons”** — 1 point(s)

   ```sparql
   ASK {
       VALUES ?indigeneity {
           <https://data.idnau.org/pid/vocab/org-indigeneity/run-by-indigenous-persons>
           <https://data.idnau.org/pid/vocab/org-indigeneity/owned-by-indigenous-persons>
           <https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation>
       }
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
           sdo:agent ?agent .
       ?agent sdo:keywords ?indigeneity .
   }
   ```

### C3 — C3

For inclusive development and innovation

Maximum score: **3**

Prerequisites:

- c2 = maximum

Requirements:

1. **License and Rights have been identified and Agent with role “Rights Holder” has been identified** — 2 point(s)

   ```sparql
   ASK {
       ?iri sdo:license ?license ;
           sdo:copyrightNotice ?rights ;
           prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/rightsHolder> .
   }
   ```
2. **Data distribution information exists** — 1 point(s)

   ```sparql
   ASK {
       ?iri sdo:distribution ?distribution .
       ?distribution sdo:contentUrl ?url .
   }
   ```

## A — Authority to Control

Indigenous Peoples' rights and interests in Indigenous data must be recognised and their authority to control such data be empowered.

Maximum score: **7**

### A1 — A1

Recognizing rights and interests

Maximum score: **3**

Requirements:

1. **Custodian (Role) Agent information in database has indigeneity = “Indigenous Persons Organisation” OR “Owned By Indigenous Persons” OR “Run By Indigenous Persons”** — 1 point(s)

   ```sparql
   ASK {
       VALUES ?indigeneity {
           <https://data.idnau.org/pid/vocab/org-indigeneity/run-by-indigenous-persons>
           <https://data.idnau.org/pid/vocab/org-indigeneity/owned-by-indigenous-persons>
           <https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation>
       }
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
           sdo:agent ?agent .
       ?agent sdo:keywords ?indigeneity .
   }
   ```
2. **License and Rights have been identified and Agent with role “Rights Holder” has been identified** — 2 point(s)

   ```sparql
   ASK {
       ?iri sdo:license ?license ;
           sdo:copyrightNotice ?rights ;
           prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/rightsHolder> .
   }
   ```

### A2 — A2

Data for governance

Maximum score: **2**

Prerequisites:

- a1 = maximum

Requirements:

1. **The URL link to, OR text description of, an Indigenous Data Governance Framework or Indigenous Data Committee is identified in the metadata record** — 1 point(s)

   ```sparql
   ASK {
       ?iri prov:wasInfluencedBy ?idgf .
       ?idgf sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> ;
           sdo:url|sdo:description ?o .
   }
   ```
2. **Agent which has indicated the Indigenous Data Governance Framework has Role = Custodian** — 1 point(s)

   ```sparql
   ASK {
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
           sdo:agent ?agent .
       ?agent prov:contributed ?idgf .
       ?idgf sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> .
   }
   ```

### A3 — A3

Governance of data

Maximum score: **2**

Prerequisites:

- a2 = maximum

Requirements:

1. **Indigeneity = By Indigenous People** — 1 point(s)

   ```sparql
   ASK {
       ?iri sdo:keywords <https://data.idnau.org/pid/vocab/indigeneity/by-indigenous-people> .
   }
   ```
2. **URL link to an Indigenous Data Governance Framework or Indigenous Data Committee is identified in the metadata record** — 1 point(s)

   ```sparql
   ASK {
       ?iri prov:wasInfluencedBy ?idgf .
       ?idgf sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> ;
           sdo:url ?url .
   }
   ```

## R — Responsibility

Those working with Indigenous data have a responsibility to share how those data are used to support Indigenous Peoples' self-determination and collective benefit.

Maximum score: **11**

### R1 — R1

For positive relationships

Maximum score: **3**

Requirements:

1. **Indigeneity = By Indigenous People** — 1 point(s)

   ```sparql
   ASK {
       ?iri sdo:keywords <https://data.idnau.org/pid/vocab/indigeneity/by-indigenous-people> .
   }
   ```
2. **Custodian (Role) Agent information in database has indigeneity = “Indigenous Persons Organisation” OR “Owned By Indigenous Persons” OR “Run By Indigenous Persons”** — 2 point(s)

   ```sparql
   ASK {
       VALUES ?indigeneity {
           <https://data.idnau.org/pid/vocab/org-indigeneity/run-by-indigenous-persons>
           <https://data.idnau.org/pid/vocab/org-indigeneity/owned-by-indigenous-persons>
           <https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation>
       }
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
           sdo:agent ?agent .
       ?agent sdo:keywords ?indigeneity .
   }
   ```

### R2 — R2

For expanding capability and capacity

Maximum score: **2**

Prerequisites:

- r1 = maximum

Requirements:

1. **Custodian (Role) Agent has identified a resolvable URL link to, OR text description of, an Indigenous Data Governance Framework or Indigenous Data Committee in the metadata record** — 2 point(s)
   - Every `url` result must resolve

   ```sparql
   SELECT ?url
   WHERE {
     ?iri prov:qualifiedAttribution ?agentRole .
     ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
         sdo:agent ?agent .
     ?agent prov:contributed ?idgf .
     ?idgf sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> ;
         sdo:url ?url .
   }
   ```

   ```sparql
   ASK {
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
           sdo:agent ?agent .
       ?agent prov:contributed ?idgf .
       ?idgf sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> ;
           sdo:url|sdo:description ?o .
   }
   ```

### R3 — R3

For Indigenous languages and worldviews

Maximum score: **6**

Prerequisites:

- r1 = maximum

Requirements:

1. **C3 has scored fully** — 2 point(s)
   - Condition: c3 = maximum
2. **Custodian (Role) Agent has identified a resolvable URL link to, OR text description of, an Indigenous Data Governance Framework or Indigenous Data Committee in the metadata record** — 1 point(s)
   - Every `url` result must resolve

   ```sparql
   SELECT ?url
   WHERE {
     ?iri prov:qualifiedAttribution ?agentRole .
     ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
         sdo:agent ?agent .
     ?agent prov:contributed ?idgf .
     ?idgf sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> ;
         sdo:url ?url .
   }
   ```

   ```sparql
   ASK {
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
           sdo:agent ?agent .
       ?agent prov:contributed ?idgf .
       ?idgf sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> ;
           sdo:url ?url .
   }
   ```
3. **Spatial geometry has been identified** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:spatialCoverage ?spatial }
   ```
4. **At least two themes have been selected** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:keywords ?theme }
   ```
5. **At least one language from AustLang has been selected** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:inLanguage ?austlang }
   ```

## E — Ethics

Indigenous Peoples' rights and wellbeing should be the primary concern at all stages of the data life cycle and across the data ecosystem.

Maximum score: **8**

### E1 — E1

For minimising harm and maximising benefit

Maximum score: **3**

Requirements:

1. **C3 has scored fully** — 2 point(s)
   - Condition: c3 = maximum
2. **A1 has scored fully** — 1 point(s)
   - Condition: a1 = maximum

### E2 — E2

For justice

Maximum score: **3**

Prerequisites:

- e1 = maximum

Requirements:

1. **A3 has scored fully** — 2 point(s)
   - Condition: a3 = maximum
2. **Custodian (Role) Agent’s information in database has ONLY Indigeneity = “Indigenous Persons Organisation”** — 1 point(s)

   ```sparql
   ASK {
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
           sdo:agent ?agent .
       ?agent sdo:keywords <https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation> .
   }
   ```

### E3 — E3

For future use

Maximum score: **2**

Prerequisites:

- e1 = maximum
- r3 = maximum

Requirements:

1. **The date that the data was created and modified are identified** — 1 point(s)

   ```sparql
   ASK {
       ?iri sdo:dateCreated ?created ;
           sdo:dateModified ?modified .
   }
   ```
2. **Name AND point of contact (Email OR Phone) is identified** — 1 point(s)

   ```sparql
   ASK {
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/pointOfContact> ;
           sdo:agent ?agent .
       ?agent sdo:name ?name .
   }
   ```
