import toml
import os

def generate_requirements(pyproject_path="pyproject.toml", output_file="requirements.txt"):
    """
    Generates a requirements.txt file from pyproject.toml dependencies.
    
    :param pyproject_path: Path to the pyproject.toml file.
    :param output_file: Output requirements.txt file path.
    """
    if not os.path.exists(pyproject_path):
        print(f"Error: {pyproject_path} not found.")
        return

    # Load pyproject.toml
    with open(pyproject_path, "r") as file:
        pyproject_data = toml.load(file)

    # Extract dependencies
    dependencies = pyproject_data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    dev_dependencies = pyproject_data.get("tool", {}).get("poetry", {}).get("dev-dependencies", {})

    # Remove Python version constraint if present
    if "python" in dependencies:
        del dependencies["python"]

    # Combine dependencies
    all_dependencies = {**dependencies, **dev_dependencies}

    # Write requirements.txt
    with open(output_file, "w") as file:
        for package, version in all_dependencies.items():
            if isinstance(version, dict):  # Handle extras or markers
                file.write(f"{package} {version.get('version', '')}\n")
            else:
                file.write(f"{package}=={version}\n")

    print(f"Requirements saved to {output_file}")

if __name__ == "__main__":
    generate_requirements()
