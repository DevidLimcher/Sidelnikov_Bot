import os
import subprocess
import tensorflow as tf

def check_gpu():
    """Проверяет доступность GPU в TensorFlow."""
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        print(f"✅ TensorFlow видит GPU: {gpus}")
    else:
        print("❌ TensorFlow не видит GPU.")

def check_nvidia_smi():
    """Проверяет наличие драйверов NVIDIA."""
    try:
        result = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("✅ NVIDIA драйверы установлены.")
            print(result.stdout.decode())
        else:
            print("❌ NVIDIA драйверы не работают.")
            print(result.stderr.decode())
    except FileNotFoundError:
        print("❌ Команда nvidia-smi не найдена. Убедитесь, что драйверы NVIDIA установлены.")

def check_nvcc():
    """Проверяет наличие компилятора CUDA."""
    try:
        result = subprocess.run(["nvcc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            print("✅ CUDA компилятор установлен.")
            print(result.stdout.decode())
        else:
            print("❌ CUDA компилятор не работает.")
            print(result.stderr.decode())
    except FileNotFoundError:
        print("❌ Команда nvcc не найдена. Убедитесь, что CUDA установлена.")

def check_tensorflow_version():
    """Проверяет версию TensorFlow и её совместимость с GPU."""
    print(f"Версия TensorFlow: {tf.__version__}")
    try:
        from tensorflow.python.compiler.tensorrt import trt_convert
        print("✅ TensorFlow поддерживает TensorRT.")
    except ImportError:
        print("❌ TensorFlow не поддерживает TensorRT.")

def check_cuda_environment():
    """Проверяет переменные окружения для CUDA."""
    ld_library_path = os.environ.get("LD_LIBRARY_PATH", "Не задано")
    print(f"LD_LIBRARY_PATH: {ld_library_path}")
    if "cuda" in ld_library_path.lower():
        print("✅ LD_LIBRARY_PATH настроен корректно.")
    else:
        print("❌ LD_LIBRARY_PATH не настроен для CUDA.")

def main():
    print("🔍 Проверяем окружение...")
    check_gpu()
    check_nvidia_smi()
    check_nvcc()
    check_tensorflow_version()
    check_cuda_environment()
    print("✅ Проверка завершена.")

if __name__ == "__main__":
    main()
