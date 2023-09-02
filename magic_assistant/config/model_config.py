from magic_assistant.config.base_config import BaseConfig

class LlmConfig(BaseConfig):
    model_type: str = ""
    model_path: str = ""

class TextEmbeddingConfig(BaseConfig):
    model_path: str = ""

class ModelConfig():
    llm: LlmConfig = LlmConfig()
    text_embedding: TextEmbeddingConfig = TextEmbeddingConfig()

    def parse(self, model_config_dict: dict):
        self.llm.parse(model_config_dict["llm"])
        self.text_embedding.parse(model_config_dict["embedding"]["text"])
