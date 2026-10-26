# FAIR Score

<!-- Generated from definitions/fair.yaml; do not edit directly. -->

In 2016, the ‘[FAIR Guiding Principles for scientific data management and stewardship](https://www.nature.com/articles/sdata201618)’ were published in Scientific Data. The authors intended to provide guidelines to improve the **F**indability, **A**ccessibility, **I**nteroperability, and **R**euse of digital assets. The principles emphasise machine-actionability (i.e., the capacity of computational systems to find, access, interoperate, and reuse data with none or minimal human intervention) because humans increasingly rely on computational support to deal with data as a result of the increase in volume, complexity, and creation speed of data.

Read more on the [GO FAIR](https://www.go-fair.org/fair-principles/) website.

Definition version: `0.5.0`

## Score summary

| Score | Description | Maximum | Depends on |
|---|---|---:|---|
| F | Metadata and data should be easy to find for both humans and computers. | 18 | — |
| F1 | (Meta)data are assigned a globally unique and persistent identifier | 5 | — |
| F2 | Data are described with rich metadata | 7 | — |
| F3 | Metadata clearly and explicitly include the identifier of the data they describe | 2 | — |
| F4 | (Meta)data are registered or indexed in a searchable resource | 4 | — |
| A | Once data is found, access information needs to be clearly indicated on the metadata. | 10 | — |
| A1 | (Meta)data are retrievable by their identifier using a standardised communications protocol | 7 | — |
| A1.1 | The protocol is open, free, and universally implementable | 4 | F1 |
| A1.2 | The protocol allows for an authentication and authorisation procedure, where necessary | 3 | F3 |
| A2 | Metadata are accessible, even when the data are no longer available | 3 | — |
| I | The data should be able to be integrated with other data. | 17 | — |
| I1 | (Meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation. | 3 | — |
| I2 | (Meta)data use vocabularies that follow FAIR principles | 9 | F1, F2 |
| I3 | (Meta)data include qualified references to other (meta)data | 5 | F1 |
| R | Metadata and data should be well-described so that they can be replicated and/or combined in different settings. | 12 | — |
| R1 | (Meta)data are richly described with a plurality of accurate and relevant attributes | 12 | — |
| R1.1 | (Meta)data are released with a clear and accessible data usage license | 3 | — |
| R1.2 | (Meta)data are associated with detailed provenance | 6 | — |
| R1.3 | (Meta)data meet domain-relevant community standards | 3 | A1, F3 |

## F — Findable

Metadata and data should be easy to find for both humans and computers.

Maximum score: **18**

### F1 — F1

(Meta)data are assigned a globally unique and persistent identifier

Maximum score: **5**

Requirements:

1. **Metadata has an identifier** — 1 point(s)

   ```sparql
   ASK { ?iri ?p ?o }
   ```
2. **Metadata identifier is a URL** — 1 point(s)

   ```sparql
   ASK { ?iri ?p ?o }
   ```
3. **Metadata identifier is globally unique, citable and persistent** — 3 point(s)
   - The resource IRI must resolve

### F2 — F2

Data are described with rich metadata

Maximum score: **7**

Requirements:

1. **Resource title and description is included** — 2 point(s)

   ```sparql
   ASK {
       ?iri sdo:name ?title ;
           sdo:description ?desc .
   }
   ```
2. **Additional descriptive properties are present** — 2 point(s)

   ```sparql
   ASK { ?iri sdo:keywords ?indigeneity }
   ```
3. **All recommended descriptive properties are present** — 3 point(s)

   ```sparql
   ASK {
       ?iri sdo:name ?title ;
           sdo:description ?desc ;
           sdo:keywords ?keywords ;
           prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/pointOfContact> ;
           sdo:agent ?agent .
       ?agent sdo:email|sdo:telephone ?contact .
   }
   ```

### F3 — F3

Metadata clearly and explicitly include the identifier of the data they describe

Maximum score: **2**

Requirements:

1. **Distribution information is included as a resolvable URL** — 2 point(s)
   - Every `url` result must resolve

   ```sparql
   SELECT ?url
   WHERE {
     ?iri sdo:distribution ?dist .
     ?dist sdo:contentUrl ?url .
   }
   ```

   ```sparql
   ASK {
       ?iri sdo:distribution ?dist .
       ?dist sdo:contentUrl ?url .
   }
   ```

### F4 — F4

(Meta)data are registered or indexed in a searchable resource

Maximum score: **4**

Requirements:

1. **Data is described in a repository** — 3 point(s)

   ```sparql
   ASK { ?iri sdo:distribution ?dist }
   ```
2. **Data is discoverable through several registries** — 1 point(s)

   ```sparql
   ASK WHERE {
     {
       SELECT ?resource (count(?dist) as ?dist_count)
       WHERE {
         BIND(?iri as ?resource)
         ?resource sdo:distribution ?dist .
       }
       GROUP BY ?resource
     }
     FILTER(?dist_count > 1)
   }
   ```

## A — Accessible

Once data is found, access information needs to be clearly indicated on the metadata.

Maximum score: **10**

### A1 — A1

(Meta)data are retrievable by their identifier using a standardised communications protocol

Maximum score: **7**

#### A1.1 — A1.1

The protocol is open, free, and universally implementable

Maximum score: **4**

Requirements:

1. **F1 >= 2 AND Access Rights exist** — 3 point(s)
   - Condition: f1 ≥ 2

   ```sparql
   ASK { ?iri sdo:usageInfo ?accessRights }
   ```
2. **Access Rights are open** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:usageInfo <https://linked.data.gov.au/def/data-access-rights/open> }
   ```

#### A1.2 — A1.2

The protocol allows for an authentication and authorisation procedure, where necessary

Maximum score: **3**

Requirements:

1. **F3 = 2 AND Access Rights exist** — 3 point(s)
   - Condition: f3 ≥ 2

   ```sparql
   ASK {
       ?iri sdo:usageInfo ?accessRights ;
           sdo:distribution ?dist .
       ?dist sdo:contentUrl ?url .
   }
   ```

### A2 — A2

Metadata are accessible, even when the data are no longer available

Maximum score: **3**

Requirements:

1. **Under the archive policy, the metadata record will be available even if the data/resource is no longer available** — 3 point(s)

   ```sparql
   ASK {
       ?iri prov:wasInfluencedBy ?policy .
       ?policy sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/data-policy> .
   }
   ```

## I — Interoperable

The data should be able to be integrated with other data.

Maximum score: **17**

### I1 — I1

(Meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation.

Maximum score: **3**

Requirements:

1. **Metadata is structured using an open standard** — 1 point(s)

   ```sparql
   ASK { ?iri ?p ?o }
   ```
2. **Metadata is machine readable** — 2 point(s)

   ```sparql
   ASK { ?iri ?p ?o }
   ```

### I2 — I2

(Meta)data use vocabularies that follow FAIR principles

Maximum score: **9**

Requirements:

1. **F1 & F2 are scored fully** — 4 point(s)
   - Condition: f1 = maximum
   - Condition: f2 = maximum
2. **Reference vocabularies have been used to describe the data** — 4 point(s)

   ```sparql
   ASK {
       ?iri sdo:keywords ?keywords ;
           sdo:license ?license ;
           sdo:usageInfo ?accessRights .
   }
   ```
3. **Vocabulary references use global identifiers** — 1 point(s)

   ```sparql
   ASK {
       ?iri sdo:keywords|sdo:license|sdo:usageInfo ?vocab .
       FILTER isIRI(?vocab)
   }
   ```

### I3 — I3

(Meta)data include qualified references to other (meta)data

Maximum score: **5**

Requirements:

1. **Metadata includes links to other metadata** — 4 point(s)

   ```sparql
   ASK {
       {
           ?iri sdo:license ?license .
           FILTER isIRI(?license)
       }
       UNION {
           ?iri sdo:spatialCoverage ?spatial .
           FILTER isIRI(?spatial)
       }
       UNION {
           ?iri sdo:distribution ?distribution .
           ?distribution sdo:contentUrl ?accessURL .
       }
       UNION {
           ?iri prov:wasInfluencedBy ?idgf .
           ?idgf sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> ;
               sdo:url ?idgfUrl .
       }
   }
   ```
2. **Metadata is machine readable** — 1 point(s)
   - Condition: f1 ≥ 2

## R — Reusable

Metadata and data should be well-described so that they can be replicated and/or combined in different settings.

Maximum score: **12**

### R1 — R1

(Meta)data are richly described with a plurality of accurate and relevant attributes

Maximum score: **12**

#### R1.1 — R1.1

(Meta)data are released with a clear and accessible data usage license

Maximum score: **3**

Requirements:

1. **Metadata includes license** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:license ?license }
   ```
2. **Metadata includes rights statement** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:copyrightNotice ?rights }
   ```
3. **Access rights exist** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:usageInfo ?accessRights }
   ```

#### R1.2 — R1.2

(Meta)data are associated with detailed provenance

Maximum score: **6**

Requirements:

1. **Includes role custodian/author/creator** — 1 point(s)

   ```sparql
   ASK {
       VALUES ?role {
           <https://linked.data.gov.au/def/data-roles/author>
           <https://linked.data.gov.au/def/data-roles/creator>
           <https://linked.data.gov.au/def/data-roles/custodian>
       }
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole ?role .
   }
   ```
2. **Created date included** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:dateCreated ?created }
   ```
3. **License exists** — 1 point(s)

   ```sparql
   ASK { ?iri sdo:license ?license }
   ```
4. **Spatial exists** — 2 point(s)

   ```sparql
   ASK { ?iri sdo:spatialCoverage ?spatial }
   ```
5. **Contact details exist** — 1 point(s)

   ```sparql
   ASK {
       ?iri prov:qualifiedAttribution ?agentRole .
       ?agentRole prov:hadRole <https://linked.data.gov.au/def/data-roles/pointOfContact> .
   }
   ```

#### R1.3 — R1.3

(Meta)data meet domain-relevant community standards

Maximum score: **3**

Requirements:

1. **Metadata includes a link to the data source** — 2 point(s)
   - Condition: f3 ≥ 2
2. **Metadata conforms to well known community standards** — 1 point(s)
   - Condition: a1 ≥ 6
