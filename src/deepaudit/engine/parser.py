import tree_sitter_python as tspy
from tree_sitter import Language, Parser

def get_ast_metadata(code_content):
    # 1. Setup Parser & Language
    PY_LANGUAGE = Language(tspy.language())
    parser = Parser(PY_LANGUAGE)
    
    # 2. Parse Code
    tree = parser.parse(bytes(code_content, "utf8"))
    root_node = tree.root_node

    libraries = []
    functions = []

    # 3. Define the Query Text
    query_text = """
        (import_statement name: (dotted_name) @import)
        (import_from_statement module_name: (dotted_name) @import)
        (function_definition name: (identifier) @func)
    """
    
    try:
        # In the newest API, we create the query from the language
        query = PY_LANGUAGE.query(query_text)
        
        # This is the line that usually breaks. 
        # If query.captures(root_node) fails, we use the Cursor method.
        try:
            captures = query.captures(root_node)
        except AttributeError:
            # Fallback for ultra-new 2026 versions
            from tree_sitter import Query
            captures = query.run(root_node)

        # Iterate through the results
        for node, tag in captures:
            content = code_content[node.start_byte:node.end_byte]
            
            if tag == "import":
                libraries.append(content.split('.')[0])
            elif tag == "func":
                functions.append(content)

    except Exception as e:
        # If this STILL fails, we use a "No-Query" fallback so you can at least see the MVP
        print(f"⚠️ AST Query Error: {e}. Switching to basic scan.")
        import re
        libraries = re.findall(r"import\s+([\w\.]+)", code_content)
        functions = re.findall(r"def\s+(\w+)", code_content)

    return {
        "libraries": list(set(libraries)),
        "functions": functions,
        "tree": tree
    }