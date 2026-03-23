<script lang="ts" setup>
import { ref, onMounted } from "vue";
import init, * as oxigraph from "oxigraph/web";
import {ScoreCalculator, type SPARQLResultsJSON, TopScoreValueObj} from "@idn-au/scores-calculator-js";
import Scores from "./components/Scores.vue";
import CircleProgress from "@/components/CircleProgress.vue";

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

let scoring: ScoreCalculator;

const fair = ref({} as TopScoreValueObj);
const care = ref({} as TopScoreValueObj);

const colorMode = ref("light");

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

onMounted(async () => {
	await init({module_or_path: "https://cdn.jsdelivr.net/npm/oxigraph@0.5.6/web_bg.wasm"});
	const store = new oxigraph.Store();
	store.load(example, { format: "text/turtle" });

	scoring = await ScoreCalculator.init(["fair", "care"]);

	const p = await Promise.all([
		scoring.score("https://example.com/example1", "fair", "json", (query) => sparqlQuery(store, query, true), (query) => sparqlQuery(store, query)),
		scoring.score("https://example.com/example1", "care", "json", (query) => sparqlQuery(store, query, true), (query) => sparqlQuery(store, query))
	]);

	fair.value = p[0] as TopScoreValueObj;
	care.value = p[1] as TopScoreValueObj;
});
</script>

<template>
	<div :class="colorMode">
		<h1>Scores Vue Component Library</h1>
		<button @click="colorMode = colorMode === 'light' ? 'dark' : 'light'">colour mode</button>
		<div class="p-3 bg-background text-foreground">
			<Scores title="FAIR" :score="fair" />
			<Scores title="CARE" :score="care" />
		</div>
	</div>
</template>
