base_model_path=$1
data_path=$2
output_dir_path=$3
torchrun --nproc_per_node=2 --master_port=1234 magic_assistant/model/llm/llama_series/finetune.py \
    --base_model meta-llama/Llama-2-13b-hf \
    --data-path $data_path \
    --output_dir $output_dir_path \
    --batch_size 16 \
    --micro_batch_size 1 \
    --num_epochs 1 \
    --learning_rate 0.0004 \
    --cutoff_len 4096 \
    --val_set_size 0 \
    --lora_r 16 \
    --lora_alpha 16 \
    --lora_dropout 0.05 \
    --lora_target_modules '[gate_proj, down_proj, up_proj]' \
    --train_on_inputs False \
    --add_eos_token False \
    --group_by_length False \
    --prompt_template_name alpaca \
    --lr_scheduler 'cosine' \
    --warmup_steps 100
