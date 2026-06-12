"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    if "[TODO]" in system_prompt:
        errors.append("system_prompt contém [TODO]")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurada no .env")
        return False

    system_text = prompt_data.get("system_prompt", "")
    user_text = prompt_data.get("user_prompt", "{bug_report}")

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_text),
        ("human", user_text),
    ])

    full_name = f"{username}/{prompt_name}"

    print(f"Publicando prompt: {full_name}")

    hub.push(
        full_name,
        prompt_template,
        new_repo_is_public=True,
        new_repo_description=prompt_data.get("description", ""),
    )

    print(f"✓ Prompt publicado com sucesso: {full_name}")
    print(f"  Acesse em: https://smith.langchain.com/prompts/{prompt_name}")
    return True


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS PARA O LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    yaml_path = "prompts/bug_to_user_story_v2.yml"

    print(f"Carregando prompt de: {yaml_path}")
    data = load_yaml(yaml_path)

    if not data:
        print(f"❌ Não foi possível carregar: {yaml_path}")
        return 1

    prompt_key = "bug_to_user_story_v2"
    prompt_data = data.get(prompt_key, {})

    if not prompt_data:
        print(f"❌ Chave '{prompt_key}' não encontrada no YAML")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Prompt inválido:")
        for err in errors:
            print(f"   - {err}")
        return 1

    print("✓ Prompt validado com sucesso")

    success = push_prompt_to_langsmith(prompt_key, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
