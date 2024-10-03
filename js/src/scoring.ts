import init, * as oxigraph from "oxigraph/web";
import { parse as parseYaml } from "yaml";
import type { ScoreDef, ScoreDefObj, ScoreValue, ScoreValueObj, Format, Condition, Dag } from "./types";

const OXIGRAPH_WASM_URL = "https://cdn.jsdelivr.net/npm/oxigraph@0.4.0/web_bg.wasm";
const DEFINITION_URL_PREFIX = "https://cdn.jsdelivr.net/gh/idn-au/scores-calculator@feature/refactor/definitions"

const PREFIXES = `PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sdo: <https://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>`;

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
 * Builds the DAG and the scored object without values
 * 
 * @param obj 
 * @returns 
 */
export function buildDag(obj: ScoreDefObj): { dag: Dag, scoredObj: ScoreValueObj } {
    const dag: Dag = {};
    const scoredObj = traverseScores(obj, dag);

    return { dag, scoredObj };
}

/**
 * Performs scoring following a DAG
 * 
 * @param key 
 * @param obj 
 */
function scoreByKey(key: string, obj: ScoreDefObj, dag: Dag, scoredObj: ScoreValueObj, store: oxigraph.Store, iri: string) {
    if (!dag[key].completed) {
        dag[key].depends.forEach(d => {
            scoreByKey(d, obj, dag, scoredObj, store, iri);
        });
        
        const def = searchByKey(key, obj) as ScoreDef;
        const value = searchByKey(key, scoredObj) as ScoreValue;
        
        if (def.requirements) {
            def.requirements.forEach((r, index) => {
                let queryResult = true;
                let conditionsResult = true;
                if (r.query) {
                    queryResult = store.query(PREFIXES + "\n" + r.query.replace("#iri#", `<${iri}>`)) as boolean;
                }
                if (r.conditions) {
                    conditionsResult = r.conditions!.every(c => evaluateCondition(c.key, scoredObj, c.value));
                }
                const result = queryResult && conditionsResult;
                value.requirements![index].enabled = result;

                let satisfiedPrereqs = true;

                if (def.prerequisites) {
                    satisfiedPrereqs = def.prerequisites.conditions.every(c => evaluateCondition(c.key, scoredObj, c.value));
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
 * Uses the DAG to score the whole score def
 * 
 * @param obj 
 */
export async function dagScoring(data: string, obj: ScoreDefObj, iri: string, format: Format = "text/turtle",
    // output: "json" | "turtle" = "json"
): Promise<ScoreValueObj> {
    await init(OXIGRAPH_WASM_URL);
    const store = new oxigraph.Store();
    store.load(data, { format });
    const { dag, scoredObj } = buildDag(obj);

    Object.keys(obj).forEach(key => {
        scoreByKey(key, obj, dag, scoredObj, store, iri);
    });

    return scoredObj;
}

export async function fairScore(data: string, iri: string, format: Format = "text/turtle"): Promise<ScoreValueObj> {
    const r = await fetch(`${DEFINITION_URL_PREFIX}/fairDef.yaml`);
    const yamlFile = await r.text()
    return await dagScoring(data, parseYaml(yamlFile) as ScoreDefObj, iri, format);
}

export async function careScore(data: string, iri: string, format: Format = "text/turtle"): Promise<ScoreValueObj> {
    const r = await fetch(`${DEFINITION_URL_PREFIX}/careDef.yaml`);
    const yamlFile = await r.text()
    return await dagScoring(data, parseYaml(yamlFile) as ScoreDefObj, iri, format);
}
