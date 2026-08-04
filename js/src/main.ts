import init, * as oxigraph from "oxigraph/web";
import { ScoreCalculator } from "./score";
import type {SPARQLResultsJSON} from "./types.ts";

const OXIGRAPH_VERSION = "0.5.8";

const example = `PREFIX geo: <http://www.opengis.net/ont/geosparql#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sdo: <https://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

<https://example.com/example1> a sdo:CreativeWork ;
    sdo:usageInfo <https://linked.data.gov.au/def/data-access-rights/open> ;
    sdo:dateCreated "2024-08-12"^^xsd:date ;
    sdo:description "This is a description for example 1" ;
    sdo:dateIssued "2024-08-12"^^xsd:date ;
    sdo:license <http://purl.org/NET/rdflicense/allrightsreserved> ;
    sdo:dateModified "2024-08-12"^^xsd:date ;
    sdo:copyrightNotice "rights" ;
    sdo:keywords <https://data.idnau.org/pid/vocab/indigeneity/by-indigenous-people> ;
    sdo:spatialCoverage [
        a geo:Geometry ;
        geo:asWKT "POLYGON ((0 1 2 3 4))"^^geo:wktLiteral ;
    ] ;
    sdo:temporalCoverage [
        prov:endedAtTime "2024-07"^^xsd:monthYear ;
        prov:startedAtTime "2023"^^xsd:gYear ;
    ] ;
    sdo:name "Example 1" ;
    sdo:distribution [
        sdo:contentUrl "https://data.idnau.org"^^xsd:anyURI ;
    ] ;
    sdo:keywords <https://vocabularyserver.com/apais/xml.php?skosTema=181> ,
        <https://vocabularyserver.com/apais/xml.php?skosTema=147> ;
    prov:qualifiedAttribution [
        prov:hadRole <https://linked.data.gov.au/def/data-roles/custodian> ;
        sdo:agent <https://example.com/custodianagent> ;
    ] ,
    [
        prov:hadRole <https://linked.data.gov.au/def/data-roles/pointOfContact> ;
        sdo:agent <https://example.com/contactagent> ;
    ] ;
    prov:wasInfluencedBy _:b1 ,
        _:b2 ;
.

<https://example.com/custodianagent> a sdo:Organization ;
    sdo:keywords <https://data.idnau.org/pid/vocab/org-indigeneity/indigenous-persons-organisation> ;
    sdo:description "Custodian agent description" ;
    sdo:identifier "id1"^^xsd:token ;
    sdo:name "Custodian Agent" ;
    prov:contributed _:b1 ;
.

<https://example.com/contactagent> a sdo:Person ;
    sdo:keywords <https://data.idnau.org/pid/vocab/org-indigeneity/indigeneity-unknown> ;
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

const emptyData = "";

function sparqlQuery(store: oxigraph.Store, query: string, ask: boolean = false): SPARQLResultsJSON | boolean {
    const options = {use_default_graph_as_union: true};
    if (!ask) {
        options.results_format = "application/sparql-results+json"
    }
    let result = store.query(query, options);
    if (!ask) {
        result = JSON.parse(result as string) as SPARQLResultsJSON;
    }
    return result;
}

async function fairScore(output: "json" | "turtle") {
    await init({module_or_path: "https://cdn.jsdelivr.net/npm/oxigraph@0.5.9/web_bg.wasm"});
    const store = new oxigraph.Store();
    store.load(example, { format: "text/turtle" });

    function askQuery(query: string): boolean {
        const result = store.query(query, {use_default_graph_as_union: true});
        return result;
    }

    function selectQuery(query: string): SPARQLResultsJSON {
        const result = store.query(query, {use_default_graph_as_union: true, results_format: "application/sparql-results+json",});
        return JSON.parse(result);
    }

    const calculator = await ScoreCalculator.init(["fair"]);
    return await calculator.score("https://example.com/example1", "fair", output, askQuery, selectQuery);
}

async function careScore(output: "json" | "turtle") {
    await init({module_or_path: "https://cdn.jsdelivr.net/npm/oxigraph@0.5.9/web_bg.wasm"});
    const store = new oxigraph.Store();
    store.load(example, { format: "text/turtle" });

    const calculator = await ScoreCalculator.init(["care"]);
    return await calculator.score("https://example.com/example1", "care", output, (query) => sparqlQuery(store, query, true), (query) => sparqlQuery(store, query));
}

function doScoringJSON() {
    document.querySelector<HTMLButtonElement>("#scoreJSONButton")!.addEventListener("click", async () => {
        document.querySelector<HTMLPreElement>("#data")!.innerText = example;
        const [fair, care] = await Promise.all([fairScore("json"), careScore("json")]);
        // const fair = await fairScore("json");
        document.querySelector<HTMLPreElement>("#score")!.innerText = JSON.stringify({fair, care}, null, 2);
        // document.querySelector<HTMLPreElement>("#score")!.innerText = JSON.stringify(fair, null, 2);
    });
}

// function doScoringRDF() {
//     document.querySelector<HTMLButtonElement>("#scoreRDFButton")!.addEventListener("click", async () => {
//         document.querySelector<HTMLPreElement>("#data")!.innerText = example;
//         const [fair, care] = await Promise.all([fairScore("turtle"), careScore("turtle")]);
//         // const fair = await fairScore("turtle");
//         document.querySelector<HTMLPreElement>("#score")!.innerText = `-----FAIR-----\n${fair}\n\n-----CARE-----\n${care}`;
//         // document.querySelector<HTMLPreElement>("#score")!.innerText = fair as string;
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
<!--        <button id="scoreRDFButton">Score RDF</button>-->
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
doScoringJSON();
// doScoringRDF();
