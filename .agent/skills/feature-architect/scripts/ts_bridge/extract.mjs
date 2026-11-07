#!/usr/bin/env node
/**
 * Opportunistic TypeScript Compiler AST extractor (`extract.mjs`).
 * Uses the target project's own `typescript` library when present; emits deterministic JSON.
 */
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

function parseArgs(argv) {
  const out = { tsLib: "", root: "", filesJson: "" };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--ts-lib") out.tsLib = argv[++i] || "";
    else if (argv[i] === "--root") out.root = argv[++i] || "";
    else if (argv[i] === "--files-json") out.filesJson = argv[++i] || "";
  }
  return out;
}

const args = parseArgs(process.argv);
if (!args.tsLib || !args.root || !args.filesJson) {
  process.stderr.write("Missing required arguments --ts-lib --root --files-json\n");
  process.exit(2);
}

const require = createRequire(import.meta.url);
const ts = require(path.resolve(args.tsLib));
const files = JSON.parse(fs.readFileSync(args.filesJson, "utf8"));

const result = {
  derivation: "ast",
  components: [],
  jsx_usages: [],
  interfaces: [],
  http_calls: [],
  dead_controls: [],
  hardcoded_arrays: [],
};

function lineOf(sf, pos) {
  return sf.getLineAndCharacterOfPosition(pos).line + 1;
}

for (const relFile of files) {
  const absPath = path.resolve(args.root, relFile);
  let content = "";
  try {
    content = fs.readFileSync(absPath, "utf8");
  } catch {
    continue;
  }
  const kind = relFile.endsWith(".tsx") || relFile.endsWith(".jsx") ? ts.ScriptKind.TSX : ts.ScriptKind.TS;
  const sf = ts.createSourceFile(relFile, content, ts.ScriptTarget.Latest, true, kind);

  const ifaceMap = new Map();

  function visit(node) {
    if (ts.isInterfaceDeclaration(node)) {
      const name = node.name.text;
      const fields = [];
      for (const member of node.members) {
        if (ts.isPropertySignature(member) && member.name) {
          const propName = member.name.getText(sf);
          const optional = Boolean(member.questionToken);
          const typeText = member.type ? member.type.getText(sf) : "unknown";
          fields.push({ name: propName, optional, type: typeText, line: lineOf(sf, member.getStart(sf)) });
        }
      }
      ifaceMap.set(name, fields);
      result.interfaces.push({ name, file: relFile, line: lineOf(sf, node.getStart(sf)), fields });
    }

    if (ts.isFunctionDeclaration(node) && node.name && /^[A-Z]/.test(node.name.text)) {
      const compName = node.name.text;
      let propTypeName = null;
      if (node.parameters.length > 0 && node.parameters[0].type) {
        propTypeName = node.parameters[0].type.getText(sf).trim();
      }
      const textBody = node.body ? node.body.getText(sf) : "";
      result.components.push({
        name: compName,
        file: relFile,
        line: lineOf(sf, node.getStart(sf)),
        prop_type: propTypeName,
        has_state: /\buseState\s*\(/.test(textBody),
        has_api: /\b(useQuery|useMutation|fetch|axios|apiClient|[A-Za-z0-9_]*Api\.)/.test(textBody),
        bound_handlers: Array.from(textBody.matchAll(/onClick\s*=\s*\{\s*([A-Za-z0-9_]+)\s*\}/g)).map((m) => m[1]),
      });
    }

    if (ts.isVariableStatement(node)) {
      for (const decl of node.declarationList.declarations) {
        if (ts.isIdentifier(decl.name) && decl.initializer) {
          const varName = decl.name.text;
          if (ts.isArrayLiteralExpression(decl.initializer) && decl.initializer.elements.length >= 2) {
            const allObjects = decl.initializer.elements.every((el) => ts.isObjectLiteralExpression(el));
            if (allObjects) {
              result.hardcoded_arrays.push({
                name: varName,
                file: relFile,
                line: lineOf(sf, decl.getStart(sf)),
                count: decl.initializer.elements.length,
                excerpt: decl.getText(sf).split(/\r?\n/)[0].slice(0, 140),
              });
            }
          }
        }
      }
    }

    if (ts.isJsxOpeningElement(node) || ts.isJsxSelfClosingElement(node)) {
      const tagName = node.tagName.getText(sf);
      const attrs = [];
      let hasSpread = false;
      const attrValues = {};
      for (const prop of node.attributes.properties) {
        if (ts.isJsxSpreadAttribute(prop)) {
          hasSpread = true;
        } else if (ts.isJsxAttribute(prop) && prop.name) {
          const aName = prop.name.getText(sf);
          attrs.push(aName);
          attrValues[aName] = prop.initializer ? prop.initializer.getText(sf) : "true";
        }
      }
      if (/^[A-Z]/.test(tagName)) {
        result.jsx_usages.push({
          component: tagName,
          file: relFile,
          line: lineOf(sf, node.getStart(sf)),
          passed_props: attrs,
          has_spread: hasSpread,
          excerpt: node.getText(sf).split(/\r?\n/)[0].slice(0, 140),
        });
      }
      if (tagName === "a" && (attrValues.href === '"#"' || attrValues.href === "'#'" || attrValues.href === '{`#`}')) {
        result.dead_controls.push({
          tag: "a",
          file: relFile,
          line: lineOf(sf, node.getStart(sf)),
          reason: "anchor_hash_href",
          excerpt: node.getText(sf).split(/\r?\n/)[0].slice(0, 140),
        });
      }
      if (tagName === "button" && attrValues.onClick && /\(\s*\)\s*=>\s*\{\s*\}/.test(attrValues.onClick)) {
        result.dead_controls.push({
          tag: "button",
          file: relFile,
          line: lineOf(sf, node.getStart(sf)),
          reason: "empty_onclick_handler",
          excerpt: node.getText(sf).split(/\r?\n/)[0].slice(0, 140),
        });
      }
    }

    if (ts.isCallExpression(node)) {
      const exprText = node.expression.getText(sf);
      const m = exprText.match(/(?:^|\.)(get|post|put|patch|delete|fetch)$/i);
      if (m && node.arguments.length >= 1) {
        const firstArg = node.arguments[0].getText(sf).replace(/^['"`]|['"`]$/g, "");
        if (firstArg.startsWith("/") || firstArg.startsWith("http")) {
          const typeArg = node.typeArguments && node.typeArguments.length > 0 ? node.typeArguments[0].getText(sf) : null;
          result.http_calls.push({
            method: m[1].toUpperCase() === "FETCH" ? "GET" : m[1].toUpperCase(),
            path: firstArg,
            response_type: typeArg,
            file: relFile,
            line: lineOf(sf, node.getStart(sf)),
            excerpt: node.getText(sf).split(/\r?\n/)[0].slice(0, 140),
          });
        }
      }
    }

    ts.forEachChild(node, visit);
  }

  visit(sf);
}

process.stdout.write(JSON.stringify(result));
