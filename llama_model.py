import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from config import GEN_MODEL_NAME

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(
    GEN_MODEL_NAME,
    trust_remote_code=True,
    padding_side="left",
    add_eos_token=True,
    add_bos_token=True,
    use_fast=False
)
tokenizer.pad_token = tokenizer.eos_token

gen_model = AutoModelForCausalLM.from_pretrained(
    GEN_MODEL_NAME, 
    device_map="auto",
    quantization_config=bnb_config,
    trust_remote_code=True
).to('cuda')

def generate_response_with_llama(user_question):
    """
    Генерирует ответ на вопрос пользователя с использованием модели LLaMA.

    Args:
        user_question (str): Вопрос пользователя, на который требуется сгенерировать ответ.

    Returns:
        str: Сгенерированный ответ на вопрос, очищенный от специальных токенов.

    Side Effects:
        - Токенизирует входной вопрос и отправляет его в модель для генерации текста.
        - Использует настройки генерации для контроля длины ответа и вариативности.

    Generation Parameters:
        - `max_length`: Максимальная длина сгенерированного текста (200).
        - `num_return_sequences`: Количество генерируемых последовательностей (1).
        - `no_repeat_ngram_size`: Минимальный размер n-грамм, которые не повторяются (3).
        - `temperature`: Управляет креативностью/разнообразием генерации (0.6).
        - `top_k`: Верхняя граница выбора токенов по частотам (50).
        - `top_p`: Верхняя вероятность для накопительного суммирования частот токенов (0.7).
        - `do_sample`: Включение семплирования для разнообразных результатов (True).
        - `repetition_penalty`: Коэффициент для предотвращения повторений (1.1).

    Example:
        >>> generate_response_with_llama("Какая сегодня погода?")
        "Сегодня ожидается солнечная погода с легким ветром."
    """
    inputs = tokenizer("Write a clear answer for: " + user_question, return_tensors='pt', padding=True)
    input_ids = inputs['input_ids'].to('cuda')
    attention_mask = inputs['attention_mask'].to('cuda')

    outputs = gen_model.generate(
        input_ids,
        attention_mask=attention_mask,
        max_length=200,
        num_return_sequences=1,
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=3,
        temperature=0.6,
        top_k=50,
        top_p=0.7,
        do_sample=True,
        repetition_penalty=1.1
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    return response

