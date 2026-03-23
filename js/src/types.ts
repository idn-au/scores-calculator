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
    resolvable?: {
        query: string;
        variable: string;
    } | "self";
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

export type TopScoreValueObj = {
    version: string;
    created: string;
    refResource: string;
    scores: ScoreValueObj;
};

export type ScoreValueObj = {
    [key: string]: ScoreValue;
};

export type SPARQLResultsJSON = {
    head: {
        vars?: string[];
        link?: string[];
    },
    results?: {
        bindings: Record<string, {
            type: "uri" | "literal" | "bnode";
            value: string;
            "xml:lang"?: string;
            datatype?: string;
        }>[];
    },
    boolean?: boolean;
};
