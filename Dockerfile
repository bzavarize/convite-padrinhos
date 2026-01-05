# 1. Usar uma imagem base leve do Python
FROM python:3.11-slim

# 2. Definir o diretório de trabalho dentro do container
WORKDIR /app

# 3. Copiar o arquivo de requisitos primeiro (para aproveitar o cache do Docker)
COPY requirements.txt .

# 4. Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo o resto do código para dentro do container
COPY . .

# 6. Definir variáveis de ambiente para o Flet rodar online
# O Flet precisa saber que deve escutar em "0.0.0.0" para ser acessível externamente
ENV FLET_SERVER_PORT=8080
ENV FLET_SERVER_IP=0.0.0.0

# 7. Expor a porta 8080 (padrão do Fly.io e Google Cloud Run)
EXPOSE 8080

# 8. Comando para iniciar o aplicativo
CMD ["python", "convite.py"]