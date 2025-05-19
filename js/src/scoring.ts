import init, * as oxigraph from "oxigraph/web";
import { parse as parseYaml } from "yaml";
import type { ScoreDef, ScoreDefObj, ScoreValue, ScoreValueObj, Format, Condition, Dag, EndpointConfig, TopScoreValueObj } from "./types";

const OXIGRAPH_WASM_URL = "https://cdn.jsdelivr.net/npm/oxigraph@0.4.10/web_bg.wasm"; // update when oxigraph version changes
const DEFINITION_URL_PREFIX = `https://cdn.jsdelivr.net/gh/idn-au/scores-calculator@${__APP_VERSION__}/definitions`;

const PREFIXES = `PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sdo: <https://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>`;

/**
 * Performs a SPARQL ASK query to a remote endpoint, with optional basic auth
 * 
 * @param endpoint 
 * @param query 
 * @returns true or false
 */
async function sparqlAskRequest(endpoint: EndpointConfig, query: string): Promise<boolean> {
    const headers = new Headers({
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/sparql-query",
    });
    if (endpoint.username && endpoint.password) {
        headers.set("Authorization", "Basic " + btoa(endpoint.username + ":" + endpoint.password));
    }
    return fetch(endpoint.url, {
        method: "POST",
        body: query,
        headers: headers,
    }).then(r => r.json()).then(r => r.boolean);
}

/**
 * Finds a nested object using only the key
 * 
 * Assumes `a1.1.1` etc notation
 * @param key 
 * @param obj 
 */
function searchByKey(key: string, obj: ScoreDefObj | ScoreValueObj): ScoreDef | ScoreValue {
    const matches = key.match(/^[a-z]|\d+|\.\d+/g)!; // split by key segment
    const keys = matches.map((k, index) => { // generate array of keys to traverse
        return (matches[index - 1]) ? matches.slice(0, index + 1).join("") : k;
    });
    // @ts-ignore
    return keys.reduce((acc, curr) => acc ? (acc[curr] || acc.scores[curr]) : undefined, obj); // traverse the object using array of keys
}

/**
 * Checks if the score's value meets the condition 
 * 
 * @param key the score's key, e.g. `a1.1`
 * @param obj the score object to traverse
 * @param condition either a number to be greater than or equal to, or `"max"`
 * @returns a boolean
 */
function evaluateCondition(key: string, obj: ScoreValueObj, condition: Condition["value"]): boolean {
    const s = searchByKey(key, obj) as ScoreValue;
    if (condition === "max") {
        return s.value === s.max;
    } else {
        return s.value >= condition;
    }
}

/**
 * Recursively traverses the score def object and builds the DAG
 * 
 * @param scores 
 * @param dag 
 */
function traverseScores(scores: ScoreDefObj, dag: Dag): ScoreValueObj {
    const scoreValObj: ScoreValueObj = {};
    Object.entries(scores).forEach(([key, value]) => {
        dag[key] ??= {
            depends: [],
            completed: false,
        };

        const tempScore: ScoreValue = {
            title: value.title,
            description: value.description,
            value: 0,
            max: 0,
        };

        if (value.prerequisites) {
            dag[key].depends.push(...value.prerequisites.conditions.map(c => c.key));
            tempScore.prerequisites = {
                conditions: value.prerequisites.conditions,
                enabled: false,
            };
        }

        if (value.scores) {
            dag[key].depends.push(...Object.keys(value.scores));
            tempScore.scores = traverseScores(value.scores, dag);
            tempScore.max = Object.values(tempScore.scores).reduce((acc, curr) => acc + curr.max, 0);
        } else if (value.requirements) {
            dag[key].depends.push(...value.requirements.filter(r => r.conditions !== undefined).map(r => r.conditions!.map(c => c.key)).flat());
            tempScore.requirements = value.requirements.map(r => {
                tempScore.max += r.value;
                return {
                    value: r.value,
                    description: r.description,
                    enabled: false,
                };
            });
        }

        scoreValObj[key] = tempScore;
    });

    return scoreValObj;
}

/**
 * Performs scoring following a DAG
 * 
 * @param key 
 * @param obj 
 */
