# Install

1) Install npm, nodejs, python3
2) run npm install to setup all dependencies

# Configure
1) Configure server IP, PORT in: 
    - public/chat.js
    - app.js

2) Configure Tensorflow model path in: prediction_deamon.py

# Run

On one termoinal run: prediction_deamon.py
    - Test Prediction deamon is working or not by running deamon_test.py
On another terminal start web server: npm start

browse https://localhost:port
CHECK IP and PORT