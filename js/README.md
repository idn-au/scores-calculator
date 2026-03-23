# JavaScript Scoring Calculator

## Install
Run (requires GitHub token auth as this package is hosted on GitHub's NPM registry)

```bash
npm install @idn-au/scores-calculator-js
```

## Use

```javascript
import { ScoreCalculator } from "@idn-au/scores-calculator-js";

// define your own SPARQL function(s)
function askQuery(...) {...}
function sparqlQuery(...) {...}

const scoring = await ScoreCalculator.init(["fair"]);
const score = scoring.score("https://example.com/resource", "fair", "json", askQuery, sparqlQuery);
```

## Development
Install dependencies (requires PNPM):

```bash
pnpm install
```

Run locally

```bash
pnpm dev
```
