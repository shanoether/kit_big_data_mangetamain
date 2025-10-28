docker build -t mangetamain .
docker run -p 8501:8501 -v ./data:/app/data mangetamain
