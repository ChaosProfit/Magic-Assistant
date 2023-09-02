from magic_assistant.config.base_config import BaseConfig


class AgentConfig(BaseConfig):
    max_loop_count: int = 0
    output_intermediate_steps: bool = True
    user_confirm_and_adjust: bool = False
    memory_size: int = 0
