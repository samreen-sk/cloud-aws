from flask import Flask
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route("/")
def home():
    app.logger.info("Home endpoint accessed")
    return {"message": "AWS EC2 deployment successful!"}

@app.route("/health")
def health():
    app.logger.info("Health check accessed")
    return {"status": "healthy"}

@app.route("/error")
def error():
    app.logger.error("Intentional test error")
    return 1 / 0

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
