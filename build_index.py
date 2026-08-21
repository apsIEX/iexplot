#!/usr/bin/env python3
"""
Build a static index of the iexplot package for later wide-ranging reviews.

Walks the iexplot/ source tree with the `ast` module (no imports/execution) and
emits:
  - .iexplot_index.json : full structured index (machine-referenceable)
  - PACKAGE_INDEX.md     : human/agent-readable map

Re-run after code changes to refresh the cache:  python build_index.py
"""
import ast
import json
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PKG_DIR = os.path.join(ROOT, "iexplot")
JSON_OUT = os.path.join(ROOT, ".iexplot_index.json")
MD_OUT = os.path.join(ROOT, "PACKAGE_INDEX.md")


def first_line(docstring):
    if not docstring:
        return None
    for ln in docstring.strip().splitlines():
        ln = ln.strip()
        if ln:
            return ln
    return None


def format_signature(node):
    """Reconstruct a def signature string from an ast.arguments node."""
    a = node.args
    parts = []

    posonly = getattr(a, "posonlyargs", [])
    all_pos = posonly + a.args
    # defaults align to the tail of all_pos
    defaults = list(a.defaults)
    n_no_default = len(all_pos) - len(defaults)

    def ann(arg):
        return f": {ast.unparse(arg.annotation)}" if arg.annotation else ""

    for i, arg in enumerate(all_pos):
        s = arg.arg + ann(arg)
        di = i - n_no_default
        if di >= 0:
            s += f"={ast.unparse(defaults[di])}"
        parts.append(s)
        if posonly and i == len(posonly) - 1:
            parts.append("/")

    if a.vararg:
        parts.append("*" + a.vararg.arg + ann(a.vararg))
    elif a.kwonlyargs:
        parts.append("*")

    for arg, default in zip(a.kwonlyargs, a.kw_defaults):
        s = arg.arg + ann(arg)
        if default is not None:
            s += f"={ast.unparse(default)}"
        parts.append(s)

    if a.kwarg:
        parts.append("**" + a.kwarg.arg + ann(a.kwarg))

    return "(" + ", ".join(parts) + ")"


def decorator_names(node):
    out = []
    for d in node.decorator_list:
        try:
            out.append(ast.unparse(d))
        except Exception:
            out.append("<decorator>")
    return out


def describe_function(node):
    return {
        "name": node.name,
        "lineno": node.lineno,
        "signature": format_signature(node),
        "is_async": isinstance(node, ast.AsyncFunctionDef),
        "decorators": decorator_names(node),
        "doc": first_line(ast.get_docstring(node)),
    }


def describe_class(node):
    methods = []
    for child in node.body:
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            methods.append(describe_function(child))
    bases = []
    for b in node.bases:
        try:
            bases.append(ast.unparse(b))
        except Exception:
            bases.append("<base>")
    return {
        "name": node.name,
        "lineno": node.lineno,
        "bases": bases,
        "decorators": decorator_names(node),
        "doc": first_line(ast.get_docstring(node)),
        "methods": methods,
    }


def collect_imports(tree):
    imports = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name + (f" as {n.asname}" if n.asname else ""))
        elif isinstance(node, ast.ImportFrom):
            mod = ("." * node.level) + (node.module or "")
            names = ", ".join(
                n.name + (f" as {n.asname}" if n.asname else "") for n in node.names
            )
            imports.append(f"from {mod} import {names}")
    return imports


def module_dotted(path):
    rel = os.path.relpath(path, ROOT)
    no_ext = rel[:-3] if rel.endswith(".py") else rel
    return no_ext.replace(os.sep, ".")


