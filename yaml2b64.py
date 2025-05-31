import base64
import sys
import os

def yaml_to_base64(yaml_file_path):
    """
    Read a YAML file and convert its content to base64.
    
    Args:
        yaml_file_path (str): Path to the YAML file
        
    Returns:
        str: Base64 encoded content of the YAML file
    """
    try:
        # Check if file exists
        if not os.path.exists(yaml_file_path):
            raise FileNotFoundError(f"File not found: {yaml_file_path}")
        
        # Read the YAML file content
        with open(yaml_file_path, 'r', encoding='utf-8') as file:
            yaml_content = file.read()
        
        # Convert to base64
        base64_content = base64.b64encode(yaml_content.encode('utf-8')).decode('utf-8')
        
        return base64_content
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def main():
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python yaml_to_base64.py <path_to_yaml_file>")
        sys.exit(1)
    
    yaml_file_path = sys.argv[1]
    
    # Convert YAML to base64
    base64_result = yaml_to_base64(yaml_file_path)
    
    if base64_result:
        print(base64_result)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
