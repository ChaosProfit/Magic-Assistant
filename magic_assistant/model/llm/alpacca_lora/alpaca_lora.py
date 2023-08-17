from loguru import logger
import torch
import transformers
from peft import PeftModel
from transformers import GenerationConfig, LlamaForCausalLM, LlamaTokenizer

from magic_assistant.model.llm.base_llm import BaseLlm
from utils.callbacks import Iteratorize, Stream

class AlpacaLora(BaseLlm):
    def __init__(self, base_model: str, lora_weights: str, load_8bit: bool=True):
        self._model = None
        self._tokenizer = None

        assert (
            base_model
        ), "Please specify a --base_model, e.g. --base_model='huggyllama/llama-7b'"

        self._tokenizer = LlamaTokenizer.from_pretrained(base_model)
        self._model = LlamaForCausalLM.from_pretrained(
            base_model,
            load_in_8bit=load_8bit,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self._model = PeftModel.from_pretrained(
            self._model,
            lora_weights,
            torch_dtype=torch.float16,
        )

        # unwind broken decapoda-research config
        self._model.config.pad_token_id = self._tokenizer.pad_token_id = 0  # unk
        self._model.config.bos_token_id = 1
        self._model.config.eos_token_id = 2

        if not load_8bit:
            self._model.half()  # seems to fix bugs for some users.

        self._model.eval()
        self._model = torch.compile(self._model)

        logger.debug("AlpacaLora init suc")

    def run(
        self,
        input="",
        temperature=0.1,
        top_p=0.75,
        top_k=40,
        num_beams=4,
        max_new_tokens=2048,
        stream_output=True,
        **kwargs,
    ):
        inputs = self._tokenizer(input, return_tensors="pt")
        input_ids = inputs["input_ids"].to("cuda")
        generation_config = GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            num_beams=num_beams,
            **kwargs,
        )
        generate_params = {
            "input_ids": input_ids,
            "generation_config": generation_config,
            "return_dict_in_generate": True,
            "output_scores": True,
            "max_new_tokens": max_new_tokens,
        }

        if stream_output:
            # Stream the reply 1 token at a time.
            # This is based on the trick of using 'stopping_criteria' to create an iterator,
            # from https://github.com/oobabooga/text-generation-webui/blob/ad37f396fc8bcbab90e11ecf17c56c97bfbd4a9c/modules/text_generation.py#L216-L243.

            def generate_with_callback(callback=None, **kwargs):
                kwargs.setdefault(
                    "stopping_criteria", transformers.StoppingCriteriaList()
                )
                kwargs["stopping_criteria"].append(
                    Stream(callback_func=callback)
                )
                with torch.no_grad():
                    self._model.generate(**kwargs)

            def generate_with_streaming(**kwargs):
                return Iteratorize(
                    generate_with_callback, kwargs, callback=None
                )

            with generate_with_streaming(**generate_params) as generator:
                for output in generator:
                    # new_tokens = len(output) - len(input_ids[0])
                    decoded_output = self._tokenizer.decode(output)

                    if output[-1] in [self._tokenizer.eos_token_id]:
                        break

                    yield decoded_output
                    # yield prompter.get_response(decoded_output)
            return  # early return for stream_output

        # Without streaming
        with torch.no_grad():
            generation_output = self._model.generate(
                input_ids=input_ids,
                generation_config=generation_config,
                return_dict_in_generate=True,
                output_scores=True,
                max_new_tokens=max_new_tokens,
            )
        s = generation_output.sequences[0]
        output = self._tokenizer.decode(s)

        logger.debug("predict suc, output:" + output)
        yield output

if __name__ == "__main__":
    alpaca_lora = AlpacaLora("/opt/mojing/Models/public/llama/llama-7b-hf", "/home/luguanglong/Codes/github/alpaca-lora/alpaca_lora_2023070702")
    output = alpaca_lora.run("请描述中美关系")
    for item in output:
        logger.debug("ouput item:" + item)
