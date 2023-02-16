from pathlib import Path

import mkdocs_gen_files

src_dir = "mdtc"
doc_dir = "docs"

for path in sorted(Path(src_dir).rglob("*.py")):
    module_path = path.relative_to(src_dir).with_suffix("")
    doc_path = path.relative_to(src_dir).with_suffix(".md")
    full_doc_path = Path(doc_dir, doc_path)

    parts = (src_dir, *module_path.parts)

    match parts[-1]:
        case "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name(f"{parts[-1]}.md")
            full_doc_path = full_doc_path.with_name(f"{parts[-1]}.md")
        case "__main__":
            continue

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        fd.write(f"::: {identifier}")

    mkdocs_gen_files.set_edit_path(full_doc_path, path)
