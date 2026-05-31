FROM python:3.14.2

# 1. Create a user with ID 1000 (Strictly required by Hugging Face)
RUN useradd -m -u 1000 user
USER user

# 2. Set environment variables for the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# 3. Copy requirements and install them (setting ownership to User 1000)
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 4. Copy the rest of your application files
COPY --chown=user . .

# 5. Launch the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
