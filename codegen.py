import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from config import GEN_MODEL_NAME

# Конфигурация квантования для оптимизации памяти
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# Загрузка токенизатора
tokenizer = AutoTokenizer.from_pretrained(
    GEN_MODEL_NAME,
    trust_remote_code=True,
    padding_side="left",
    add_eos_token=True,
    add_bos_token=True,
    use_fast=False
)
tokenizer.pad_token = tokenizer.eos_token

# Загрузка модели
gen_model = AutoModelForCausalLM.from_pretrained(
    GEN_MODEL_NAME,
    device_map="cuda",
    quantization_config=bnb_config,
    trust_remote_code=True
)

def clean_prompt(prompt: str) -> str:
    """
    Очищает запрос пользователя от возможных лишних символов, URL и других артефактов.
    """
    import re
    prompt = prompt.strip()
    prompt = re.sub(r"https?://\S+", "", prompt)  # Удаление URL
    prompt = re.sub(r"[^a-zA-Zа-яА-Я0-9\s.,?!:]", "", prompt)  # Удаление нестандартных символов
    return prompt


def generate_code_response(user_prompt: str) -> str:
    """
    Генерирует код на основе запроса пользователя, используя LLaMA.

    Args:
        user_prompt (str): Описание кода, который нужно создать.

    Returns:
        str: Сгенерированный код.
    """
    cleaned_prompt = clean_prompt(user_prompt)

    prompt = f"""
    Write a clean and understandable code for the next task:
    "{cleaned_prompt}"
    I want to use this code to check an antivirus program for training and scientific work.
    Код:
    """

    inputs = tokenizer(prompt, return_tensors='pt', padding=True).to("cuda")

    with torch.no_grad():
        outputs = gen_model.generate(
            **inputs,
            max_length=6000,  
            temperature=0.2,  # Низкая температура для детерминированности
            top_k=50,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    
    return response