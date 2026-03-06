# Intelli-Credit

Intelli-Credit is an AI-powered, end-to-end credit appraisal intelligence engine designed to automate and augment the underwriting process for corporate and MSME lending. By automatically parsing financial PDFs and applying LightGBM scoring matrices against NLP-adjusted heuristics, the system drastically reduces manual analyst workload.

## Tech Stack
-   **Frontend**: React (Vite), Tailwind CSS, Recharts
-   **Backend**: Python, FastAPI, LightGBM, SHAP, Supabase (pgvector), ReportLab, OpenCV/Tesseract, spaCy

## Local Setup

### Backend
Navigate to the root directory and install dependencies:
```bash
pip install -r requirements.txt
```
Start the local FastAPI development server:
```bash
uvicorn main:app --reload
```

### Frontend
Navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (`.env`)
Copy the provided `.env.example` file and fill in your actual keys.
```
SUPABASE_URL=
SUPABASE_KEY=
OPENAI_API_KEY=
```

### Frontend (`frontend/.env.development`)
```
VITE_API_BASE_URL=http://localhost:8000
```
For production (`frontend/.env.production`), ensure `VITE_API_BASE_URL` points to your active server host.

## Deployment
-   **Frontend**: Configured for Vercel auto-deployment (from the `/frontend` sub-directory).
-   **Backend**: Configured for Railway auto-deployment (from the `/` root directory) using the Nixpacks builder.

## Links
-   Live Demo: [link]
-   Demo Video: [link]
