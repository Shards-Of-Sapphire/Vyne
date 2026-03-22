import os
from deepaudit.engine.parser import CodeParser
# Assuming you'll use an API like Gemini or OpenAI here
# import google.generativeai as ai 

def generate_folder_readme(folder_path):
    """
    Scans a folder, extracts AST metadata, and generates a local README.
    """
    metadata_summary = []
    
    for file in os.listdir(folder_path):
        if file.endswith(".py") and file != "__init__.py":
            parser = CodeParser(os.path.join(folder_path, file))
            # Leveraging the work we did tonight!
            meta = parser.get_metadata()
            
            # Extracting function names from the root node for the LLM
            functions = [node.text.decode('utf8') for node in meta['root'].children if node.type == 'function_definition']
            metadata_summary.append(f"File: {file}\nFunctions: {', '.join(functions)}")

    # LLM PROMPT (The "Humane" Agent)
    prompt = f"""
    You are the Technical Writer for the Sapphire Collective. 
    Based on this AST metadata, write a professional, concise README.md for this folder.
    Include a 'Purpose' section and a 'Table of Contents' for the functions.
    
    Metadata:
    {metadata_summary}
    """
    
    # response = ai.generate(prompt)
    # with open(os.path.join(folder_path, "README.md"), "w") as f:
    #     f.write(response.text)
    print(f"✅ Generated README skeleton for {folder_path}")

if __name__ == "__main__":
    generate_folder_readme("src/deepaudit/scanners")