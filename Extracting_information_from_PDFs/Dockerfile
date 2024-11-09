FROM python:3.12
WORKDIR /app

# Install the application dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy in the source code
COPY main.py .
COPY pdf_processing.py .
COPY excel_processing.py .
COPY data/ /app/data

CMD ["python", "main.py"]