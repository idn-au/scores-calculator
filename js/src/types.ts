export interface DagItem {
    depends: string[];
    completed: boolean;
}

export interface Dag {
    [key: string]: DagItem;
}

export interface Condition {
    title: string;
    key: string;
    value: number | "max";
}

export interface Requirement {
    value: number;
    description: string;
    query?: string;
    resolvable?: {
        query: string;
        variable: string;
    } | "self";
    conditions?: Condition[];
}

export type RequirementScored = Omit<Requirement, "query" | "conditions"> & {
    enabled: boolean;
};

export interface Prerequisite {
    conditions: Condition[];
}

export type PrerequisiteScored = Prerequisite & {
    enabled: boolean;
};

export interface ScoreDef {
    title: string;
    description: string;
    prerequisites?: Prerequisite;
    scores?: ScoreDefObj;
    requirements?: Requirement[];
}

export type ScoreValue = Omit<ScoreDef, "scores" | "prerequisites" | "requirements"> & {
    value: number;
    max: number;
    scores?: ScoreValueObj;
    prerequisites?: PrerequisiteScored;
    requirements?: RequirementScored[];
};

export interface ScoreDefObj {
    [key: string]: ScoreDef;
}

export interface TopScoreValueObj {
    version: string;
    created: string;
    refResource: string;
    scores: ScoreValueObj;
}

export interface ScoreValueObj {
    [key: string]: ScoreValue;
}

export interface SPARQLResultsJSON {
    head: {
        vars?: string[];
        link?: string[];
    };
    results?: {
        bindings: Record<string, {
            "type": "uri" | "literal" | "bnode";
            "value": string;
            "xml:lang"?: string;
            "datatype"?: string;
        }>[];
    };
    boolean?: boolean;
}
