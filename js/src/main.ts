// import { type ContextDefinition } from "jsonld";
// import * as jsonld from "jsonld";
import { Scoring } from "./scoring";
// import { Frame } from "jsonld/jsonld-spec";

const example = `PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sdo: <https://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

<https://example.com/example1> a dcat:Resource ;
    dcterms:accessRights <https://linked.data.gov.au/def/data-access-rights/open> ;
    dcterms:created "2024-08-12"^^xsd:date ;
    dcterms:description "This is a description for example 1" ;
    dcterms:issued "2024-08-12"^^xsd:date ;
    dcterms:license <http://purl.org/NET/rdflicense/allrightsreserved> ;
    dcterms:modified "2024-08-12"^^xsd:date ;
    dcterms:rights "rights" ;
    dcterms:type <https://data.idnau.org/pid/vocab/indigeneity/by-indigenous-people> ;
    dcterms:spatial [
        a geo:Geometry ;
        geo:asWKT "POLYGON ((0 1 2 3 4))"^^geo:wktLiteral ;
    ] ;
    dcterms:temporal [
        prov:endedAtTime "2024-07"^^xsd:monthYear ;
        prov:startedAtTime "2023"^^xsd:gYear ;
    ] ;
    dcterms:title "Example 1" ;
    dcat:distribution [
        dcat:accessURL "https://example.com/distribution"^^xsd:anyURI ;
    ] ;
    dcat:theme <https://vocabularyserver.com/apais/xml.php?skosTema=181> ,
        <https://vocabularyserver.com/apais/xml.php?skosTema=147> ;
    prov:qualifiedAttribution [
        dcat:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
        prov:agent <https://example.com/custodianagent> ;
    ] ,
    [
        dcat:hadRole <https://linked.data.gov.au/def/data-roles/pointOfContact> ;
        prov:agent <https://example.com/contactagent> ;
    ] ;
    prov:wasInfluencedBy _:b1 ,
        _:b2 ;
.

<https://example.com/custodianagent> a sdo:Organization ;
    dcterms:type <https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation> ;
    sdo:description "Custodian agent description" ;
    sdo:identifier "id1"^^xsd:token ;
    sdo:name "Custodian Agent" ;
    prov:contributed _:b1 ;
.

<https://example.com/contactagent> a sdo:Person ;
    dcterms:type <https://data.idnau.org/pid/vocab/org-indigeneity/indigeneity-unknown> ;
    sdo:description "Contact agent description" ;
    sdo:identifier "id2"^^xsd:token ;
    sdo:name "Contact Agent" ;
.

_:b1 a sdo:DigitalDocument ;
    sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/indigenous-data-governance> ;
    sdo:url "https://example.com/idg-framework"^^xsd:anyURI ;
.

_:b2 a sdo:DigitalDocument ;
    sdo:additionalType <https://data.idnau.org/pid/vocab/policy-types/data-policy> ;
    sdo:description "Description of the archive policy" ;
.
`;

// const rdf = `PREFIX dcat: <http://www.w3.org/ns/dcat#>
// PREFIX dcterms: <http://purl.org/dc/terms/>
// PREFIX qb: <http://purl.org/linked-data/cube#>
// PREFIX scores: <https://linked.data.gov.au/def/scores/>
// PREFIX sdo: <https://schema.org/>
// PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

// <https://example.com/resource>
//     a dcat:Resource ;
//     scores:hasScore [
//         a
//             qb:ObservationGroup ,
//             scores:FairScore ;
//         qb:observation
//             [
//                 a qb:Observation ;
//                 scores:fairFScore [
//                     a qb:ObservationGroup ;
//                     qb:observation [
//                         a qb:Observation ;
//                         scores:fairF1Score 4 ;
//                     ] ,
//                     [
//                         a qb:Observation ;
//                         scores:fairF2Score 3 ;
//                     ] ,
//                     [
//                         a qb:Observation ;
//                         scores:fairF3Score [
//                             a qb:ObservationGroup ;
//                             qb:observation [
//                                 a qb:Observation ;
//                                 scores:fairF3Req1Score 4 ;
//                             ] ,
//                             [
//                                 a qb:Observation ;
//                                 scores:fairF3Req2Score 1 ;
//                             ] ,
//                             [
//                                 a qb:Observation ;
//                                 scores:fairF3Req3Score 2 ;
//                             ] ;
//                         ] ;
//                     ] ;
//                 ] ;
//             ] ,
//             [
//                 a qb:Observation ;
//                 scores:fairAScore 0 ;
//             ] ,
//             [
//                 a qb:Observation ;
//                 scores:fairIScore 6 ;
//             ] ,
//             [
//                 a qb:Observation ;
//                 scores:fairRScore 3 ;
//             ] ;
//         scores:refResource <https://example.com/resource> ;
//         dcterms:created "2025-05-06T05:47:41"^^xsd:dateTime ;
//         sdo:version "0.1.0" ;
//     ] ;
// .
// `;

