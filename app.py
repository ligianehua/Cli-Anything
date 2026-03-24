"""
Simple web server for Railway deployment.
Serves a landing page with CLI documentation and API status.
"""

import os
from flask import Flask, jsonify

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VeraPOS CLI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 40px 20px; }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }
        .subtitle { color: #94a3b8; font-size: 1.1rem; margin-bottom: 40px; }
        .status {
            display: inline-flex; align-items: center; gap: 8px;
            background: #1e293b; padding: 8px 16px; border-radius: 20px;
            font-size: 0.9rem; margin-bottom: 32px;
        }
        .dot { width: 8px; height: 8px; background: #4ade80; border-radius: 50%; }
        .section { background: #1e293b; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
        .section h2 { color: #38bdf8; font-size: 1.2rem; margin-bottom: 16px; }
        pre {
            background: #0f172a; padding: 16px; border-radius: 8px;
            overflow-x: auto; font-size: 0.9rem; line-height: 1.6;
        }
        code { color: #a5f3fc; }
        .cmd { color: #4ade80; }
        .comment { color: #64748b; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; }
        .card {
            background: #1e293b; border-radius: 12px; padding: 20px;
            border: 1px solid #334155; transition: border-color 0.2s;
        }
        .card:hover { border-color: #38bdf8; }
        .card h3 { color: #f1f5f9; font-size: 1rem; margin-bottom: 8px; }
        .card p { color: #94a3b8; font-size: 0.85rem; line-height: 1.5; }
        .footer { text-align: center; color: #475569; margin-top: 40px; font-size: 0.85rem; }
        a { color: #38bdf8; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="container">
        <h1>VeraPOS CLI</h1>
        <p class="subtitle">Command-line interface for the VeraPOS Point of Sale system</p>
        <div class="status"><span class="dot"></span> Service Running</div>

        <div class="section">
            <h2>Quick Start</h2>
            <pre><code><span class="comment"># Install</span>
<span class="cmd">pip install -e .</span>

<span class="comment"># Configure server URL</span>
<span class="cmd">pos set-url</span> http://your-server:8000

<span class="comment"># Login</span>
<span class="cmd">pos login</span> -e admin@example.com -p yourpassword

<span class="comment"># Start using</span>
<span class="cmd">pos products list</span>
<span class="cmd">pos sales new</span> -i '[{"product_id":1,"quantity":2}]' -p cash
<span class="cmd">pos reports dashboard</span></code></pre>
        </div>

        <h2 style="color:#f1f5f9; margin-bottom:16px;">Features</h2>
        <div class="grid">
            <div class="card">
                <h3>Products & Categories</h3>
                <p>Create, update, search, import products. Manage categories and organize inventory.</p>
            </div>
            <div class="card">
                <h3>Sales & Transactions</h3>
                <p>Process sales, view receipts, handle returns. Support for cash payments.</p>
            </div>
            <div class="card">
                <h3>Inventory Management</h3>
                <p>Track stock levels, low stock alerts, adjustments, and export reports.</p>
            </div>
            <div class="card">
                <h3>Cash Register</h3>
                <p>Open/close sessions, X and Z readings, cash counting and reconciliation.</p>
            </div>
            <div class="card">
                <h3>Customer & Credits</h3>
                <p>Manage customers, track credits (utang), record payments, view history.</p>
            </div>
            <div class="card">
                <h3>Reports & Analytics</h3>
                <p>Dashboard summaries, sales reports, inventory reports, forecasting.</p>
            </div>
        </div>

        <div class="section" style="margin-top:20px;">
            <h2>API Endpoints</h2>
            <pre><code><span class="cmd">GET</span>  /           — This page
<span class="cmd">GET</span>  /api/health — Service health check</code></pre>
        </div>

        <p class="footer">
            VeraPOS CLI v1.0.0 &mdash;
            <a href="https://github.com/ligianehua/Cli-Anything">GitHub</a>
        </p>
    </div>
</body>
</html>"""


@app.route("/")
def index():
    return HTML_PAGE


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "pos-cli", "version": "1.0.0"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