function scoreByKey(key: string, obj: ScoreDefObj, dag: Dag, scoredObj: ScoreValueObj, store: oxigraph.Store | null, iri: string, endpoint?: EndpointConfig) {
    if (!dag[key].completed) {
        dag[key].depends.forEach(d => {
            scoreByKey(d, obj, dag, scoredObj, store, iri);
        });

        const def = searchByKey(key, obj) as ScoreDef;
        const value = searchByKey(key, scoredObj) as ScoreValue;

        if (def.requirements) {
            def.requirements.forEach(async (r, index) => {
                let queryResult = true;
                let conditionsResult = true;
                if (r.query) {
                    const query = PREFIXES + "\n" + r.query.replace("#iri#", `<${iri}>`);
                    if (store === null && endpoint) {
                        queryResult = await sparqlAskRequest(endpoint, query);
                    } else {
                        queryResult = store!.query(query) as boolean;
                    }

                }
                if (r.conditions) {
                    conditionsResult = r.conditions!.every(c => evaluateCondition(c.key, scoredObj, c.value));
                }
                const result = queryResult && conditionsResult;
                value.requirements![index].enabled = result;

                let satisfiedPrereqs = true;

                if (def.prerequisites) {
                    satisfiedPrereqs = def.prerequisites.conditions.every(c => evaluateCondition(c.key, scoredObj, c.value));
                    value.prerequisites!.enabled = satisfiedPrereqs;
                }

                if (result && satisfiedPrereqs) {
                    value.value += r.value;
                }
            });
        } else if (def.scores) {
            value.value = Object.values(value.scores!).reduce((acc, curr) => acc + curr.value, 0);
        }

        dag[key].completed = true;
    }
}

/**
 * Builds the DAG and the scored object without values
 * 
 * @param obj 
 * @returns 
 */
function buildDag(iri: string, obj: ScoreDefObj): { dag: Dag, scoredObj: TopScoreValueObj } {
    const dag: Dag = {};
    const scoredObj: TopScoreValueObj = {
        version: __APP_VERSION__,
        refResource: iri,
        created: new Date().toISOString().split(".")[0],
        scores: traverseScores(obj, dag),
    };

    return { dag, scoredObj };
}

function generateRDFScoreByKey(key: string, scoreType: string, store: oxigraph.Store, scoredObj: ScoreValue, obsBNode: oxigraph.BlankNode) {
    const bnode = oxigraph.blankNode();
    store.add(oxigraph.triple(obsBNode, oxigraph.namedNode("http://purl.org/linked-data/cube#observation"), bnode));
    store.add(oxigraph.triple(bnode, oxigraph.namedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), oxigraph.namedNode("http://purl.org/linked-data/cube#Observation")));

    const bnode2 = oxigraph.blankNode();
    store.add(oxigraph.triple(bnode, oxigraph.namedNode(`https://linked.data.gov.au/def/scores/${scoreType.toLowerCase()}${key.toUpperCase()}Score`), bnode2));
    store.add(oxigraph.triple(bnode2, oxigraph.namedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), oxigraph.namedNode("http://purl.org/linked-data/cube#ObservationGroup")));
    
    if (scoredObj.scores) {
        Object.keys(scoredObj.scores).forEach(subkey => {
            generateRDFScoreByKey(subkey, scoreType, store, scoredObj.scores![subkey], bnode2);
        });
    } else {
        scoredObj.requirements!.forEach((r, index) => {
            const bnode3 = oxigraph.blankNode();
            store.add(oxigraph.triple(bnode2, oxigraph.namedNode("http://purl.org/linked-data/cube#observation"), bnode3));
            store.add(oxigraph.triple(bnode3, oxigraph.namedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), oxigraph.namedNode("http://purl.org/linked-data/cube#Observation")));
            store.add(oxigraph.triple(bnode3, oxigraph.namedNode(`https://linked.data.gov.au/def/scores/${scoreType.toLowerCase()}${key.toUpperCase()}Req${index + 1}Score`), oxigraph.literal((r.enabled ? r.value : 0).toString(), oxigraph.namedNode("http://www.w3.org/2001/XMLSchema#integer"))));
        });
    }
}

