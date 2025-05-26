# Use uma imagem base Python
FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Copia os arquivos para dentro do container
COPY . /app

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta onde o frontend vai rodar
EXPOSE 5000

# Comando para rodar o frontend
CMD ["python", "app.py"]
