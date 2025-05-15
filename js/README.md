# JavaScript Scoring Implementation

## Install
Run (requires GitHub token auth as this package is hosted on GitHub's NPM registry)

```bash
npm install @idn-au/scores-calculator-js
```

## Use

```javascript
import { Scoring } from "@idn-au/scores-calculator-js";

const data = "<sdkjlhsd> <sdlkflksdf> <lksdjflksdf>";

const scoring = await Scoring.init(["fair"], {value: data, format: "n-triples"});
const score = scoring.score("https://example.com/resource", "fair");
```

You can also provide your own Oxigraph Store if you have one instead of passing string data and the scoring library will use that Store instead of creating its own.

## Development
Install dependencies (requires PNPM):

```bash
pnpm install
```

Run locally

```bash
pnpm dev
```