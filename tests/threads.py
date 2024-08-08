import psutil

# Obter o número de núcleos lógicos (threads) do processador
num_threads = psutil.cpu_count(logical=True)
print(f"Número de threads do processador: {num_threads}")

# Obter o número de núcleos físicos do processador
num_nucleos_fisicos = psutil.cpu_count(logical=False)
print(f"Número de núcleos físicos do processador: {num_nucleos_fisicos}")