function generateRDFScores(scoreType: string, scoredObj: TopScoreValueObj): string {
    const store = new oxigraph.Store();
    store.load(`PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX qb: <http://purl.org/linked-data/cube#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX scores: <https://linked.data.gov.au/def/scores/>
PREFIX sdo: <https://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>`, {format: "text/turtle"});
    const resource = oxigraph.namedNode(scoredObj.refResource);
    store.add(oxigraph.triple(resource, oxigraph.namedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), oxigraph.namedNode("http://www.w3.org/ns/dcat#Resource")));
    const scoresBNode = oxigraph.blankNode();
    store.add(oxigraph.triple(resource, oxigraph.namedNode("https://linked.data.gov.au/def/scores/hasScore"), scoresBNode));
    store.add(oxigraph.triple(scoresBNode, oxigraph.namedNode("https://linked.data.gov.au/def/scores/refResource"), resource));
    store.add(oxigraph.triple(scoresBNode, oxigraph.namedNode("http://purl.org/dc/terms/created"), oxigraph.literal(scoredObj.created, oxigraph.namedNode("http://www.w3.org/2001/XMLSchema#dateTime"))));
    store.add(oxigraph.triple(scoresBNode, oxigraph.namedNode("https://schema.org/version"), oxigraph.literal(scoredObj.version)));
    store.add(oxigraph.triple(scoresBNode, oxigraph.namedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), oxigraph.namedNode("http://purl.org/linked-data/cube#ObservationGroup")));
    store.add(oxigraph.triple(scoresBNode, oxigraph.namedNode("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), oxigraph.namedNode(`https://linked.data.gov.au/def/scores/${scoreType.charAt(0).toUpperCase() + scoreType.substring(1).toLowerCase()}Score`)));

    Object.keys(scoredObj.scores).forEach(key => {
        generateRDFScoreByKey(key, scoreType, store, scoredObj.scores[key], scoresBNode);
    });

    return store.dump({ format: "text/turtle", from_graph_name: oxigraph.defaultGraph() });
}

export class Scoring {
    public store: oxigraph.Store | null;
    public scoreDefs: Record<string, ScoreDefObj>;

    constructor(scoreDefs: Record<string, ScoreDefObj>, store: oxigraph.Store | null) {
        this.scoreDefs = scoreDefs;
        this.store = store;
    }

    static async init(scoreTypes: string[], data?: oxigraph.Store | { value: string, format: Format }) {
        // initialise oxigraph wasm
        if (!data || typeof data === "object") {
            await init(OXIGRAPH_WASM_URL);
        }

        let store = null;

        // set oxigraph store if applicable
        if (data instanceof (oxigraph.Store)) {
            store = data;
        } else if (typeof data === "object") {
            store = new oxigraph.Store();
            store.load(data.value, { format: data.format });
        }
        
        // get score def files
        const promises = await Promise.all(scoreTypes.map(s => {
            return fetch(`${DEFINITION_URL_PREFIX}/${s.toLowerCase()}Def.yaml`).then(r => r.text()).then(r => {
                const obj = parseYaml(r) as ScoreDefObj;
                return { score: s, def: obj }
            });
        }));
        const scoreDefs = promises.reduce((obj, curr) => {
            obj[curr.score] = curr.def;
            return obj
        }, {} as Record<string, ScoreDefObj>);

        return new Scoring(scoreDefs, store);
    }

    /**
     * 
     * 
     * @param iri 
     * @param scoreType 
     * @param data 
     * @param endpoint 
     * @returns 
     */
    public score(iri: string, scoreType: string, output: "json" | "turtle", data?: { value: string, format: Format }, endpoint?: EndpointConfig): TopScoreValueObj | string {
        if (data) {
            this.store?.update("DROP ALL");
            this.store?.load(data.value, { format: data.format });
        }

        const { dag, scoredObj } = buildDag(iri, this.scoreDefs[scoreType]); // could move to init(), have a factory function for creating new scoredObjs

        Object.keys(this.scoreDefs[scoreType]).forEach(key => {
            scoreByKey(key, this.scoreDefs[scoreType], dag, scoredObj.scores, this.store, iri, endpoint);
        });

        if (output === "json") {
            return scoredObj;
        } else if (output === "turtle") {
            return generateRDFScores(scoreType, scoredObj);
        } else {
            throw new TypeError("Invalid output format. Supported output formats are: 'json', 'turtle'");
        }
    }

    // output score as either JS obj or RDF

    /**
     * 
     * 
     * @param iri 
     * @param scoreType 
     * @param data 
     * @param endpoint 
     */
    // public parse(iri: string, scoreType: string, data?: {value: string, format: Format}, endpoint?: EndpointConfig): ScoreValueObj {
    //     if (data) {
    //         this.store?.update("DROP ALL");
    //         this.store?.load(data.value, {format: data.format});
    //     }


    // }
}
