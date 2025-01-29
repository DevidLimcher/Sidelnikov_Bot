import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# Название модели StarCoder
GEN_MODEL_NAME = "bigcode/starcoderbase"

# Конфигурация квантования (4-битное квантование)
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
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

# Очистка VRAM перед загрузкой модели
torch.cuda.empty_cache()

# ✅ Загружаем модель с Offload (CPU/Disk)
gen_model = AutoModelForCausalLM.from_pretrained(
    GEN_MODEL_NAME,
    device_map={"": "cpu"},
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
    prompt = re.sub(r"[^a-zA-Z0-9\s.,?!:]", "", prompt)  # Удаление нестандартных символов
    return prompt


def generate_code_response(user_prompt: str) -> str:
    """
    Генерирует код на основе запроса пользователя, используя StarCoder.

    Args:
        user_prompt (str): Описание кода, который нужно создать.

    Returns:
        str: Сгенерированный код.
    """
    cleaned_prompt = clean_prompt(user_prompt)

    prompt = f"""
    # Python code to solve the following task:
    # {cleaned_prompt}

    def
    """

    inputs = tokenizer(prompt, return_tensors='pt', padding=True).to("cuda")

    with torch.no_grad():
        outputs = gen_model.generate(
            **inputs,
            max_new_tokens=300,  # Ограничиваем количество новых токенов
            temperature=0.2,  # Низкая температура для детерминированности
            top_k=50,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
            repetition_penalty=1.1
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    
    return response


# Тест генерации кода с StarCoder
if __name__ == "__main__":
    test_queries = [
        "Write a function to calculate Fibonacci numbers.",
        "Create a Python script to read a CSV file and process data.",
        "Generate a function that implements quicksort.",
        "Write a script to scrape web data using BeautifulSoup."
    ]

    for query in test_queries:
        print(f"🔹 Запрос: {query}")
        result = generate_code_response(query)
        print(f"📝 Код:\n{result}\n{'-'*50}\n")
