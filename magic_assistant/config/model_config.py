
class LlmConfig():
    model_type: str = ""
    model_path: str = ""

class TextEmbeddingConfig():
    model_path: str = ""

class ModelConfig():
    llm: LlmConfig = LlmConfig()
    text_embedding: TextEmbeddingConfig = TextEmbeddingConfig()

    def parse(self, model_config_dict: dict):
        self.llm.__dict__ = model_config_dict["llm"]
        self.text_embedding.__dict__ = model_config_dict["embedding"]["text"]
