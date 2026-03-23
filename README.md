# Scores Calculator

This is a collection of packages that can calculate [FAIR](https://www.go-fair.org/fair-principles/), [CARE](https://ardc.edu.au/resource/the-care-principles/) and other scores for datasets, based on DCAT-style metadata.

## Installation
To install the NPM packages for the JavaScript scoring library and component library, you will need an authenticated token to install NPM packages from GitHub's NPM registry.

Once you have access, you may install the packages by running the following:

```bash
npm install @idn-au/scores-calculator-js
```

```bash
npm install @idn-au/score-component-lib
```

## Calculator logic

The tables below describe the scoring rules described in the YAML files in the [`/definitions`](/definitions) directory:

### FAIR

<table>
    <tr>
        <td>
            <p>F - Findable</p>
            <p><em>Metadata and data should be easy to find for both humans and computers.</em></p>
            <table>
                <tr>
                    <td>
                        <p>F1</p>
                        <p><em>(Meta)data are assigned a globally unique and persistent identifier</em></p>
                        <table>
                            <tr>
                                <td>Metadata has an identifier [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# ?p ?o }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Metadata identifier is a URL [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# ?p ?o }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Metadata identifier is globally unique, citable and persistent [3]</td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>F2</p>
                        <p><em>Data are described with rich metadata</em></p>
                        <table>
                            <tr>
                                <td>Resource title and description is included [2]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:title ?title ;
        dcterms:description ?desc .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Additional descriptive properties are present [2]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# dcterms:type ?indigeneity }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>All recommended descriptive properties are present [3]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:title ?title ;
        dcterms:description ?desc ;
        dcterms:type ?indigeneity ;
        dcat:theme ?theme ;
        prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/pointOfContact&gt; ;
        prov:agent ?agent .
    ?agent sdo:email|sdo:telephone ?contact .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>F3</p>
                        <p><em>Metadata clearly and explicitly include the identifier of the data they describe</em></p>
                        <table>
                            <tr>
                                <td>Distribution information is included as a resolvable URL [2]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcat:distribution ?dist .
    ?dist dcat:accessURL ?url .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>F4</p>
                        <p><em>(Meta)data are registered or indexed in a searchable resource</em></p>
                        <table>
                            <tr>
                                <td>Data is described in a repository [3]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# dcat:distribution ?dist }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Data is discoverable through several registries [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK WHERE {
  {
    SELECT ?resource (count(?dist) as ?dist_count)
    WHERE {
      BIND(#iri# as ?resource)
      ?resource dcat:distribution ?dist . 
    }
    GROUP BY ?resource
  }
  FILTER(?dist_count &gt; 1)
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td>
            <p>A - Accessible</p>
            <p><em>Once data is found, access information needs to be clearly indicated on the metadata.</em></p>
            <table>
                <tr>
                    <td>
                        <p>A1</p>
                        <p><em>(Meta)data are retrievable by their identifier using a standardised communications
                            protocol</em></p>
                        <table>
                            <tr>
                                <td>
                                    <p>A1.1</p>
                                    <p><em>The protocol is open, free, and universally implementable</em></p>
                                    <table>
                                        <tr>
                                            <td>F1 >= 2 AND Access Rights exist [3]</td>
                                            <td><p>Query</p>
                                                <pre>ASK { #iri# dcterms:accessRights ?accessRights }</pre>
                                            </td>
                                            <td><p>Conditions</p>
                                                <ul>
                                                    <li>F1 >= 2</li>
                                                </ul>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Access Rights are open [1]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK { #iri# dcterms:accessRights &lt;https://linked.data.gov.au/def/data-access-rights/open&gt; }</pre>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <p>A1.2</p>
                                    <p><em>The protocol allows for an authentication and authorisation procedure, where
                                        necessary</em></p>
                                    <table>
                                        <tr>
                                            <td>F3 = 2 AND Access Rights exist [3]</td>
                                            <td><p>Query</p>
                                                <pre>ASK {
    #iri# dcterms:accessRights ?accessRights ;
        dcat:distribution ?dist .
    ?dist dcat:accessURL ?url .
}
</pre>
                                            </td>
                                            <td><p>Conditions</p>
                                                <ul>
                                                    <li>F3 = 2</li>
                                                </ul>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>A2</p>
                        <p><em>Metadata are accessible, even when the data are no longer available</em></p>
                        <table>
                            <tr>
                                <td>Under the archive policy, the metadata record will be available even if the
                                    data/resource is no longer available [3]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# prov:wasInfluencedBy ?policy .
    ?policy sdo:additionalType &lt;https://data.idnau.org/pid/vocab/policy-types/data-policy&gt; .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td>
            <p>I - Interoperable</p>
            <p><em>The data should be able to be integrated with other data.</em></p>
            <table>
                <tr>
                    <td>
                        <p>I1</p>
                        <p><em>(Meta)data use a formal, accessible, shared, and broadly applicable language for
                            knowledge representation.</em></p>
                        <table>
                            <tr>
                                <td>Metadata is structured using an open standard [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# ?p ?o }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Metadata is machine readable [2]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# ?p ?o }</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>I2</p>
                        <p><em>(Meta)data use vocabularies that follow FAIR principles</em></p>
                        <table>
                            <tr>
                                <td>F1 & F2 are scored fully [4]</td>
                                <td colspan="2"><p>Conditions</p>
                                    <ul>
                                        <li>F1 has scored fully</li>
                                        <li>F2 has scored fully</li>
                                    </ul>
                                </td>
                            </tr>
                            <tr>
                                <td>Reference vocabularies have been used to describe the data [4]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:type ?indigeneity ;
        dcat:theme ?theme ;
        dcterms:license ?license ;
        dcterms:accessRights ?accessRights .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Vocabulary references use global identifiers [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:type|dcat:theme|dcterms:license|dcterms:accessRights ?vocab .
    FILTER isIRI(?vocab)
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>I3</p>
                        <p><em>(Meta)data include qualified references to other (meta)data</em></p>
                        <table>
                            <tr>
                                <td>Metadata includes links to other metadata [4]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    {
        #iri# dcterms:license ?license .
        FILTER isIRI(?license)
    }
    UNION {
        #iri# dcterms:spatial ?spatial .
        FILTER isIRI(?spatial)
    }
    UNION {
        #iri# dcat:distribution ?distribution .
        ?distribution dcat:accessURL ?accessURL .
    }
    UNION {
        #iri# prov:wasInfluencedBy ?idgf .
        ?idgf sdo:additionalType &lt;https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance&gt; ;
            sdo:url ?idgfUrl .
    }
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Metadata is machine readable [1]</td>
                                <td colspan="2"><p>Conditions</p>
                                    <ul>
                                        <li>F1 > 1</li>
                                    </ul>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td>
            <p>R - Reusable</p>
            <p><em>Metadata and data should be well-described so that they can be replicated and/or combined in
                different settings.</em></p>
            <table>
                <tr>
                    <td>
                        <p>R1</p>
                        <p><em>(Meta)data are richly described with a plurality of accurate and relevant attributes</em>
                        </p>
                        <table>
                            <tr>
                                <td>
                                    <p>R1.1</p>
                                    <p><em>(Meta)data are released with a clear and accessible data usage license</em>
                                    </p>
                                    <table>
                                        <tr>
                                            <td>Metadata includes license [1]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK { #iri# dcterms:license ?license }</pre>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Metadata includes rights statement [1]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK { #iri# dcterms:rights ?rights }</pre>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Access rights exist [1]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK { #iri# dcterms:accessRights ?accessRights }</pre>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <p>R1.2</p>
                                    <p><em>(Meta)data are associated with detailed provenance</em></p>
                                    <table>
                                        <tr>
                                            <td>Includes role custodian/author/creator [1]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK {
    VALUES ?role {
        &lt;https://linked.data.gov.au/def/data-roles/author&gt;
        &lt;https://linked.data.gov.au/def/data-roles/creator&gt;
        &lt;https://linked.data.gov.au/def/data-roles/custodian&gt;
    }
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole ?role .
}
</pre>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Created date included [1]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK { #iri# dcterms:created ?created }</pre>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>License exists [1]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK { #iri# dcterms:license ?license }</pre>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Spatial exists [2]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK { #iri# dcterms:spatial ?spatial }</pre>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Contact details exist [1]</td>
                                            <td colspan="2"><p>Query</p>
                                                <pre>ASK {
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/pointOfContact&gt; .
}
</pre>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <p>R1.3</p>
                                    <p><em>(Meta)data meet domain-relevant community standards</em></p>
                                    <table>
                                        <tr>
                                            <td>Metadata includes a link to the data source [2]</td>
                                            <td colspan="2"><p>Conditions</p>
                                                <ul>
                                                    <li>F3 = 2</li>
                                                </ul>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td>Metadata conforms to well known community standards [1]</td>
                                            <td colspan="2"><p>Conditions</p>
                                                <ul>
                                                    <li>A1 >= 6</li>
                                                </ul>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>

### CARE

<table>
    <tr>
        <td>
            <p>C - Collective Benefit</p>
            <p><em>Data ecosystems shall be designed and function in ways that enable Indigenous Peoples to derive
                benefit from the data.</em></p>
            <table>
                <tr>
                    <td>
                        <p>C1</p>
                        <p><em>For inclusive development and innovation</em></p>
                        <table>
                            <tr>
                                <td>Metadata is discoverable (persistently identified) [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# ?p ?o }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>The data has been assigned one or more Indigeneity terms [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# dcterms:type ?indigeneity }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Data has Access Rights described [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# dcterms:accessRights ?accessRights }</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>C2</p>
                        <p><em>For improved government and citizen engagement</em></p>
                        <table>
                            <tr>
                                <td>Metadata is discoverable via the internet (i.e. IRI resolves) [1]</td>
                            </tr>
                            <tr>
                                <td>Data title exists [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# dcterms:title ?title }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Data description exists [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# dcterms:description ?description }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Custodian (Role) Agent information in database has indigeneity = “Indigenous Persons
                                    Organisation” OR “Owned By Indigenous Persons” OR “Run By Indigenous Persons” [1]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    VALUES ?indigeneity {
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/run-by-indigenous-persons&gt;
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/owned-by-indigenous-persons&gt;
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation&gt;
    }
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/custodian&gt; ;
        prov:agent ?agent .
    ?agent dcterms:type ?indigeneity .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>C3</p>
                        <p><em>For inclusive development and innovation</em></p>
                        <table>
                            <tr>
                                <td>License and Rights have been identified and Agent with role “Rights Holder” has been
                                    identified [2]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:license ?license ;
        dcterms:rights ?rights ;
        prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/rightsHolder&gt; .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Data distribution information exists [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcat:distribution ?distribution .
    ?distribution dcat:accessURL ?url .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td>
            <p>A - Authority to Control</p>
            <p><em>Indigenous Peoples' rights and interests in Indigenous data must be recognised and their authority to
                control such data be empowered.</em></p>
            <table>
                <tr>
                    <td>
                        <p>A1</p>
                        <p><em>Recognizing rights and interests</em></p>
                        <table>
                            <tr>
                                <td>Custodian (Role) Agent information in database has indigeneity = “Indigenous Persons
                                    Organisation” OR “Owned By Indigenous Persons” OR “Run By Indigenous Persons” [1]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    VALUES ?indigeneity {
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/run-by-indigenous-persons&gt;
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/owned-by-indigenous-persons&gt;
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation&gt;
    }
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/custodian&gt; ;
        prov:agent ?agent .
    ?agent dcterms:type ?indigeneity .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>License and Rights have been identified and Agent with role “Rights Holder” has been
                                    identified [2]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:license ?license ;
        dcterms:rights ?rights ;
        prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/rightsHolder&gt; .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>A2</p>
                        <p><em>Data for governance</em></p>
                        <table>
                            <tr>
                                <td>The URL link to, OR text description of, an Indigenous Data Governance Framework or
                                    Indigenous Data Committee is identified in the metadata record [1]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# prov:wasInfluencedBy ?idgf .
    ?idgf sdo:additionalType &lt;https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance&gt; ;
        sdo:url|sdo:description ?o .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Agent which has indicated the Indigenous Data Governance Framework has Role =
                                    Custodian [1]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/custodian&gt; ;
        prov:agent ?agent .
    ?agent prov:contributed ?idgf .
    ?idgf sdo:additionalType &lt;https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance&gt; .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>A3</p>
                        <p><em>Governance of data</em></p>
                        <table>
                            <tr>
                                <td>Indigeneity = By Indigenous People [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:type &lt;https://data.idnau.org/pid/vocab/indigeneity/by-indigenous-people&gt; .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>URL link to an Indigenous Data Governance Framework or Indigenous Data Committee is
                                    identified in the metadata record [1]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# prov:wasInfluencedBy ?idgf .
    ?idgf sdo:additionalType &lt;https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance&gt; ;
        sdo:url ?url .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td>
            <p>R - Responsibility</p>
            <p><em>Those working with Indigenous data have a responsibility to share how those data are used to support
                Indigenous Peoples' self-determination and collective benefit.</em></p>
            <table>
                <tr>
                    <td>
                        <p>R1</p>
                        <p><em>For positive relationships</em></p>
                        <table>
                            <tr>
                                <td>Indigeneity = By Indigenous People [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:type &lt;https://data.idnau.org/pid/vocab/indigeneity/by-indigenous-people&gt; .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Custodian (Role) Agent information in database has indigeneity = “Indigenous Persons
                                    Organisation” OR “Owned By Indigenous Persons” OR “Run By Indigenous Persons” [2]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    VALUES ?indigeneity {
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/run-by-indigenous-persons&gt;
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/owned-by-indigenous-persons&gt;
        &lt;https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation&gt;
    }
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/custodian&gt; ;
        prov:agent ?agent .
    ?agent dcterms:type ?indigeneity .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>R2</p>
                        <p><em>For expanding capability and capacity</em></p>
                        <table>
                            <tr>
                                <td>Custodian (Role) Agent has identified a resolvable URL link to, OR text description
                                    of, an Indigenous Data Governance Framework or Indigenous Data Committee in the
                                    metadata record [2]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/custodian&gt; ;
        prov:agent ?agent .
    ?agent prov:contributed ?idgf .
    ?idgf sdo:additionalType &lt;https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance&gt; ;
        sdo:url|sdo:description ?o .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>R3</p>
                        <p><em>For Indigenous languages and worldviews</em></p>
                        <table>
                            <tr>
                                <td>C3 has scored fully [2]</td>
                                <td colspan="2"><p>Conditions</p>
                                    <ul>
                                        <li>C3 has scored fully</li>
                                    </ul>
                                </td>
                            </tr>
                            <tr>
                                <td>Custodian (Role) Agent has identified a resolvable URL link to, OR text description
                                    of, an Indigenous Data Governance Framework or Indigenous Data Committee in the
                                    metadata record [1]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/custodian&gt; ;
        prov:agent ?agent .
    ?agent prov:contributed ?idgf .
    ?idgf sdo:additionalType &lt;https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance&gt; ;
        sdo:url ?url .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Spatial geometry has been identified [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# dcterms:spatial ?spatial }</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>At least two themes have been selected [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK { #iri# dcat:theme ?theme }</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td>
            <p>E - Ethics</p>
            <p><em>Indigenous Peoples' rights and wellbeing should be the primary concern at all stages of the data life
                cycle and across the data ecosystem.</em></p>
            <table>
                <tr>
                    <td>
                        <p>E1</p>
                        <p><em>For minimising harm and maximising benefit</em></p>
                        <table>
                            <tr>
                                <td>C3 has scored fully [2]</td>
                                <td colspan="2"><p>Conditions</p>
                                    <ul>
                                        <li>C3 has scored fully</li>
                                    </ul>
                                </td>
                            </tr>
                            <tr>
                                <td>A1 has scored fully [1]</td>
                                <td colspan="2"><p>Conditions</p>
                                    <ul>
                                        <li>A1 has scored fully</li>
                                    </ul>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>E2</p>
                        <p><em>For justice</em></p>
                        <table>
                            <tr>
                                <td>A3 has scored fully [2]</td>
                                <td colspan="2"><p>Conditions</p>
                                    <ul>
                                        <li>A3 has scored fully</li>
                                    </ul>
                                </td>
                            </tr>
                            <tr>
                                <td>Custodian (Role) Agent’s information in database has ONLY Indigeneity = “Indigenous
                                    Persons Organisation” [1]
                                </td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/custodian&gt; ;
        prov:agent ?agent .
    ?agent dcterms:type &lt;https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation&gt; .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <p>E3</p>
                        <p><em>For future use</em></p>
                        <table>
                            <tr>
                                <td>The date that the data was created and modified are identified [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# dcterms:created ?created ;
        dcterms:modified ?modified .
}
</pre>
                                </td>
                            </tr>
                            <tr>
                                <td>Name AND point of contact (Email OR Phone) is identified [1]</td>
                                <td colspan="2"><p>Query</p>
                                    <pre>ASK {
    #iri# prov:qualifiedAttribution ?agentRole .
    ?agentRole dcat:hadRole &lt;https://linked.data.gov.au/def/data-roles/pointOfContact&gt; ;
        prov:agent ?agent .
    ?agent sdo:name ?name .
}
</pre>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>

## Licensing & Rights

The creators and maintainers of this software wish for it to be available for use as widely as possible. The software is thus licensed using the very permissive [BSD 3-Clause](https://opensource.org/licenses/BSD-3-Clause) software license, a copy of the deed of which is in the file LICENSE.

This software is copyright as follows:

(c) Indigenous Data Network, 2025

## Contacts

For technical enquiries:

**Jamie Feiss**  
*Data Infrastructure Developer*  
Indigenous Data Network  
University of Melbourne  
jamie.feiss@unimelb.edu.au

For policy:

**Levi Murray**  
*Strategic Data Manager*  
Indigenous Data Network  
University of Melbourne  
levi.murray@unimelb.edu.au