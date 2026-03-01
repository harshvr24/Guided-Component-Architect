# backend/cli.py

import sys
from backend.agent import ComponentAgent
from backend.exporter import export_component

def main():
    prompt = " ".join(sys.argv[1:])
    agent = ComponentAgent()

    result = agent.run(prompt)

    print("\nGeneration successful.\n")

    export_dir = export_component(result)
    print(f"Exported to folder: {export_dir}")

if __name__ == "__main__":
    main()