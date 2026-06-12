"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 do LangSmith Hub e salva localmente."""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False

    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = "prompts/bug_to_user_story_v1.yml"

    print(f"Puxando prompt: {prompt_name}")

    try:
        prompt = hub.pull(prompt_name)
        print("✓ Prompt carregado com sucesso")

        system_prompt = ""
        user_prompt = ""

        for msg in prompt.messages:
            type_name = type(msg).__name__
            template = msg.prompt.template if hasattr(msg, "prompt") else str(msg)

            if "System" in type_name:
                system_prompt = template
            elif "Human" in type_name:
                user_prompt = template

        data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "pulled_from": prompt_name,
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        if save_yaml(data, output_path):
            print(f"✓ Prompt salvo em: {output_path}")
            return True

        return False

    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
