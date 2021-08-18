# -*- coding: utf-8 -*-
import argparse
import json
import subprocess
from collections import defaultdict


def generate_deps(project_path: str):
    process = subprocess.run(
        "go mod graph", shell=True, capture_output=True, text=True, cwd=project_path
    )
    process.check_returncode()
    deps = defaultdict(list)
    for line in process.stdout.strip().split("\n"):
        mod, req = line.split(" ")
        deps[mod].append(req)
    process = subprocess.run(
        "go mod edit -json",
        shell=True,
        capture_output=True,
        text=True,
        cwd=project_path,
    )
    process.check_returncode()
    mod_file = json.loads(process.stdout.strip())

    root = mod_file["Module"]["Path"]

    return root, deps


def print_graph_deps(root, deps):
    done = set()

    def print_indent(current_module, indent):
        if current_module not in deps:
            return
        done.add(current_module)
        for d in deps[current_module]:
            print("--" * (indent + 1) + f"> {d}")
            if d not in done:
                print_indent(d, indent + 1)

    print(root)
    print_indent(root, 0)


def reverse_dependencies(root, deps):
    reverse_deps = defaultdict(list)
    done = set()

    def append_chain(dep, chain):
        if dep not in reverse_deps:
            reverse_deps[dep] = chain
        else:
            l = len(chain)
            for existing_chain in reverse_deps[dep]:
                if len(existing_chain) == l - 1 and existing_chain == chain[:-1]:
                    existing_chain.append(chain[-1])
                    return
            reverse_deps[dep] = chain

    def inner(current_module, current_chain: list):
        done.add(current_module)
        for d in deps[current_module]:
            append_chain(d, current_chain)
            if d not in done:
                inner(d, current_chain + [d])

    inner(root, [root])
    return reverse_deps


def print_graph_reverse(root, deps, module_of_interest):
    reverse_deps = reverse_dependencies(root, deps)
    if module_of_interest is not None:
        print(reverse_deps[module_of_interest])
    else:
        print(json.dumps(reverse_deps))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("project", help="Path to the golang project to analyze.")
    parser.add_argument(
        "--reverse", "-r", help="Print reverse dependencies.", action="store_true"
    )
    parser.add_argument(
        "--module", "-m", help="Print reverse dependencies for this module."
    )
    args = parser.parse_args()

    root, deps = generate_deps(args.project)

    if args.reverse:
        print_graph_reverse(root, deps, args.module)
    else:
        print_graph_deps(root, deps)


if __name__ == "__main__":
    main()
