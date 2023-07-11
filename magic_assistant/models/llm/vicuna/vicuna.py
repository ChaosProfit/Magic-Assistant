from loguru import logger
import torch

try:
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        LlamaTokenizer,
        LlamaForCausalLM,
        AutoModel,
        AutoModelForSeq2SeqLM,
    )
except ImportError:
    from transformers import (
        AutoTokenizer,
        AutoModelForCausalLM,
        LLaMATokenizer,
        LLamaForCausalLM,
        AutoModel,
        AutoModelForSeq2SeqLM,
    )

from magic_assistant.models.llm.base_llm import BaseLlm
from magic_assistant.models.llm.vicuna.conversation import (
    get_default_conv_template,
    compute_skip_echo_len,
    SeparatorStyle,
)
from magic_assistant.models.llm.vicuna.compression import compress_module
from magic_assistant.models.llm.vicuna.chatio import RichChatIO

class Vicuna(BaseLlm):
    model_path: str
    load_8bit: bool = True

    _device: str = "cuda"
    _model: any = None
    _tokenizer: any = None
    _max_new_tokens: int = 2048
    _temperature: float = 0.7

    _num_gpus: int = 1
    _max_gpu_memory: any = None

# class Vicuna():
#     def __init__(self, model_path):
#         self.model_path: str = model_path
#         self.load_8bit: bool = True
#
#         self._device: str = "cuda"
#         self._model: any = None
#         self._tokenizer: any = None
#         self._max_new_tokens: int = 2048
#         self._temperature: float = 0.7
#
#         self._num_gpus: int = 1
#         self._max_gpu_memory: any = None

    def init(self):
        self._chatio = RichChatIO()

        if self._device == "cuda":
            kwargs = {"torch_dtype": torch.float16}
            num_gpus = int(self._num_gpus)
            if num_gpus != 1:
                kwargs["device_map"] = "auto"
                if self._max_gpu_memory is None:
                    kwargs[
                        "device_map"
                    ] = "sequential"  # This is important for not the same VRAM sizes
                    available_gpu_memory = self._get_gpu_memory(num_gpus)
                    kwargs["max_memory"] = {
                        i: str(int(available_gpu_memory[i] * 0.85)) + "GiB"
                        for i in range(num_gpus)
                    }
                else:
                    kwargs["max_memory"] = {i: self._max_gpu_memory for i in range(num_gpus)}
        else:
            raise ValueError(f"Invalid device: {self._device}")

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_path, use_fast=False)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_path, low_cpu_mem_usage=True, **kwargs
        )

        if self.load_8bit:
            compress_module(self._model, self._device)

        if (self._device == "cuda" and self._num_gpus == 1):
            self._model.to(self._device)

        logger.debug("vicuna init suc")

    def predict(self, input: str):
        conv = get_default_conv_template(self.model_path).copy()

        conv.append_message(conv.roles[0], input)
        conv.append_message(conv.roles[1], None)

        prompt = conv.get_prompt()

        skip_echo_len = compute_skip_echo_len(self.model_path, conv, prompt)
        stop_str = (
            conv.sep
            if conv.sep_style in [SeparatorStyle.SINGLE]
            else None
        )
        params = {
            # "model": self.model_path,
            "prompt.py": prompt,
            # "temperature": self._temperature,
            # "max_new_tokens": self._max_new_tokens,
            "stop": stop_str,
        }

        self._chatio.prompt_for_output(conv.roles[1])
        output_stream = self._generate_stream(params)
        outputs = self._chatio.stream_output(output_stream, skip_echo_len)
        # NOTE: strip is important to align with the training data.
        conv.messages[-1][-1] = outputs.strip()

        output = outputs.strip()
        logger.debug("execute suc, input:%s, output:%s" % (input, output))
        return output

    @torch.inference_mode()
    def _generate_stream(self, params, context_len=2048, stream_interval=2):
        prompt = params["prompt.py"]
        l_prompt = len(prompt)
        stop_str = params.get("stop", None)
        stop_token_ids = params.get("stop_ids", [self._tokenizer.eos_token_id])

        input_ids = self._tokenizer(prompt).input_ids
        output_ids = list(input_ids)

        max_src_len = context_len - self._max_new_tokens - 8
        input_ids = input_ids[-max_src_len:]

        for i in range(self._max_new_tokens):
            if i == 0:
                out = self._model(torch.as_tensor([input_ids], device=self._device), use_cache=True)
                logits = out.logits
                past_key_values = out.past_key_values
            else:
                out = self._model(
                    input_ids=torch.as_tensor([[token]], device=self._device),
                    use_cache=True,
                    past_key_values=past_key_values,
                )
                logits = out.logits
                past_key_values = out.past_key_values

            last_token_logits = logits[0][-1]

            if self._temperature < 1e-4:
                token = int(torch.argmax(last_token_logits))
            else:
                probs = torch.softmax(last_token_logits / self._temperature, dim=-1)
                token = int(torch.multinomial(probs, num_samples=1))

            output_ids.append(token)

            if token in stop_token_ids:
                stopped = True
            else:
                stopped = False

            if i % stream_interval == 0 or i == self._max_new_tokens - 1 or stopped:
                output = self._tokenizer.decode(output_ids, skip_special_tokens=True)
                if stop_str:
                    pos = output.rfind(stop_str, l_prompt)
                    if pos != -1:
                        output = output[:pos]
                        stopped = True
                yield output

            if stopped:
                break

        del past_key_values

    def _get_gpu_memory(self, max_gpus=None):
        gpu_memory = []
        num_gpus = (
            torch.cuda.device_count()
            if max_gpus is None
            else min(max_gpus, torch.cuda.device_count())
        )

        for gpu_id in range(num_gpus):
            with torch.cuda.device(gpu_id):
                device = torch.cuda.current_device()
                gpu_properties = torch.cuda.get_device_properties(device)
                total_memory = gpu_properties.total_memory / (1024**3)
                allocated_memory = torch.cuda.memory_allocated() / (1024**3)
                available_memory = total_memory - allocated_memory
                gpu_memory.append(available_memory)
        return gpu_memory

if __name__ == "__main__":
    vicuna_adapter = Vicuna(model_path="/opt/mojing/Models/public/vicuna-13b-v1.3")
    vicuna_adapter.init()
    vicuna_adapter.predict("who are you")