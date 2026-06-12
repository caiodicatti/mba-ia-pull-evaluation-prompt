"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


class TestPrompts:
    def setup_method(self):
        data = load_prompts(str(PROMPT_FILE))
        self.prompt = data.get("bug_to_user_story_v2", {})
        self.system_prompt = self.prompt.get("system_prompt", "")

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in self.prompt, "Campo 'system_prompt' ausente no YAML"
        assert self.system_prompt.strip() != "", "system_prompt está vazio"

    def test_prompt_has_role_definition(self):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        role_keywords = ["Você é um", "Você é uma", "Product Manager", "PM Sênior"]
        assert any(kw in self.system_prompt for kw in role_keywords), (
            "O prompt não define uma persona/role. "
            f"Esperado um dos termos: {role_keywords}"
        )

    def test_prompt_mentions_format(self):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        format_keywords = ["Markdown", "User Story", "Como um", "Critérios de Aceitação"]
        assert any(kw in self.system_prompt for kw in format_keywords), (
            "O prompt não menciona o formato de saída esperado. "
            f"Esperado um dos termos: {format_keywords}"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        few_shot_keywords = ["Exemplo", "exemplo", "Entrada", "Bug Report", "Saída"]
        assert any(kw in self.system_prompt for kw in few_shot_keywords), (
            "O prompt não contém exemplos Few-shot. "
            f"Esperado um dos termos: {few_shot_keywords}"
        )

    def test_prompt_no_todos(self):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        full_text = str(self.prompt)
        assert "[TODO]" not in full_text, "O prompt contém '[TODO]' não resolvido"

    def test_minimum_techniques(self):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = self.prompt.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}. "
            f"Técnicas: {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
