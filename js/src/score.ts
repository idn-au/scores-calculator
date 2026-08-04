import type {
    Condition,
    Dag,
    Requirement,
    ScoreDef,
    ScoreDefObj,
    ScoreValue,
    ScoreValueObj,
    SPARQLResultsJSON,
    TopScoreValueObj,
} from "./types";
import { parse as parseYaml } from "yaml";

// const DEFINITION_URL_PREFIX = `https://cdn.jsdelivr.net/gh/idn-au/scores-calculator@${__APP_VERSION__}/definitions`;
// const DEFINITION_URL_PREFIX = `https://cdn.jsdelivr.net/gh/idn-au/scores-calculator@0.4.0/definitions`;
const DEFINITION_URL_PREFIX = "/definitions";

const PREFIXES = `PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    PREFIX prov: <http://www.w3.org/ns/prov#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sdo: <https://schema.org/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>`;

export class ScoreCalculator {
    public scoreMap: Record<string, {
        def: ScoreDefObj;
        dag: Dag;
        valueTemplate: TopScoreValueObj;
    }>;

    public urlMap: Record<string, boolean>;

    constructor(scoreDefs: Record<string, ScoreDefObj>) {
        const map: Record<string, {
            def: ScoreDefObj;
            dag: Dag;
            valueTemplate: TopScoreValueObj;
        }> = {};

        Object.entries(scoreDefs).forEach(([key, def]) => {
            const { dag, scoredObj } = this.buildDag(def);
            map[key] = {
                def: scoreDefs[key],
                dag,
                valueTemplate: scoredObj,
            };
        });

        this.scoreMap = map;
        this.urlMap = {};
    }

    static async init(scoreTypes: string[]) {
        // get score def files
        const promises = await Promise.all(scoreTypes.map(async (s) => {
            const r = await fetch(`${DEFINITION_URL_PREFIX}/${s.toLowerCase()}Def.yaml`);
            const r_1 = await r.text();
            const obj = parseYaml(r_1) as ScoreDefObj;
            return { score: s, def: obj };
        }));
        const scoreDefs = promises.reduce((obj, curr) => {
            obj[curr.score] = curr.def;
            return obj;
        }, {} as Record<string, ScoreDefObj>);

        return new ScoreCalculator(scoreDefs);
    }

    private async checkResolvable(url: string): Promise<boolean> {
        if (this.urlMap[url] !== undefined) {
            return this.urlMap[url];
        }
        else {
            let resolves = false;
            let retries = 0; // max 3

            while (!resolves && retries < 3) {
                try {
                    await fetch(url, { mode: "no-cors" });
                    resolves = true;
                }
                catch {
                    retries += 1;
                    await new Promise(r => setTimeout(r, 1000)); // 1s sleep
                }
            }

            this.urlMap[url] = resolves;

            return resolves;
        }
    }

