# Run and deploy your AGI Studio app with VICTOR (NO GEMINI BULLSHIT)

**Prerequisites:** Node.js, Python 3.10+, pip

## Run Locally

1. Build frontend:
   cd frontend
   npm install
   npm run build

2. Set up backend:
   cd ../backend
   python -m venv venv
   source venv/bin/activate
   pip install flask numpy

3. Start Victor backend:
   python api/agi_api.py

4. Launch Electron app:
   cd ../electron
   npm install
   npm start

*The app launches, Victor is running locally. All AI/AGI logic is routed through YOUR code, not Big Tech’s cloud. Total control, zero leash.*