def index_file(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()
    result = {
        "path": os.path.relpath(path, ROOT),
        "module": module_dotted(path),
        "loc": src.count("\n") + 1,
        "error": None,
        "doc": None,
        "imports": [],
        "classes": [],
        "functions": [],
        "constants": [],
    }
    try:
        tree = ast.parse(src, filename=path)
    except SyntaxError as e:
        result["error"] = f"SyntaxError: {e}"
        return result

    result["doc"] = first_line(ast.get_docstring(tree))
    result["imports"] = collect_imports(tree)

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            result["classes"].append(describe_class(node))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            result["functions"].append(describe_function(node))
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper():
                    result["constants"].append({"name": t.id, "lineno": node.lineno})
    return result


def build():
    files = []
    for dirpath, dirnames, filenames in os.walk(PKG_DIR):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]
        for fn in sorted(filenames):
            if fn.endswith(".py"):
                files.append(os.path.join(dirpath, fn))
    files.sort()

    modules = [index_file(p) for p in files]

    totals = {
        "modules": len(modules),
        "classes": sum(len(m["classes"]) for m in modules),
        "functions": sum(len(m["functions"]) for m in modules),
        "methods": sum(len(c["methods"]) for m in modules for c in m["classes"]),
        "loc": sum(m["loc"] for m in modules),
        "parse_errors": sum(1 for m in modules if m["error"]),
    }

    index = {
        "package": "iexplot",
        "root": os.path.relpath(PKG_DIR, ROOT),
        "generated_by": "build_index.py (ast, static)",
        "totals": totals,
        "modules": modules,
    }
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    write_markdown(index)
    return totals


def write_markdown(index):
    lines = []
    t = index["totals"]
    lines.append("# iexplot — Package Index")
    lines.append("")
    lines.append(
        "> Static AST index for wide-ranging package reviews. "
        "Regenerate with `python build_index.py`. Do not edit by hand."
    )
    lines.append("")
    lines.append(
        f"**{t['modules']}** modules · **{t['classes']}** classes · "
        f"**{t['functions']}** module-level functions · **{t['methods']}** methods · "
        f"**{t['loc']:,}** LOC"
        + (f" · ⚠ {t['parse_errors']} parse errors" if t["parse_errors"] else "")
    )
    lines.append("")

    # group modules by top-level subpackage
    groups = {}
    for m in index["modules"]:
        rel = m["path"]
        parts = rel.split(os.sep)
        group = os.sep.join(parts[1:-1]) or "(root)"  # drop leading 'iexplot'
        groups.setdefault(group, []).append(m)

    lines.append("## Contents")
    for group in sorted(groups):
        anchor = group.replace(os.sep, "").replace("(", "").replace(")", "").replace(" ", "-").lower()
        lines.append(f"- [`{group}`](#{anchor}) — {len(groups[group])} modules")
    lines.append("")

    for group in sorted(groups):
        lines.append(f"## {group}")
        lines.append("")
        for m in sorted(groups[group], key=lambda x: x["path"]):
            lines.append(f"### `{m['path']}`  ·  {m['loc']} LOC")
            if m["doc"]:
                lines.append(f"_{m['doc']}_")
            if m["error"]:
                lines.append(f"⚠ **{m['error']}**")
            lines.append("")
            for c in m["classes"]:
                base = f"({', '.join(c['bases'])})" if c["bases"] else ""
                lines.append(f"- **class `{c['name']}{base}`** — L{c['lineno']}"
                             + (f" — {c['doc']}" if c["doc"] else ""))
                for meth in c["methods"]:
                    lines.append(f"    - `{meth['name']}{meth['signature']}` — L{meth['lineno']}"
                                 + (f" — {meth['doc']}" if meth["doc"] else ""))
            for fn in m["functions"]:
                lines.append(f"- `{fn['name']}{fn['signature']}` — L{fn['lineno']}"
                             + (f" — {fn['doc']}" if fn["doc"] else ""))
            if m["constants"]:
                lines.append(f"- _constants:_ " + ", ".join(f"`{c['name']}`" for c in m["constants"]))
            lines.append("")

    with open(MD_OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    totals = build()
    print("Wrote:")
    print(" ", os.path.relpath(JSON_OUT, ROOT))
    print(" ", os.path.relpath(MD_OUT, ROOT))
    print("Totals:", json.dumps(totals))
