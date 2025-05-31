import json
import os
import openai
from dotenv import load_dotenv
from groq import Groq

class Antares:
    def __init__(self, config_path="antares.json"):
        load_dotenv()
        self.config = self.load_config(config_path)
        self.openai = openai
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.cerebras = openai.OpenAI(
            api_key=os.getenv("CEREBRAS_API_KEY"),
            base_url="https://api.cerebras.ai/v1",
        )
        self.sambanova = openai.OpenAI(
            api_key=os.getenv("SAMBANOVA_API_KEY"),
            base_url="https://api.sambanova.ai/v1",
        )
        self.openrouter = openai.OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    def load_config(self, config_path):
        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Join the script directory with the config file name
        full_config_path = os.path.join(script_dir, config_path)

        if not os.path.exists(full_config_path):
            print(f"Warning: Configuration file {full_config_path} not found. Using default configuration.")
            return {}  # Return an empty dictionary or a default configuration
        with open(full_config_path, "r") as config_file:
            return json.load(config_file)
