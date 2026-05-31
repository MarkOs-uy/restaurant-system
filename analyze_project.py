import os
import ast
from datetime import datetime

EXCLUDE_DIRS = {"venv", "__pycache__", ".git", ".idea", ".vscode", "node_modules"}
OUTPUT_FILE = "PROJECT_SUMMARY.md"
INCLUDE_CODE = True  # Cambia a True si quieres incluir el código completo

def analyze_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except:
            return None

    functions = []
    classes = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)
        elif isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            for n in node.names:
                imports.append(f"{module}.{n.name}")

    return {
        "functions": functions,
        "classes": classes,
        "imports": imports,
    }

def build_tree(root):
    tree = []
    for root_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        level = root_dir.replace(root, "").count(os.sep)
        indent = "  " * level
        tree.append(f"{indent}- {os.path.basename(root_dir)}/")

        subindent = "  " * (level + 1)
        for f in files:
            if f.endswith(".py"):
                tree.append(f"{subindent}- {f}")
    return "\n".join(tree)

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"# 📊 Project Summary\n")
        out.write(f"Generated: {datetime.now()}\n\n")

        out.write("## 📁 Estructura del proyecto\n\n")
        out.write("```\n")
        out.write(build_tree("."))
        out.write("\n```\n\n")

        out.write("## 📄 Archivos analizados\n\n")

        for root_dir, dirs, files in os.walk("."):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root_dir, file)
                    analysis = analyze_file(path)

                    if not analysis:
                        continue

                    out.write(f"### {path}\n\n")

                    out.write(f"**Funciones ({len(analysis['functions'])}):**\n")
                    for fn in analysis["functions"]:
                        out.write(f"- {fn}\n")

                    out.write(f"\n**Clases ({len(analysis['classes'])}):**\n")
                    for cl in analysis["classes"]:
                        out.write(f"- {cl}\n")

                    out.write(f"\n**Imports ({len(analysis['imports'])}):**\n")
                    for im in analysis["imports"]:
                        out.write(f"- {im}\n")

                    if INCLUDE_CODE:
                        with open(path, "r", encoding="utf-8") as f:
                            out.write("\n```python\n")
                            out.write(f.read())
                            out.write("\n```\n")

                    out.write("\n---\n\n")

    print(f"✅ Archivo generado: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()