// const context: ContextDefinition = {
//     // prefixes
//     "dcat": "http://www.w3.org/ns/dcat#",
//     "dcterms": "http://purl.org/dc/terms/",
//     "qb": "http://purl.org/linked-data/cube#",
//     "scores": "https://linked.data.gov.au/def/scores/",
//     "sdo": "https://schema.org/",
//     "xsd": "http://www.w3.org/2001/XMLSchema#",
//     // aliases
//     "id": "@id",
//     "type": "@type",
//     "value": "@value",
//     "created": {
//         "@id": "dcterms:created",
//         "@type": "xsd:dateTime",
//     },
//     "refResource": {
//         "@id": "scores:refResource",
//         "@type": "@id",
//     },
//     "hasScore": "scores:hasScore",
//     "version": "sdo:version",
//     "scores_obj": {
//         "@id": "qb:observation",
//         "@type": "@id",
//     },
//     "F": {
//         "@id": "scores:fairFScore",
//         "@type": "@id",
//     },
//     "A": {
//         "@id": "scores:fairAScore",
//         // "@type": "@id",
//     },
//     "I": {
//         "@id": "scores:fairIScore",
//         // "@type": "@id",
//     },
//     "R": {
//         "@id": "scores:fairRScore",
//         // "@type": "@id",
//     },
// };

// const frame: Frame = {
//     "@context": context,
//     type: "dcat:Resource",
//     "scores:hasScore": {
//         type: "qb:ObservationGroup",
//         // "scores_obj": {
//         //     type: "qb:Observation",
//         // }
//     },
// };

const scoring = await Scoring.init(["fair", "care"], { value: example, format: "text/turtle" });

function fairScore(output: "json" | "turtle") {
    return scoring.score("https://example.com/example1", "fair", output);
}

function careScore(output: "json" | "turtle") {
    return scoring.score("https://example.com/example1", "care", output);
}

function doScoringJSON() {
    document.querySelector<HTMLButtonElement>("#scoreJSONButton")!.addEventListener("click", async () => {
        document.querySelector<HTMLPreElement>("#data")!.innerText = example;
        const [fair, care] = await Promise.all([fairScore("json"), careScore("json")]);
        document.querySelector<HTMLPreElement>("#score")!.innerText = JSON.stringify({fair, care}, null, 2);
    });
}

function doScoringRDF() {
    document.querySelector<HTMLButtonElement>("#scoreRDFButton")!.addEventListener("click", async () => {
        document.querySelector<HTMLPreElement>("#data")!.innerText = example;
        const [fair, care] = await Promise.all([fairScore("turtle"), careScore("turtle")]);
        document.querySelector<HTMLPreElement>("#score")!.innerText = `-----FAIR-----\n${fair}\n\n-----CARE-----\n${care}`;
    });
}

// async function frameData() {
//     scoring.store!.update("DROP ALL");
//     scoring.store!.load(rdf, {format: "text/turtle"});
//     const nquads = scoring.store!.dump({format: "application/n-quads"});
//     const jsonldObj = await jsonld.fromRDF(nquads, { format: "application/n-quads" });
//     return await jsonld.frame(jsonldObj, frame);
// }

// function setupFrameButton() {
//     document.querySelector<HTMLButtonElement>("#frameButton")!.addEventListener("click", async () => {
//         document.querySelector<HTMLPreElement>("#data")!.innerText = JSON.stringify(context, null, 2);
//         const data = await frameData();
//         delete data["@context"];
//         document.querySelector<HTMLPreElement>("#score")!.innerText = JSON.stringify(data, null, 2);
//     });
// }

function setupClearButton() {
    document.querySelector<HTMLButtonElement>("#clearButton")!.addEventListener("click", async () => {
        document.querySelector<HTMLPreElement>("#data")!.innerText = "";
        document.querySelector<HTMLPreElement>("#score")!.innerText = "";
    });
}

document.querySelector<HTMLDivElement>("#app")!.innerHTML = `
    <style>
        #content {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }
        pre {
            white-space: pre-wrap;
        }
    </style>
    <h1>JS Score Calculator</h1>
    <div>
        <button id="scoreJSONButton">Score JSON</button>
        <button id="scoreRDFButton">Score RDF</button>
        <button id="clearButton">Clear</button>
    </div>
    <div id="content">
        <div class="column data-col">
            <h3>Data</h3>
            <pre id="data"></pre>
        </div>
        <div class="column score-col">
            <h3>Score</h3>
            <pre id="score"></pre>
        </div>
    </div>
`;

setupClearButton();
// setupFrameButton();
doScoringJSON();
doScoringRDF();
