import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from config import GEN_MODEL_NAME

# Конфигурация для 4-bit квантования
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

# Загружаем LLaMA с корректной передачей device_map
gen_model = AutoModelForCausalLM.from_pretrained(
    GEN_MODEL_NAME, 
    device_map="cuda",  # Убираем conflict с accelerate
    quantization_config=bnb_config,
    trust_remote_code=True
)




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

# def generate_code_response(user_question):
#     """
#     Генерирует ответ в виде кода на запрос пользователя с помощью LLaMA. Эта функция специально настроена для генерации кода на основе запросов, содержащих указание на создание программного кода.

#     Args:
#         user_question (str): Запрос пользователя, в котором содержится запрос на создание кода.

#     Returns:
#         str: Сгенерированный моделью текст, содержащий код, соответствующий запросу пользователя.

#     Example:
#         >>> generate_code_response("Напиши функцию на C++ для нахождения факториала числа.")
#         "int factorial(int n) { return (n <= 1) ? 1 : n * factorial(n - 1); }"

#     Параметры генерации:
#         - max_length=2000: Максимальная длина сгенерированного ответа, обеспечивающая достаточный объем текста для сложных программ.
#         - temperature=0.1: Низкая температура для повышения последовательности и качества кода.
#         - top_k=40 и top_p=0.6: Контролируют вероятность выбора следующего токена, избегая низкокачественных вариантов.
#         - do_sample=True: Включение сэмплирования для более разнообразных, но контролируемых вариантов.
#         - repetition_penalty=1.1: Снижает вероятность повторений в ответе.

#     Side Effects:
#         - Использует предобученную модель генерации, загруженную на GPU для быстродействия.
#         - Производит токенизацию входного запроса, передает его в генерацию и возвращает декодированный ответ.

#     """
#     inputs = tokenizer("Write a code: " + user_question, return_tensors='pt', padding=True)
#     input_ids = inputs['input_ids'].to('cuda')
#     attention_mask = inputs['attention_mask'].to('cuda')

#     outputs = gen_model.generate(
#         input_ids,
#         attention_mask=attention_mask,
#         max_length=2000,
#         num_return_sequences=1,
#         temperature=0.1,         
#         top_k=40,                
#         top_p=0.6,              
#         do_sample=True,
#         pad_token_id=tokenizer.eos_token_id,
#         repetition_penalty=1.1
#     )
#     response = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
#     return response