    /**
     * Finds a nested object using only the key
     *
     * Assumes `a1.1.1` etc notation
     * @param key
     * @param obj
     */
    private searchByKey(key: string, obj: ScoreDefObj | ScoreValueObj): ScoreDef | ScoreValue {
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
    private evaluateCondition(key: string, obj: ScoreValueObj, condition: Condition["value"]): boolean {
        const s = this.searchByKey(key, obj) as ScoreValue;
        if (condition === "max") {
            return s.value === s.max;
        }
        else {
            return s.value >= condition;
        }
    }

    /**
     * Recursively traverses the score def object and builds the DAG
     *
     * @param scores
     * @param dag
     */
    private traverseScores(scores: ScoreDefObj, dag: Dag): ScoreValueObj {
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
                tempScore.scores = this.traverseScores(value.scores, dag);
                tempScore.max = Object.values(tempScore.scores).reduce((acc, curr) => acc + curr.max, 0);
            }
            else if (value.requirements) {
                dag[key].depends.push(...value.requirements.filter(r => r.conditions !== undefined).map(r => r.conditions!.map(c => c.key)).flat());
                tempScore.requirements = value.requirements.map((r) => {
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

    private async scoreRequirement(r: Requirement, index: number, def: ScoreDef, value: ScoreValue, iri: string, scoredObj: ScoreValueObj, askQueryFn: (query: string) => boolean, selectQueryFn: (query: string) => SPARQLResultsJSON) {
        let queryResult = true;
        let resolved = true;
        let conditionsResult = true;
        if (r.query) {
            const query = `${PREFIXES}\n${r.query.replace("?iri", `<${iri}>`)}`;
            queryResult = askQueryFn(query);
        }
        if (r.resolvable !== undefined) {
            if (r.resolvable === "self") {
                resolved = await this.checkResolvable(iri);
            }
            else {
                const query = `${PREFIXES}\n${r.resolvable.query.replace("?iri", `<${iri}>`)}`;
                const sparqlResults = selectQueryFn(query).results!.bindings;
                // @ts-ignore
                resolved = (await Promise.all([...sparqlResults.map(x => this.checkResolvable(x[r.resolvable!.variable!].value))])).every(x => x);
            }
        }
        if (r.conditions) {
            conditionsResult = r.conditions!.every(c => this.evaluateCondition(c.key, scoredObj, c.value));
        }
        const result = queryResult && resolved && conditionsResult;
        value.requirements![index].enabled = result;

        let satisfiedPrereqs = true;

        if (def.prerequisites) {
            satisfiedPrereqs = def.prerequisites.conditions.every(c => this.evaluateCondition(c.key, scoredObj, c.value));
            value.prerequisites!.enabled = satisfiedPrereqs;
        }

        if (result && satisfiedPrereqs) {
            value.value += r.value;
        }
    }

    /**
     * Performs scoring following a DAG
     *
     * @param key
     * @param obj
     * @param dag
     * @param scoredObj
     * @param iri
     * @param askQueryFn
     * @param selectQueryFn
     */
    private async scoreByKey(key: string, obj: ScoreDefObj, dag: Dag, scoredObj: ScoreValueObj, iri: string, askQueryFn: (query: string) => boolean, selectQueryFn: (query: string) => SPARQLResultsJSON) {
        if (!dag[key].completed) {
            for (const d of dag[key].depends) {
                await this.scoreByKey(d, obj, dag, scoredObj, iri, askQueryFn, selectQueryFn);
            }

            const def = this.searchByKey(key, obj) as ScoreDef;
            const value = this.searchByKey(key, scoredObj) as ScoreValue;

            if (def.requirements) {
                for (const [index, r] of def.requirements.entries()) {
                    await this.scoreRequirement(r, index, def, value, iri, scoredObj, askQueryFn, selectQueryFn);
                }
            }
            else if (def.scores) {
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
    private buildDag(obj: ScoreDefObj): { dag: Dag; scoredObj: TopScoreValueObj } {
        const dag: Dag = {};
        const scoredObj: TopScoreValueObj = {
            version: __APP_VERSION__,
            refResource: "",
            created: "",
            scores: this.traverseScores(obj, dag),
        };

        return { dag, scoredObj };
    }

    private newScoreValueObj(scoreType: string, iri: string): { dag: Dag; scoredObj: TopScoreValueObj } {
        const dag = structuredClone(this.scoreMap[scoreType].dag);
        const scoredObj = structuredClone(this.scoreMap[scoreType].valueTemplate);
        scoredObj.refResource = iri;
        scoredObj.created = new Date().toISOString().split(".")[0];

        return { dag, scoredObj };
    }

    /**
     *
     *
     * @param iri
     * @param scoreType
     * @param output
     * @param askQueryFn
     * @param selectQueryFn
     * @returns
     */
    public async score(iri: string, scoreType: string, output: "json" | "turtle", askQueryFn: (query: string) => boolean, selectQueryFn: (query: string) => SPARQLResultsJSON): Promise<TopScoreValueObj | string> {
        const { dag, scoredObj } = this.newScoreValueObj(scoreType, iri);

        for (const key of Object.keys(this.scoreMap[scoreType].def)) {
            await this.scoreByKey(key, this.scoreMap[scoreType].def, dag, scoredObj.scores, iri, askQueryFn, selectQueryFn);
        }

        if (output === "json") {
            return scoredObj;
        }
        else if (output === "turtle") {
            return "";
        }
        else {
            throw new TypeError("Invalid output format. Supported output formats are: 'json', 'turtle'");
        }
    }
}
