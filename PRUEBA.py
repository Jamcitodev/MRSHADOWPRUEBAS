from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Paso 1: Cargar el modelo pre-entrenado y el tokenizador
modelo = GPT2LMHeadModel.from_pretrained("gpt2")
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

# Paso 2: Preparar los datos de entrenamiento
preguntas = [
    "¿Cuál es tu nombre?",
    "¿Cuál es la capital de Francia?",
    "¿Cuánto es 2 + 2?"
]
respuestas = [
    "Mi nombre es Jarvis",
    "La capital de Francia es París",
    "2 + 2 es igual a 4"
]

datos_entrenamiento = []
for pregunta, respuesta in zip(preguntas, respuestas):
    entrada = pregunta + " " + respuesta
    datos_entrenamiento.append(entrada)

# Paso 3: Tokenizar los datos de entrenamiento
tokens_entrenamiento = tokenizer.batch_encode_plus(
    datos_entrenamiento,
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="pt"
)

# Paso 4: Entrenar el modelo con los datos de entrenamiento
inputs = tokens_entrenamiento["input_ids"]
mascaras_atencion = tokens_entrenamiento["attention_mask"]

modelo.train()
modelo.resize_token_embeddings(len(tokenizer))

optimizador = torch.optim.AdamW(modelo.parameters(), lr=1e-5)

for epoch in range(3):
    optimizador.zero_grad()
    outputs = modelo(inputs, attention_mask=mascaras_atencion, labels=inputs)
    perdida = outputs.loss
    perdida.backward()
    optimizador.step()

# Paso 5: Hacer preguntas y obtener respuestas del modelo entrenado
pregunta = "¿Cuál es la capital de Perú?"
entrada_pregunta = pregunta + " "

tokens_pregunta = tokenizer.encode(entrada_pregunta, return_tensors="pt")

modelo.eval()
respuesta = modelo.generate(
    tokens_pregunta,
    max_length=100,
    num_beams=5,
    no_repeat_ngram_size=2,
    early_stopping=True
)

respuesta_decodificada = tokenizer.decode(respuesta[0], skip_special_tokens=True)

print(respuesta_decodificada)
