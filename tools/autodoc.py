import sys
import os
from pathlib import Path
from src.engine.parser import CodeParser
from src.utils.logger import get_logger

logger = get_logger("AUTODOC")

class AutodocAgent:
    def __init__(self, src_root="src", output_file="docs/API.md"):
        self.src_root = Path(src_root)
        self.output_file = Path(output_file)
        self.registry = {}

    def extract_docstring(self, node):
        """Clean the raw bytes from Tree-sitter into a readable string."""
        if not node: return "No documentation provided."
        raw = node.text.decode('utf-8').strip('"').strip("'")
        return raw.strip()

    def process_file(self, file_path):
        """Uses CodeParser to map a single file's API."""
        parser = CodeParser(str(file_path))
        root = parser.parse()
        
        # v0.3.0 Logic: Query the AST for definitions
        # (Simplified for implementation - uses the SCM logic above)
        module_data = {"classes": [], "functions": []}
        
        # Iterate through root.children to find definitions...
        # [Implementation of Query Execution Here]
        
        return module_data

    def render_markdown(self):
        """Aggregates all module_data into the final Codex."""
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write("# 💎 DeepAudit API Codex (v0.3.0)\n\n")
            for path, data in self.registry.items():
                f.write(f"## 📦 Module: `{path}`\n\n")
                # ... Loop through data and write Tables/Sections ...

    def run(self):
        logger.info(f"🚀 Starting Autodoc crawl in {self.src_root}")
        py_files = [p for p in self.src_root.rglob("*.py") if "__" not in p.name]
        
        for pf in py_files:
            logger.info(f"Mapping: {pf}")
            self.registry[str(pf)] = self.process_file(pf)
            
        self.render_markdown()
        logger.info(f"✅ Codex generated at {self.output_file}")

if __name__ == "__main__":
    agent = AutodocAgent()
    agent.run()