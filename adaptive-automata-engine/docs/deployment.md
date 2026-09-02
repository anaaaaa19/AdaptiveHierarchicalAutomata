# Deployment & Operations Guide

## Running Offline Replay

Execute reproducible PCAP and trace dataset replays:

```powershell
$env:PYTHONPATH="src;experiments/phase8"; python experiments/phase8/replay_benchmark.py
```

## Running the Real-Time API Server

```powershell
$env:PYTHONPATH="src"; python -m api.app
```

The API server will listen on `http://localhost:8000`.

## Running the React Dashboard

```powershell
cd frontend
npm install
npm run dev
```

The dashboard will open on `http://localhost:3000`.
