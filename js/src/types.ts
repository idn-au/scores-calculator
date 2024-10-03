export type Format = "text/turtle"
    | "ttl"
    // | "turtle"
    | "application/trig"
    | "trig"
    | "application/n-triples"
    // | "n-triples"
    // | "ntriples"
    | "nt"
    | "application/n-quads"
    // | "n-quads"
    // | "nquads"
    | "nq"
    | "text/n3"
    | "n3"
    | "application/rdf+xml"
    | "rdf"
// | "xml";

export type DagItem = {
    depends: string[];
    completed: boolean;
};

export type Dag = {
    [key: string]: DagItem;
};

export type Condition = {
    title: string;
    key: string;
    value: number | "max";
};

export type Requirement = {
    value: number;
    description: string;
    query?: string;
    conditions?: Condition[];
};

export type RequirementScored = Omit<Requirement, "query" | "conditions"> & {
    enabled: boolean;
};

export type Prerequisite = {
    conditions: Condition[];
};

export type PrerequisiteScored = Prerequisite & {
    enabled: boolean;
};

export type ScoreDef = {
    title: string;
    description: string;
    prerequisites?: Prerequisite;
    scores?: ScoreDefObj;
    requirements?: Requirement[];
};

export type ScoreValue = Omit<ScoreDef, "scores" | "prerequisites" | "requirements"> & {
    value: number;
    max: number;
    scores?: ScoreValueObj;
    prerequisites?: PrerequisiteScored;
    requirements?: RequirementScored[];
};

export type ScoreDefObj = {
    [key: string]: ScoreDef;
};

export type ScoreValueObj = {
    [key: string]: ScoreValue;
};