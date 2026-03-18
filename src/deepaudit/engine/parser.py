import tree_sitter_python as tspy
from tree_sitter import Language, Parser

def get_ast_metadata(code_content):
    # 1. Setup the Python Language & Parser
    PY_LANGUAGE = Language(tspy.language())
    parser = Parser(PY_LANGUAGE)
    
    # 2. Parse the code
    tree = parser.parse(bytes(code_content, "utf8"))
    root_node = tree.root_node

    libraries = []
    
    # 3. Define the Query
    query_text = """
        (import_statement name: (dotted_name) @import)
        (import_from_statement module_name: (dotted_name) @import)
    """
    query = PY_LANGUAGE.query(query_text)
    
    # 4. Execute the Query correctly for v0.21+
    # In the new API, we call query.captures() and pass the node
    captures = query.captures(root_node)
    
    # captures is a dictionary of { tag_name: [list_of_nodes] }
    # We iterate through the 'import' tag we defined in the query_text
    if 'import' in captures:
        for node in captures['import']:
            lib_name = code_content[node.start_byte:node.end_byte]
            # Split to get the base package (e.g., 'os.path' -> 'os')
            libraries.append(lib_name.split('.')[0])

    # Let's also grab function names for the Logic Scanner
    func_query = PY_LANGUAGE.query("(function_definition name: (identifier) @func)")
    func_captures = func_query.captures(root_node)
    functions = []
    if 'func' in func_captures:
        for node in func_captures['func']:
            functions.append(code_content[node.start_byte:node.end_byte])

    return {
        "libraries": list(set(libraries)),
        "functions": functions,
        "tree": tree
    }