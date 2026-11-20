# Gold Pulse AI — Vercel Deployment Guide

Deploy your **Gold Pulse AI Macroeconomic Signal Terminal** to **[Vercel](https://vercel.com)** to get a fast, global, 100% free public web application URL.

---

## Architecture Overview

Your repository is now pre-configured for native Vercel Serverless deployment:

```
xauusd_macro_predictor/
├── vercel.json                 # Vercel serverless routing & clean URLs
├── requirements.txt            # Python serverless dependencies
├── public/
│   └── index.html              # Modern, responsive Tailwind CSS fintech frontend
├── api/
│   ├── calendar.py             # Serverless endpoint: /api/calendar (ForexFactory in WAT)
│   ├── signal.py               # Serverless endpoint: /api/signal (Autonomous AI Signals)
│   └── market.py               # Serverless endpoint: /api/market (Live Gold, DXY, Yields)
├── auto_predictor.py           # Autonomous AI signal generator & reasoning
├── calendar_feed.py            # Live multi-week ForexFactory parser in WAT
└── market_data.py              # Intermarket real-time data manager
```

---

## 2-Minute Deployment Steps

### Method 1: Deploy via GitHub (Recommended)

1. **Create a GitHub Repository**:
   * Go to [github.com/new](https://github.com/new) and create a repository (e.g. `gold-pulse-ai`).

2. **Push Your Code**:
   Open a terminal in `C:\Users\user\Documents\xauusd_macro_predictor` and run:
   ```bash
   git init
   git add .
   git commit -m "Gold Pulse AI Vercel Web App"
   git branch -M main
   git remote add origin https://github.com/<your-username>/gold-pulse-ai.git
   git push -u origin main
   ```

3. **Import into Vercel**:
   * Log in to [vercel.com](https://vercel.com) (free account).
   * Click **"Add New..."** → **"Project"**.
   * Select your `gold-pulse-ai` repository from the list.
   * Leave all build settings at their defaults (Vercel automatically detects `vercel.json` and `requirements.txt`).
   * Click **"Deploy"**.

4. **Your App is Live!**:
   * Vercel will build and deploy your project in under 60 seconds.
   * You will receive a live URL: `https://gold-pulse-ai.vercel.app`.

---

### Method 2: Deploy via Vercel CLI (Direct from Command Line)

If you have Node.js / npm installed:
1. Open PowerShell or Command Prompt.
2. Install the Vercel CLI:
   ```bash
   npm install -g vercel
   ```
3. Navigate to your project folder:
   ```bash
   cd C:\Users\user\Documents\xauusd_macro_predictor
   ```
4. Run:
   ```bash
   vercel
   ```
5. Follow the 3 prompts (hit Enter to accept defaults). To deploy to production:
   ```bash
   vercel --prod
   ```

---

## Connecting a Custom Domain (For Selling Subscriptions)

1. In your Vercel Dashboard, go to your project → **Settings** → **Domains**.
2. Enter your custom domain (e.g., `goldpulse.trade` or `goldpulseai.com`).
3. Add the two DNS records (A record & CNAME) provided by Vercel to your domain registrar (Namecheap, GoDaddy, Cloudflare, etc.).
4. Vercel provides automatic SSL certificates (HTTPS) for free.

---

## Local Testing

You can test the web app right now on your machine:
* **Local Web Address:** [http://localhost:3000](http://localhost:3000)
* Test the API directly in your browser:
  * [http://localhost:3000/api/calendar](http://localhost:3000/api/calendar)
  * [http://localhost:3000/api/signal](http://localhost:3000/api/signal)
  * [http://localhost:3000/api/market](http://localhost:3000/api/market)
