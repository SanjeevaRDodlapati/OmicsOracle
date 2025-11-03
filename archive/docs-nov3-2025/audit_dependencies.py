#!/usr/bin/env python3
"""
Audit Python dependencies and identify unused packages.

This script:
1. Scans all Python files for import statements
2. Compares with installed packages in requirements.txt
3. Identifies unused/redundant dependencies
4. Generates clean requirements files
"""

import ast
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class DependencyAuditor:
    """Audit dependencies in the codebase."""

    # Packages that are development/test only
    DEV_PACKAGES = {
        "pytest",
        "pytest-asyncio",
        "pytest-cov",
        "pytest-mock",
        "pytest-env",
        "pytest-xdist",
        "pytest-timeout",
        "faker",
        "factory-boy",
        "black",
        "flake8",
        "mypy",
        "isort",
        "pre-commit",
        "bandit",
        "safety",
        "ipdb",
        "pdbpp",
        "ipython",
        "jupyter",
        "notebook",
        "memory-profiler",
        "line-profiler",
        "coverage",
        "mkdocs",
        "mkdocs-material",
        "mkdocs-mermaid2-plugin",
        "sphinx",
        "sphinx-rtd-theme",
        "autopep8",
        "ruff",
    }

    # Standard library modules that aren't packages
    STDLIB_MODULES = {
        "abc",
        "asyncio",
        "argparse",
        "base64",
        "collections",
        "contextlib",
        "copy",
        "csv",
        "dataclasses",
        "datetime",
        "decimal",
        "enum",
        "functools",
        "hashlib",
        "http",
        "io",
        "itertools",
        "json",
        "logging",
        "math",
        "os",
        "pathlib",
        "pickle",
        "random",
        "re",
        "shutil",
        "socket",
        "sqlite3",
        "ssl",
        "string",
        "subprocess",
        "sys",
        "tempfile",
        "threading",
        "time",
        "traceback",
        "typing",
        "unittest",
        "urllib",
        "uuid",
        "warnings",
        "weakref",
        "xml",
        "zipfile",
    }

    # Package name mappings (import name → package name)
    PACKAGE_MAPPINGS = {
        "PIL": "pillow",
        "bs4": "beautifulsoup4",
        "cv2": "opencv-python",
        "dotenv": "python-dotenv",
        "jose": "python-jose",
        "sklearn": "scikit-learn",
        "yaml": "pyyaml",
        "Bio": "biopython",
        "OpenSSL": "pyopenssl",
        "dateutil": "python-dateutil",
        "requests_oauthlib": "requests-oauthlib",
        "oauthlib": "oauthlib",
        "multipart": "python-multipart",
        "engineio": "python-engineio",
        "socketio": "python-socketio",
    }

    def __init__(self, project_root: Path):
        """Initialize auditor."""
        self.project_root = project_root
        self.imported_modules: Set[str] = set()
        self.installed_packages: Dict[str, str] = {}

    def scan_imports(self, directory: Path = None) -> Set[str]:
        """Scan all Python files for import statements."""
        if directory is None:
            directory = self.project_root

        imports = set()

        # Scan Python files
        for py_file in directory.rglob("*.py"):
            # Skip archived code
            if "archive" in py_file.parts or "__pycache__" in py_file.parts:
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse AST
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.add(alias.name.split(".")[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imports.add(node.module.split(".")[0])
                except SyntaxError:
                    # Fallback to regex for syntax errors
                    import_pattern = r"^(?:from\s+(\S+)|import\s+(\S+))"
                    for match in re.finditer(import_pattern, content, re.MULTILINE):
                        module = match.group(1) or match.group(2)
                        if module:
                            imports.add(module.split(".")[0])
            except Exception as e:
                print(f"Warning: Could not process {py_file}: {e}")

        self.imported_modules = imports
        return imports

    def load_requirements(self, req_file: Path) -> Dict[str, str]:
        """Load packages from requirements.txt."""
        packages = {}

        if not req_file.exists():
            return packages

        with open(req_file, "r") as f:
            for line in f:
                line = line.strip()

                # Skip comments, empty lines, and -r includes
                if not line or line.startswith("#") or line.startswith("-r"):
                    continue

                # Skip -e editable installs
                if line.startswith("-e"):
                    continue

                # Skip URLs (spacy models, etc.)
                if line.startswith("http://") or line.startswith("https://"):
                    # Extract package name from URL
                    match = re.search(r"([a-zA-Z0-9_-]+)-\d+", line)
                    if match:
                        packages[match.group(1).lower()] = line
                    continue

                # Parse package==version or package>=version
                match = re.match(r"^([a-zA-Z0-9_-]+)", line)
                if match:
                    pkg_name = match.group(1).lower()
                    packages[pkg_name] = line

        self.installed_packages = packages
        return packages

    def get_package_name(self, import_name: str) -> str:
        """Convert import name to package name."""
        # Check direct mappings first
        if import_name in self.PACKAGE_MAPPINGS:
            return self.PACKAGE_MAPPINGS[import_name]

        # Most packages match their import name
        return import_name.lower().replace("_", "-")

    def analyze(self) -> Dict[str, any]:
        """Analyze dependencies and return report."""
        print("\n" + "=" * 80)
        print("DEPENDENCY AUDIT REPORT")
        print("=" * 80)

        # Scan imports
        print(f"\n1. Scanning Python files in {self.project_root}...")
        imports = self.scan_imports()
        print(f"   Found {len(imports)} unique top-level imports")

        # Load requirements
        req_file = self.project_root / "requirements" / "requirements.txt"
        print(f"\n2. Loading requirements from {req_file}...")
        packages = self.load_requirements(req_file)
        print(f"   Found {len(packages)} packages in requirements.txt")

        # Filter out stdlib and local modules
        third_party_imports = imports - self.STDLIB_MODULES
        third_party_imports = {
            imp for imp in third_party_imports if not imp.startswith("omics_oracle")
        }

        print(f"\n3. Filtering out standard library modules...")
        print(f"   {len(third_party_imports)} third-party imports detected")

        # Map imports to packages
        used_packages = set()
        for imp in third_party_imports:
            pkg = self.get_package_name(imp)
            used_packages.add(pkg)

        # Find unused packages
        installed_pkg_names = set(packages.keys())
        unused_packages = installed_pkg_names - used_packages - self.DEV_PACKAGES

        # Find missing packages (imported but not in requirements)
        missing_packages = used_packages - installed_pkg_names

        # Generate report
        report = {
            "total_imports": len(imports),
            "third_party_imports": len(third_party_imports),
            "installed_packages": len(packages),
            "used_packages": len(used_packages),
            "unused_packages": len(unused_packages),
            "missing_packages": len(missing_packages),
            "unused_list": sorted(unused_packages),
            "missing_list": sorted(missing_packages),
            "used_list": sorted(used_packages),
        }

        return report

    def print_report(self, report: Dict):
        """Print formatted report."""
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total imports found:        {report['total_imports']}")
        print(f"Third-party imports:        {report['third_party_imports']}")
        print(f"Installed packages:         {report['installed_packages']}")
        print(f"Used packages:              {report['used_packages']}")
        print(f"Unused packages:            {report['unused_packages']}")
        print(f"Missing packages:           {report['missing_packages']}")

        if report["unused_list"]:
            print("\n" + "=" * 80)
            print("POTENTIALLY UNUSED PACKAGES")
            print("=" * 80)
            print("These packages are in requirements.txt but not imported:\n")
            for pkg in report["unused_list"]:
                print(f"  - {pkg}")
            print(
                "\n⚠️  WARNING: Some may be used indirectly (dependencies of other packages)"
            )
            print("   Always test thoroughly after removing packages!")

        if report["missing_list"]:
            print("\n" + "=" * 80)
            print("MISSING PACKAGES")
            print("=" * 80)
            print("These modules are imported but not in requirements.txt:\n")
            for pkg in report["missing_list"]:
                print(f"  - {pkg}")
            print("\n💡 These might be:")
            print("   - Sub-packages of other packages")
            print("   - Incorrectly mapped import names")
            print("   - Actually missing dependencies")

    def generate_clean_requirements(self, output_file: Path):
        """Generate clean requirements.txt with only used packages."""
        print(f"\n" + "=" * 80)
        print(f"GENERATING CLEAN REQUIREMENTS: {output_file}")
        print("=" * 80)

        # Get used packages
        used_packages = set()
        for imp in self.imported_modules - self.STDLIB_MODULES:
            if not imp.startswith("omics_oracle"):
                pkg = self.get_package_name(imp)
                used_packages.add(pkg)

        # Write clean requirements
        clean_reqs = []
        for pkg in sorted(used_packages):
            if pkg in self.installed_packages:
                clean_reqs.append(self.installed_packages[pkg])
            else:
                # Package not in original requirements, add without version
                clean_reqs.append(pkg)

        with open(output_file, "w") as f:
            f.write("# Production dependencies (auto-generated)\n")
            f.write("# Generated by scripts/audit_dependencies.py\n\n")
            for req in clean_reqs:
                f.write(f"{req}\n")

        print(f"✅ Wrote {len(clean_reqs)} packages to {output_file}")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent

    auditor = DependencyAuditor(project_root)

    # Run analysis
    report = auditor.analyze()
    auditor.print_report(report)

    # Ask to generate clean requirements
    print("\n" + "=" * 80)
    response = input("\nGenerate clean requirements.txt? (y/N): ")
    if response.lower() == "y":
        output_file = project_root / "requirements" / "requirements-clean.txt"
        auditor.generate_clean_requirements(output_file)
        print(f"\n✅ Review the file and rename to requirements.txt if satisfied")

    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print("1. Review unused packages carefully")
    print("2. Some packages may be indirect dependencies")
    print("3. Test thoroughly after removing packages")
    print("4. Use 'pipdeptree' to see dependency tree")
    print("5. Consider using 'pip-tools' for better dependency management")
    print("\n")


if __name__ == "__main__":
    main()
