# OpenAPI type generator

`make setup` installs this tool's lockfile; `make types` exports the FastAPI schema
without starting a server or opening a database, then regenerates
`web/src/api/schema.d.ts`. Never edit the generated file by hand.

The generator is isolated here because openapi-typescript 7 requires TypeScript 5,
while the web application uses TypeScript 6. This keeps both supported dependency
trees and avoids the outdated transitive dependencies of openapi-typescript 6.
