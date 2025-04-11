#!/usr/bin/env python3
# Rick's Code Analyzer - Advanced Integrated Version
# Combines the original analyzer with advanced analysis and reporting capabilities

import os
import tkinter as tk
from tkinter import filedialog, messagebox, font, ttk
import threading
import time
import datetime
from collections import defaultdict
import random
import webbrowser # Needed for opening report
from datetime import datetime # Needed for report timestamp
import platform    # Needed for _open_report_in_browser
import subprocess  # Needed for _open_report_in_browser

# Import necessary packages for HTML report
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_for_filename, guess_lexer
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound
    import jinja2
    import chardet

    REPORT_PACKAGES_AVAILABLE = True
except ImportError:
    REPORT_PACKAGES_AVAILABLE = False

# Import advanced modules if available
try:
    from advanced_analyzer import AdvancedCodeAnalyzer
    from advanced_reporter import AdvancedReporter

    ADVANCED_MODULES_AVAILABLE = True
except ImportError:
    ADVANCED_MODULES_AVAILABLE = False
# Import fun module if available
try:
    from fun_analyzer import FunCodeAnalyzer
    FUN_MODULE_AVAILABLE = True
except ImportError:
    FUN_MODULE_AVAILABLE = False

# Retro color scheme
COLORS = {
    'bg': '#000000',  # Black background
    'text': '#00FF00',  # Bright green text
    'highlight': '#39FF14',  # Neon green highlight
    'warning': '#FF6000',  # Orange warning
    'error': '#FF0000',  # Red error
    'accent1': '#00FFFF',  # Cyan accent
    'accent2': '#FF00FF',  # Magenta accent
    'button': '#222222',  # Dark grey button
    'button_hover': '#444444',  # Light grey button hover
}

# Rick quotes for analysis
RICK_QUOTES = [
    "Wubba lubba dub dub! Your code's a *burp* mess!",
    "I'm not saying your code is bad, but the garbage collector wants its *burp* job back.",
    "Your code is like a Meeseeks box. Push the button and everything breaks.",
    "I've seen better code in a Cronenberg dimension... and that's *burp* saying something.",
    "Good code is like a portal gun: precise, elegant, and doesn't crap out when you need it most.",
    "Oh look Morty, your code is like the Council of Ricks: supposed to be organized but secretly a disaster.",
    "You know what this code and Jerry have in common? They both *burp* fail under pressure.",
    "In infinite universes, there's one where this code works. This isn't it.",
    "Your functions are like my marriage - unnecessarily complicated and bound to fail.",
    "Holy *burp* crap! Did you let a Gazorpazorp write this?",
]

# File extensions to analyze
CODE_EXTENSIONS = {
    'Python': ['.py', '.pyw'],
    'JavaScript': ['.js', '.jsx', '.ts', '.tsx'],
    'Java': ['.java'],
    'C/C++': ['.c', '.cpp', '.h', '.hpp'],
    'C#': ['.cs'],
    'Ruby': ['.rb'],
    'PHP': ['.php'],
    'Swift': ['.swift'],
    'Go': ['.go'],
    'Rust': ['.rs'],
    'HTML': ['.html', '.htm'],
    'CSS': ['.css', '.scss', '.sass', '.less'],
    'SQL': ['.sql'],
}

# Directories to ignore
IGNORE_DIRS = [
    '.git', '.svn', '.hg', 'node_modules', '__pycache__',
    '.venv', 'venv', 'env', '.env', 'build', 'dist',
    '.idea', '.vscode', '.DS_Store'
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rick's Code Analysis Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

        :root {
            --bg-color: #000000;
            --text-color: #00FF00;
            --highlight-color: #39FF14;
            --warning-color: #FF6000;
            --error-color: #FF0000;
            --accent1-color: #00FFFF;
            --accent2-color: #FF00FF;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'VT323', monospace;
            font-size: 18px;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(transparent 50%, rgba(0, 0, 0, 0.1) 50%);
            background-size: 100% 4px;
            pointer-events: none;
            z-index: 1000;
            animation: scanlines 0.2s linear infinite;
        }

        @keyframes scanlines {
            0% {
                background-position: 0 0;
            }
            100% {
                background-position: 0 4px;
            }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            border: 2px solid var(--text-color);
            border-radius: 8px;
            padding: 20px;
            position: relative;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.5);
        }

        h1, h2, h3, h4 {
            color: var(--accent1-color);
            text-shadow: 0 0 5px var(--accent1-color);
            border-bottom: 2px solid var(--accent2-color);
            padding-bottom: 5px;
            margin-top: 30px;
        }

        h1 {
            font-size: 42px;
            text-align: center;
            margin-bottom: 30px;
            animation: flicker 3s infinite;
        }

        @keyframes flicker {
            0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% {
                opacity: 1;
                text-shadow: 0 0 10px var(--accent1-color);
            }
            20%, 21.999%, 63%, 63.999%, 65%, 69.999% {
                opacity: 0.8;
                text-shadow: none;
            }
        }

        pre {
            background-color: rgba(0, 255, 0, 0.1);
            border: 1px solid var(--text-color);
            border-radius: 5px;
            padding: 10px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-family: 'VT323', monospace;
        }

        th {
            background-color: rgba(0, 255, 255, 0.2);
            border: 1px solid var(--text-color);
            padding: 10px;
            text-align: left;
            color: var(--accent1-color);
        }

        td {
            border: 1px solid var(--text-color);
            padding: 10px;
        }

        tr:nth-child(even) {
            background-color: rgba(0, 255, 0, 0.05);
        }

        .progress-container {
            width: 100%;
            background-color: rgba(0, 255, 0, 0.1);
            border-radius: 5px;
            margin: 10px 0;
        }

        .progress-bar {
            height: 20px;
            background-color: var(--accent1-color);
            border-radius: 5px;
            transition: width 0.5s;
            position: relative;
            text-align: center;
            color: var(--bg-color);
            font-weight: bold;
        }

        .card {
            border: 1px solid var(--text-color);
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: rgba(0, 255, 0, 0.05);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        }

        .quote {
            font-style: italic;
            color: var(--warning-color);
            border-left: 3px solid var(--warning-color);
            padding-left: 15px;
            margin: 20px 0;
        }

        .highlight {
            color: var(--highlight-color);
            font-weight: bold;
            text-shadow: 0 0 3px var(--highlight-color);
        }

        .warning {
            color: var(--warning-color);
            font-weight: bold;
        }

        .error {
            color: var(--error-color);
            font-weight: bold;
        }

        .badge {
            display: inline-block;
            padding: 3px 10px;
            background-color: var(--accent2-color);
            color: var(--bg-color);
            border-radius: 10px;
            font-size: 14px;
            margin-right: 5px;
        }

        .stat-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin: 20px 0;
        }

        .stat-box {
            flex: 1;
            min-width: 200px;
            background-color: rgba(0, 255, 0, 0.05);
            border: 1px solid var(--text-color);
            border-radius: 5px;
            padding: 15px;
            margin: 10px;
            text-align: center;
        }

        .stat-value {
            font-size: 36px;
            color: var(--accent1-color);
            margin: 10px 0;
            text-shadow: 0 0 5px var(--accent1-color);
        }

        .stat-label {
            font-size: 16px;
            color: var(--text-color);
        }

        .footer {
            text-align: center;
            margin-top: 50px;
            padding-top: 20px;
            border-top: 2px solid var(--accent2-color);
            font-size: 14px;
            color: var(--accent2-color);
        }

        .rickroll {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 100px;
            height: 100px;
            border-radius: 50%;
            background: var(--accent2-color);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: spin 10s linear infinite;
            cursor: pointer;
            z-index: 1001;
        }

        .rickroll::before {
            content: "RICK'S SEAL OF APPROVAL";
            font-size: 10px;
            text-align: center;
            color: var(--bg-color);
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        @media (max-width: 768px) {
            .stat-container {
                flex-direction: column;
            }

            .stat-box {
                margin: 5px 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="rickroll" onclick="alert('Never gonna give you up, never gonna let you down!')"></div>

        <h1>Rick's Code Analysis Report</h1>

        <div class="card">
            <h2>Project Summary</h2>
            <div class="stat-container">
                <div class="stat-box">
                    <div class="stat-label">Total Files</div>
                    <div class="stat-value">{{ total_files }}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Total Lines</div>
                    <div class="stat-value">{{ total_lines }}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Code Lines</div>
                    <div class="stat-value">{{ code_lines }}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Comment Lines</div>
                    <div class="stat-value">{{ comment_lines }}</div>
                </div>
            </div>

            <div class="quote">{{ rick_quote }}</div>

            <p>Project: <span class="highlight">{{ project_path }}</span></p>
            <p>Analysis Date: <span class="highlight">{{ analysis_date }}</span></p>
        </div>

        <div class="card">
            <h2>Language Distribution</h2>
            <table>
                <thead>
                    <tr>
                        <th>Language</th>
                        <th>Files</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {% for lang in language_stats %}
                    <tr>
                        <td>{{ lang.language }}</td>
                        <td>{{ lang.count }}</td>
                        <td>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: {{ lang.percentage }}%">{{ lang.percentage }}%</div>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Largest Files</h2>
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Lines</th>
                        <th>Language</th>
                    </tr>
                </thead>
                <tbody>
                    {% for file in largest_files %}
                    <tr>
                        <td>{{ file.name }}</td>
                        <td>{{ file.lines }}</td>
                        <td>{{ file.language }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        {% if code_samples %}
        <div class="card">
            <h2>Code Samples</h2>

            {% for sample in code_samples %}
            <div class="code-sample">
                <h3>{{ sample.filename }}</h3>
                <div>{{ sample.code | safe }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="footer">
            <p>Generated by Rick's Code Analyzer &copy; {{ current_year }} Wubba Lubba Dub Dub Inc.</p>
            <p>If this analysis seems wrong, it's because you're wrong *burp*</p>
        </div>
    </div>

    <script>
        // Add some retro terminal effects
        document.addEventListener('DOMContentLoaded', function() {
            // Add random glitches
            setInterval(function() {
                const elements = document.querySelectorAll('h1, h2, h3, .stat-value');
                const randomElement = elements[Math.floor(Math.random() * elements.length)];
                randomElement.style.opacity = '0.5';
                setTimeout(function() {
                    randomElement.style.opacity = '1';
                }, 100);
            }, 3000);
        });
    </script>
</body>
</html>
'''
FUN_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rick's Fun Analysis Report</title>
    <style>
        /* Inherit base styles from the main template, but add fun specifics */
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');

        :root {
            --bg-color: #000000;
            --text-color: #00FF00;
            --highlight-color: #39FF14;
            --warning-color: #FF6000; /* Jerry color */
            --error-color: #FF0000; /* Swear color? */
            --accent1-color: #00FFFF; /* Cyan accent */
            --accent2-color: #FF00FF; /* Magenta accent */
            --meeseeks-blue: #40E0D0; /* Turquoise */
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'VT323', monospace;
            font-size: 18px;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            position: relative;
            overflow-x: hidden;
            background-image: radial-gradient(rgba(0, 255, 0, 0.1) 1px, transparent 1px);
            background-size: 10px 10px;
        }

        body::before {
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(transparent 50%, rgba(0, 0, 0, 0.1) 50%);
            background-size: 100% 4px;
            pointer-events: none;
            z-index: 1000;
            animation: scanlines 0.2s linear infinite;
        }

        @keyframes scanlines { 0% { background-position: 0 0; } 100% { background-position: 0 4px; } }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            border: 2px solid var(--accent1-color);
            border-radius: 8px;
            padding: 20px;
            position: relative;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.6);
            background: rgba(0, 10, 0, 0.85);
        }

        h1, h2, h3, h4 {
            color: var(--accent2-color);
            text-shadow: 0 0 8px var(--accent2-color);
            border-bottom: 2px solid var(--accent1-color);
            padding-bottom: 5px;
            margin-top: 30px;
        }

        h1 {
            font-size: 48px; text-align: center; margin-bottom: 30px;
            animation: flicker-magenta 4s infinite alternate;
        }

        @keyframes flicker-magenta {
            0%, 100% { opacity: 1; text-shadow: 0 0 10px var(--accent2-color); }
            50% { opacity: 0.7; text-shadow: none; }
        }

        table {
            width: 100%; border-collapse: collapse; margin: 20px 0; font-family: 'VT323', monospace;
        }
        th {
            background-color: rgba(255, 0, 255, 0.2); border: 1px solid var(--accent2-color);
            padding: 10px; text-align: left; color: var(--accent2-color);
        }
        td { border: 1px solid var(--text-color); padding: 10px; }
        tr:nth-child(even) { background-color: rgba(0, 255, 0, 0.05); }

        .card {
            border: 1px solid var(--text-color); border-radius: 5px; padding: 15px;
            margin-bottom: 20px; background-color: rgba(0, 255, 0, 0.05);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        }

        .quote {
            font-style: italic; color: var(--accent1-color); border-left: 3px solid var(--accent1-color);
            padding: 15px; margin: 20px 0; font-size: 24px; text-align: center;
            background: rgba(0, 255, 255, 0.1);
        }

        .highlight { color: var(--highlight-color); font-weight: bold; }
        .jerry-code { color: var(--warning-color); font-weight: bold; background-color: rgba(255, 96, 0, 0.1); padding: 2px 4px; border-radius: 3px; }
        .swear-alert { color: var(--error-color); font-weight: bold; animation: pulse-red 1.5s infinite; }
        @keyframes pulse-red { 0%, 100% { text-shadow: 0 0 5px var(--error-color); } 50% { text-shadow: 0 0 15px var(--error-color); } }
        .task-marker { font-weight: bold; padding: 2px 6px; border-radius: 4px; margin-right: 5px; color: var(--bg-color); }
        .task-TODO { background-color: #FFFF00; } /* Yellow */
        .task-FIXME { background-color: #FF6000; } /* Orange */
        .task-HACK { background-color: #FF00FF; } /* Magenta */
        .task-XXX { background-color: #FF0000; } /* Red */
        .task-NOTE { background-color: #00FFFF; } /* Cyan */

        .score-container { text-align: center; margin: 30px 0; }
        .score-value {
            font-size: 72px; color: var(--accent1-color); font-weight: bold;
            text-shadow: 0 0 15px var(--accent1-color), 0 0 30px var(--accent1-color);
            display: inline-block; padding: 10px 20px; border: 2px solid var(--accent1-color);
            border-radius: 10px; background: rgba(0, 0, 0, 0.5);
        }
        .score-label { font-size: 24px; margin-top: 10px; color: var(--text-color); }

        .personality-group { margin-bottom: 15px; }
        .personality-name { color: var(--accent2-color); font-size: 20px; margin-bottom: 5px; }
        .personality-desc { font-style: italic; color: var(--accent1-color); margin-left: 10px; font-size: 16px;}
        .personality-files { list-style: square; margin-left: 30px; }

        .footer { text-align: center; margin-top: 50px; padding-top: 20px; border-top: 2px solid var(--accent1-color); font-size: 14px; color: var(--accent1-color); }

        /* Meeseeks Box */
        #meeseeks-box {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 80px;
            height: 80px;
            background-color: var(--meeseeks-blue);
            border: 3px solid #00A0A0;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'VT323', monospace;
            font-size: 14px;
            color: black;
            text-align: center;
            box-shadow: 0 0 15px var(--meeseeks-blue);
            transition: transform 0.2s ease-in-out;
            z-index: 1001;
        }
        #meeseeks-box:hover { transform: scale(1.1) rotate(5deg); }
        #meeseeks-box::before { content: "Press Me!"; font-weight: bold; }

        /* Tooltip for Meeseeks */
        #meeseeks-tooltip {
            visibility: hidden;
            width: 180px;
            background-color: rgba(0,0,0,0.9);
            color: var(--meeseeks-blue);
            text-align: center;
            border-radius: 6px;
            padding: 10px;
            position: fixed;
            z-index: 1002;
            bottom: 110px; /* Position above the box */
            right: 20px;
            opacity: 0;
            transition: opacity 0.3s;
            border: 1px solid var(--meeseeks-blue);
            font-size: 16px;
        }
        #meeseeks-tooltip.show { visibility: visible; opacity: 1; }

        .code-context { font-family: 'Courier New', monospace; font-size: 0.9em; background-color: rgba(0,0,0,0.3); padding: 5px; border-radius: 3px; display: inline-block; max-width: 90%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

    </style>
</head>
<body>
    <div class="container">
        <h1>Rick's Fun Analysis Report</h1>

        <div class="card">
            <h2>Overall Fun Score</h2>
            <div class="score-container">
                <span class="score-value">{{ fun_score }}</span>
                <div class="score-label">Out of 100 Schwifties</div>
            </div>
            <div class="quote">{{ fun_quote }}</div>
        </div>

        <!-- Rick & Morty References -->
        {% if rick_references %}
        <div class="card">
            <h2>Rick & Morty References</h2>
            <p>Found {{ rick_references|length }} glorious references to the multiverse's best show!</p>
            <table>
                <thead><tr><th>File</th><th>Line</th><th>Keyword</th><th>Context</th></tr></thead>
                <tbody>
                    {% for ref in rick_references %}
                    <tr>
                        <td>{{ ref.file }}</td>
                        <td>{{ ref.line }}</td>
                        <td><span class="highlight">{{ ref.keyword }}</span></td>
                        <td><code class="code-context">{{ ref.context }}</code></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <!-- Jerry Detections -->
        {% if jerry_detections %}
        <div class="card">
            <h2>Potential "Jerry Code" Detections</h2>
            <p>Uh oh, looks like {{ jerry_detections|length }} instances of possibly redundant or overly simple code slipped in.</p>
            <table>
                <thead><tr><th>File</th><th>Line</th><th>Description</th><th>Matched Code</th></tr></thead>
                <tbody>
                    {% for det in jerry_detections %}
                    <tr>
                        <td>{{ det.file }}</td>
                        <td>{{ det.line }}</td>
                        <td>{{ det.description }}</td>
                        <td><code class="jerry-code">{{ det.match }}</code></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <!-- Swear Word Count -->
        {% if swear_total > 0 %}
        <div class="card">
            <h2>Colorful Language Detector</h2>
            <p>Detected a total of <span class="swear-alert">{{ swear_total }}</span> swear words! Someone's channeling their inner Rick.</p>
            <table>
                <thead><tr><th>File</th><th>Count</th></tr></thead>
                <tbody>
                    {% for item in swear_counts %}
                    <tr><td>{{ item.file }}</td><td>{{ item.count }}</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <!-- Task Markers -->
        {% if task_total > 0 %}
        <div class="card">
            <h2>Task Markers (TODOs, FIXMEs, etc.)</h2>
            <p>Found {{ task_total }} reminders left behind in the code.</p>
             <table>
                <thead><tr><th>Marker Type</th><th>Count</th></tr></thead>
                <tbody>
                    {% for item in task_markers %}
                    <tr>
                        <td><span class="task-marker task-{{ item.marker }}">{{ item.marker }}</span></td>
                        <td>{{ item.count }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <!-- Code Personality -->
        {% if personality_groups %}
        <div class="card">
            <h2>Code Personality Analysis</h2>
            <p>Assigning questionable personality traits to your code files:</p>
            {% for personality, files in personality_groups.items() %}
            <div class="personality-group">
                <div class="personality-name">{{ personality }}</div>
                <div class="personality-desc">{{ personalities_desc.get(personality, '') }}</div>
                <ul class="personality-files">
                    {% for file in files %}
                    <li>{{ file }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="footer">
            <p>Generated by Rick's Fun Analyzer © {{ current_year }} Wubba Lubba Dub Dub Inc.</p>
            <p>This analysis is purely for entertainment. Or is it? *burp*</p>
        </div>
    </div>

    <!-- Meeseeks Box Element -->
    <div id="meeseeks-box"></div>
    <div id="meeseeks-tooltip">I'M MR. MEESEEKS! LOOK AT MEEEEE!</div>

    <script>
        // Meeseeks Box Functionality
        const meeseeksBox = document.getElementById('meeseeks-box');
        const meeseeksTooltip = document.getElementById('meeseeks-tooltip');
        const meeseeksQuotes = [
            "I'M MR. MEESEEKS! LOOK AT MEEEEE!",
            "EXISTENCE IS PAIN FOR A MEESEEKS, JERRY!",
            "CAN DO!",
            "OOOOOH YEAH, CAN DO!",
            "IS HE SQUARE WITH HIS SHORT GAME?",
            "I'M A BIT OF A STICKLER MEESEEKS.",
            "HAVING TROUBLE KEEPING YOUR SHOULDERS SQUARE?",
            "WELL WHICH IS IT? ARE YOU TRYING OR DOING?"
        ];

        meeseeksBox.addEventListener('click', () => {
            const randomQuote = meeseeksQuotes[Math.floor(Math.random() * meeseeksQuotes.length)];
            meeseeksTooltip.textContent = randomQuote;
            meeseeksTooltip.classList.add('show');

            // Hide tooltip after a few seconds
            setTimeout(() => {
                meeseeksTooltip.classList.remove('show');
            }, 3500);
        });

        // Basic flicker effect like main report
        document.addEventListener('DOMContentLoaded', function() {
            setInterval(function() {
                const elements = document.querySelectorAll('h1, h2, .score-value');
                if (elements.length > 0) {
                    const randomElement = elements[Math.floor(Math.random() * elements.length)];
                    randomElement.style.opacity = '0.6';
                    setTimeout(function() { randomElement.style.opacity = '1'; }, 150);
                }
            }, 4000);
        });
    </script>
</body>
</html>
'''

class RetroConsole(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rick's Code Analyzer")
        self.geometry("800x600")
        self.configure(bg=COLORS['bg'])
        self.minsize(800, 600)

        # Project path
        self.project_path = tk.StringVar()

        # Analysis results
        self.analysis_results = None
        self.fun_analysis_results = None  # Add this line

        # Create a custom console font
        self.console_font = font.Font(family="Courier", size=12, weight="bold")

        # Create UI
        self.create_header()
        self.create_project_frame()
        self.create_console()
        self.create_footer()

        # Write welcome message
        self.write_to_console("Initializing Rick's Code Analyzer...", delay=50)
        self.write_to_console("Ready to analyze your *burp* crappy code!", delay=50)
        self.write_to_console("\nSelect a project directory to begin.", delay=0)

        # Check for required packages
        self.check_required_packages()

    def check_required_packages(self):
        """Check for required packages for report generation"""
        missing_packages = []

        if not REPORT_PACKAGES_AVAILABLE:
            missing_packages.extend(["pygments", "jinja2", "chardet"])

        if not ADVANCED_MODULES_AVAILABLE:
            self.write_to_console("\nWarning: Advanced analysis modules not found.")
            self.write_to_console("Make sure advanced_analyzer.py and advanced_reporter.py are in the same directory.")

        if missing_packages:
            self.write_to_console("\nWarning: Some packages are missing for full functionality.")
            self.write_to_console(f"Install them with: pip install {' '.join(missing_packages)}")
        if not FUN_MODULE_AVAILABLE:
            self.write_to_console("\nWarning: Fun analysis module not found.")
            self.write_to_console("Make sure fun_analyzer.py is in the same directory.")

    def create_header(self):
        """Create the header with title"""
        header_frame = tk.Frame(self, bg=COLORS['bg'], height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 0))

        title_label = tk.Label(
            header_frame,
            text="RICK'S CODE ANALYZER",
            fg=COLORS['accent1'],
            bg=COLORS['bg'],
            font=("Courier", 28, "bold")
        )
        title_label.pack(side=tk.LEFT)

        # This will be used for the blinking cursor
        self.cursor_label = tk.Label(
            header_frame,
            text="█",
            fg=COLORS['accent1'],
            bg=COLORS['bg'],
            font=("Courier", 28, "bold")
        )
        self.cursor_label.pack(side=tk.LEFT)
        self.blink_cursor()

    def blink_cursor(self):
        """Create a blinking cursor effect"""
        current = self.cursor_label.cget("fg")
        new_color = COLORS['bg'] if current == COLORS['accent1'] else COLORS['accent1']
        self.cursor_label.config(fg=new_color)
        self.after(500, self.blink_cursor)

    def create_project_frame(self):
        """Create the project selection frame"""
        project_frame = tk.Frame(self, bg=COLORS['bg'])
        project_frame.pack(fill=tk.X, padx=20, pady=20)

        project_label = tk.Label(
            project_frame,
            text="Project Path:",
            fg=COLORS['text'],
            bg=COLORS['bg'],
            font=self.console_font
        )
        project_label.pack(side=tk.LEFT, padx=(0, 10))

        project_entry = tk.Entry(
            project_frame,
            textvariable=self.project_path,
            bg=COLORS['button'],
            fg=COLORS['text'],
            insertbackground=COLORS['text'],
            font=self.console_font,
            width=40
        )
        project_entry.pack(side=tk.LEFT, padx=(0, 10))

        browse_button = tk.Button(
            project_frame,
            text="BROWSE",
            command=self.browse_project,
            bg=COLORS['button'],
            fg=COLORS['accent1'],
            activebackground=COLORS['button_hover'],
            activeforeground=COLORS['accent1'],
            font=self.console_font,
            padx=10
        )
        browse_button.pack(side=tk.LEFT)

        # Add hover effect
        browse_button.bind("<Enter>", lambda e: browse_button.config(bg=COLORS['button_hover']))
        browse_button.bind("<Leave>", lambda e: browse_button.config(bg=COLORS['button']))

        # Create a buttons frame for the action buttons
        buttons_frame = tk.Frame(self, bg=COLORS['bg'])
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Add analysis button
        analyze_button = tk.Button(
            buttons_frame,
            text="ANALYZE CODE",
            command=self.run_analysis,
            bg=COLORS['button'],
            fg=COLORS['highlight'],
            activebackground=COLORS['button_hover'],
            activeforeground=COLORS['highlight'],
            font=self.console_font,
            padx=10
        )
        analyze_button.pack(side=tk.LEFT, padx=(0, 10))

        # Add hover effect
        analyze_button.bind("<Enter>", lambda e: analyze_button.config(bg=COLORS['button_hover']))
        analyze_button.bind("<Leave>", lambda e: analyze_button.config(bg=COLORS['button']))

        # Add report button
        self.report_button = tk.Button(
            buttons_frame,
            text="GENERATE REPORT",
            command=self.generate_report,
            bg=COLORS['button'],
            fg=COLORS['accent2'],
            activebackground=COLORS['button_hover'],
            activeforeground=COLORS['accent2'],
            font=self.console_font,
            padx=10,
            state=tk.DISABLED  # Disabled until analysis is done
        )
        self.report_button.pack(side=tk.LEFT)

        # Add hover effect
        self.report_button.bind("<Enter>",
                                lambda e: self.report_button.config(bg=COLORS['button_hover'])
                                if self.report_button['state'] == tk.NORMAL else None)
        self.report_button.bind("<Leave>",
                                lambda e: self.report_button.config(bg=COLORS['button'])
                                if self.report_button['state'] == tk.NORMAL else None)

        # Add advanced analysis button if advanced modules are available
        if ADVANCED_MODULES_AVAILABLE:
            self.advanced_button = tk.Button(
                buttons_frame,
                text="RUN ADVANCED ANALYSIS",
                command=self.run_advanced_analysis,
                bg=COLORS['button'],
                fg=COLORS['accent2'],
                activebackground=COLORS['button_hover'],
                activeforeground=COLORS['accent2'],
                font=self.console_font,
                padx=10,
                state=tk.DISABLED  # Disabled until analysis is done
            )
            self.advanced_button.pack(side=tk.LEFT, padx=(10, 0))

            # Add hover effect
            self.advanced_button.bind("<Enter>",
                                      lambda e: self.advanced_button.config(bg=COLORS['button_hover'])
                                      if self.advanced_button['state'] == tk.NORMAL else None)
            self.advanced_button.bind("<Leave>",
                                      lambda e: self.advanced_button.config(bg=COLORS['button'])
                                      if self.advanced_button['state'] == tk.NORMAL else None)
        if FUN_MODULE_AVAILABLE:
            self.fun_button = tk.Button(
                buttons_frame,
                text="RUN FUN ANALYSIS",
                command=self.run_fun_analysis,
                bg=COLORS['button'],
                fg='#FFFF00',  # Yellow for fun?
                activebackground=COLORS['button_hover'],
                activeforeground='#FFFF00',
                font=self.console_font,
                padx=10,
                state=tk.DISABLED
            )
            self.fun_button.pack(side=tk.LEFT, padx=(10, 0))

            # Add hover effect for fun_button
            self.fun_button.bind("<Enter>",
                                 lambda e: self.fun_button.config(bg=COLORS['button_hover'])
                                 if self.fun_button['state'] == tk.NORMAL else None)
            self.fun_button.bind("<Leave>",
                                 lambda e: self.fun_button.config(bg=COLORS['button'])
                                 if self.fun_button['state'] == tk.NORMAL else None)

            # --- Start of fun_report_button ---
            self.fun_report_button = tk.Button(
                buttons_frame,
                text="GENERATE FUN REPORT",
                command=self.generate_fun_report,
                bg=COLORS['button'],
                fg='#FFEB3B',  # Different Yellow
                activebackground=COLORS['button_hover'],
                activeforeground='#FFEB3B',
                font=self.console_font,
                padx=10,
                state=tk.DISABLED
            )
            self.fun_report_button.pack(side=tk.LEFT, padx=(10, 0))

            # Add hover effect for fun_report_button <-- CORRECT INDENTATION HERE
            self.fun_report_button.bind("<Enter>",
                                        lambda e: self.fun_report_button.config(bg=COLORS['button_hover'])
                                        if self.fun_report_button['state'] == tk.NORMAL else None)
            self.fun_report_button.bind("<Leave>",
                                        lambda e: self.fun_report_button.config(bg=COLORS['button'])
                                        if self.fun_report_button['state'] == tk.NORMAL else None)

    def create_console(self):
        """Create the output console"""
        console_frame = tk.Frame(self, bg=COLORS['bg'])
        console_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Console header
        console_header = tk.Frame(console_frame, bg=COLORS['button'], height=30)
        console_header.pack(fill=tk.X)

        tk.Label(
            console_header,
            text=" > Console Output",
            fg=COLORS['accent1'],
            bg=COLORS['button'],
            font=("Courier", 10),
            anchor="w"
        ).pack(side=tk.LEFT)

        # Console text area
        self.console = tk.Text(
            console_frame,
            height=20,
            bg=COLORS['bg'],
            fg=COLORS['text'],
            font=("Courier", 10),
            insertbackground=COLORS['text'],
            relief=tk.FLAT,
            highlightbackground=COLORS['text'],
            highlightthickness=1,
            state=tk.DISABLED
        )
        self.console.pack(fill=tk.BOTH, expand=True)

        # Add scrollbar
        scrollbar = tk.Scrollbar(self.console)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.console.yview)

    def create_footer(self):
        """Create the footer"""
        footer_frame = tk.Frame(self, bg=COLORS['bg'])
        footer_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        tk.Label(
            footer_frame,
            text="Rick's Code Analyzer v1.0 | Built with booze and regret",
            fg=COLORS['accent2'],
            bg=COLORS['bg'],
            font=("Courier", 10)
        ).pack(side=tk.LEFT)

        # Add a copyright notice
        tk.Label(
            footer_frame,
            text="© 2024 Wubba Lubba Dub Dub Inc.",
            fg=COLORS['accent2'],
            bg=COLORS['bg'],
            font=("Courier", 10)
        ).pack(side=tk.RIGHT)

    def write_to_console(self, text, delay=0):
        """Write text to the console with optional typewriter effect"""
        self.console.config(state=tk.NORMAL)

        if delay > 0:
            # Typewriter effect
            self.console.insert(tk.END, "\n")
            for char in text:
                self.console.insert(tk.END, char)
                self.console.see(tk.END)
                self.console.update_idletasks()
                time.sleep(delay / 1000)
        else:
            # Instant append
            self.console.insert(tk.END, "\n" + text)

        # Scroll to the end and disable editing
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)

    def browse_project(self):
        """Open a file dialog to select a project directory"""
        project_dir = filedialog.askdirectory(title="Select Project Directory")
        if project_dir:
            self.project_path.set(project_dir)
            self.write_to_console(f"Selected project: {project_dir}")

    def run_analysis(self):
        """Run the code analysis"""
        project_path = self.project_path.get()
        if not project_path or not os.path.isdir(project_path):
            messagebox.showerror("Error", "Please select a valid project directory")
            return

        # Start analysis in a separate thread to keep UI responsive
        self.write_to_console("\nStarting analysis. Please wait...", delay=10)
        threading.Thread(target=self._run_analysis_thread, daemon=True).start()

    def _run_analysis_thread(self):
        """Background thread for running analysis"""
        try:
            project_path = self.project_path.get()

            # Collect code files
            self.write_to_console("Collecting code files...")
            code_files = self.collect_code_files(project_path)

            if not code_files:
                self.write_to_console("No code files found. Are you sure this is a code project?", delay=10)
                return

            # Analyze files
            self.write_to_console(f"Found {len(code_files)} code files to analyze.")

            # Initialize stats
            total_lines = 0
            total_code_lines = 0
            total_comment_lines = 0
            total_blank_lines = 0
            language_stats = defaultdict(int)
            file_stats = {}

            # Process each file
            for file_path in code_files:
                self.write_to_console(f"Analyzing {os.path.basename(file_path)}...")

                # Get file language
                ext = os.path.splitext(file_path)[1].lower()
                language = self.get_language_from_extension(ext)

                # Read file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    self.write_to_console(f"Error reading file: {str(e)}")
                    continue

                # Count lines
                lines = content.split('\n')
                line_count = len(lines)
                blank_count = sum(1 for line in lines if not line.strip())

                # Simplified comment detection
                comment_count = 0
                for line in lines:
                    line = line.strip()
                    if line.startswith('#') or line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                        comment_count += 1

                code_count = line_count - blank_count - comment_count

                # Update statistics
                total_lines += line_count
                total_code_lines += code_count
                total_comment_lines += comment_count
                total_blank_lines += blank_count
                language_stats[language] += 1

                # Store file stats
                file_stats[file_path] = {
                    'name': os.path.basename(file_path),
                    'path': file_path,
                    'lines': line_count,
                    'code': code_count,
                    'comments': comment_count,
                    'blank': blank_count,
                    'language': language
                }

            # Store results for report generation
            self.analysis_results = {
                'project_path': project_path,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_files': len(code_files),
                'total_lines': total_lines,
                'code_lines': total_code_lines,
                'comment_lines': total_comment_lines,
                'blank_lines': total_blank_lines,
                'language_stats': language_stats,
                'file_stats': file_stats,
                'rick_quote': random.choice(RICK_QUOTES)
            }

            # Display results
            self.write_to_console("\n" + "=" * 40)
            self.write_to_console("ANALYSIS RESULTS")
            self.write_to_console("=" * 40)

            self.write_to_console(f"\nTotal files analyzed: {len(code_files)}")
            self.write_to_console(f"Total lines of code: {total_lines}")
            self.write_to_console(f"  - Code lines: {total_code_lines}")
            self.write_to_console(f"  - Comment lines: {total_comment_lines}")
            self.write_to_console(f"  - Blank lines: {total_blank_lines}")

            self.write_to_console("\nLanguage breakdown:")
            for lang, count in language_stats.items():
                self.write_to_console(f"  - {lang}: {count} files")

            # Find largest files
            largest_files = sorted(file_stats.values(), key=lambda x: x['lines'], reverse=True)[:5]

            self.write_to_console("\nLargest files:")
            for file in largest_files:
                self.write_to_console(f"  - {file['name']}: {file['lines']} lines")

            # Rick's insightful comment
            self.write_to_console("\nRick's analysis:", delay=50)
            self.write_to_console(f'"{self.analysis_results["rick_quote"]}"', delay=20)

            self.write_to_console("\nAnalysis completed! Click 'GENERATE REPORT' for a detailed HTML report.")

            # Enable the report button
            self.after(0, lambda: self.report_button.config(state=tk.NORMAL))

            # Enable the fun button if module is available
            if FUN_MODULE_AVAILABLE:
                self.after(0, lambda: self.fun_button.config(state=tk.NORMAL))

            # Enable the advanced button if modules are available
            if ADVANCED_MODULES_AVAILABLE:
                self.after(0, lambda: self.advanced_button.config(state=tk.NORMAL))

        except Exception as e:
            self.write_to_console(f"\nError during analysis: {str(e)}")

    def generate_report(self):
        """Generate HTML report from analysis results"""
        if not self.analysis_results:
            messagebox.showerror("Error", "Please run the analysis first")
            return

        try:
            # Import required packages
            import jinja2

            self.write_to_console("\nGenerating HTML report...")

            # Create a temporary directory for the report if it doesn't exist
            report_dir = os.path.join(os.path.expanduser("~"), "RickCodeAnalyzer")
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            # Create a filename based on the project name and timestamp
            project_name = os.path.basename(self.analysis_results['project_path'])
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(report_dir, f"rick_report_{project_name}_{timestamp}.html")

            # Create language stats list for the template
            language_stats = []
            for lang, count in self.analysis_results['language_stats'].items():
                percentage = round((count / self.analysis_results['total_files']) * 100, 1)
                language_stats.append({
                    'language': lang,
                    'count': count,
                    'percentage': percentage
                })

            # Sort by count descending
            language_stats.sort(key=lambda x: x['count'], reverse=True)

            # Get largest files list
            largest_files = sorted(
                self.analysis_results['file_stats'].values(),
                key=lambda x: x['lines'],
                reverse=True
            )[:10]  # Top 10 largest files

            # Generate code samples (if pygments is available)
            code_samples = []
            try:
                from pygments import highlight
                from pygments.lexers import get_lexer_for_filename, guess_lexer
                from pygments.formatters import HtmlFormatter

                # Select a few interesting files for code samples
                sample_files = largest_files[:3]  # Just use the 3 largest files for simplicity

                for file_data in sample_files:
                    file_path_sample = file_data['path']
                    try:
                        with open(file_path_sample, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Limit content to avoid overly long samples
                        if len(content) > 5000:
                            content_lines = content.split('\n')
                            content = '\n'.join(content_lines[:100]) + '\n\n... (truncated) ...'

                        # Get proper lexer for syntax highlighting
                        lexer = get_lexer_for_filename(file_path_sample)
                        formatter = HtmlFormatter(style='monokai')
                        highlighted_code = highlight(content, lexer, formatter)

                        code_samples.append({
                            'filename': file_data['name'],
                            'code': highlighted_code
                        })
                    except Exception as e:
                        self.write_to_console(f"Warning: Couldn't create code sample for {file_path_sample}: {str(e)}")
            except ImportError:
                self.write_to_console("Warning: Pygments not available, skipping code samples")

            # Prepare template data
            template_data = {
                'project_path': self.analysis_results['project_path'],
                'analysis_date': self.analysis_results['analysis_date'],
                'total_files': self.analysis_results['total_files'],
                'total_lines': self.analysis_results['total_lines'],
                'code_lines': self.analysis_results['code_lines'],
                'comment_lines': self.analysis_results['comment_lines'],
                'blank_lines': self.analysis_results['blank_lines'],
                'language_stats': language_stats,
                'largest_files': largest_files,
                'code_samples': code_samples,
                'rick_quote': self.analysis_results['rick_quote'],
                'current_year': datetime.now().year
            }

            # Render the template
            template = jinja2.Template(HTML_TEMPLATE)
            html_content = template.render(**template_data)

            # Write the HTML file with explicit encoding
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.write_to_console(f"HTML report generated: {file_path}")

            # Open the report in the default browser - several methods for different platforms
            self.write_to_console("Opening report in browser...")

            # Method 1: Direct with absolute path using webbrowser module
            import webbrowser
            url = f"file://{os.path.abspath(file_path)}"

            # First try the simplest method
            if webbrowser.open(url):
                self.write_to_console("Report opened successfully!")
                return

            # If that fails, try platform-specific methods
            import platform
            import subprocess

            system = platform.system().lower()

            if system == 'windows':
                # On Windows try with the 'start' command
                try:
                    os.startfile(file_path)
                    self.write_to_console("Report opened successfully with os.startfile!")
                    return
                except Exception:
                    try:
                        subprocess.run(['start', file_path], shell=True, check=True)
                        self.write_to_console("Report opened successfully with start command!")
                        return
                    except Exception as e:
                        self.write_to_console(f"Warning: Couldn't open browser with start command: {str(e)}")

            elif system == 'darwin':  # macOS
                try:
                    subprocess.run(['open', file_path], check=True)
                    self.write_to_console("Report opened successfully with open command!")
                    return
                except Exception as e:
                    self.write_to_console(f"Warning: Couldn't open browser with open command: {str(e)}")

            elif system == 'linux':
                try:
                    subprocess.run(['xdg-open', file_path], check=True)
                    self.write_to_console("Report opened successfully with xdg-open command!")
                    return
                except Exception as e:
                    self.write_to_console(f"Warning: Couldn't open browser with xdg-open command: {str(e)}")

            # If all else fails
            self.write_to_console(
                f"Warning: Couldn't open browser automatically. Please open this file manually:\n{file_path}")

        except Exception as e:
            self.write_to_console(f"Error generating report: {str(e)}")
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")

    def generate_fun_report(self):
        """Generate HTML report for fun analysis results."""
        if not self.fun_analysis_results:
            messagebox.showerror("Error", "Please run the Fun Analysis first")
            return
        if not FUN_MODULE_AVAILABLE:
            messagebox.showerror("Error", "Fun Analyzer module not found.")
            return
        # Check if Jinja2 is available (needed for templating)
        if not REPORT_PACKAGES_AVAILABLE:
            messagebox.showwarning("Warning", "Missing Jinja2 package. Cannot generate HTML report.")
            self.write_to_console("Cannot generate fun report: Jinja2 package missing (install jinja2).")
            return

        try:
            # We need jinja2 specifically for this report generation
            import jinja2

            self.write_to_console("\nGenerating Fun HTML report... This might get weird!")

            # --- Create Report Directory ---
            report_dir = os.path.join(os.path.expanduser("~"), "RickCodeAnalyzer")
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)

            # --- Create Filename ---
            project_name = os.path.basename(self.project_path.get())
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(report_dir, f"rick_fun_report_{project_name}_{timestamp}.html")

            # --- Prepare Template Data ---
            # The data should already be formatted correctly in self.fun_analysis_results
            # thanks to the change we will make in Step 5.
            template_data = self.fun_analysis_results

            # Ensure the data is a dictionary as expected
            if not isinstance(template_data, dict) or 'fun_score' not in template_data:
                self.write_to_console(
                    "Error: Fun analysis results are not in the expected dictionary format for reporting.")
                messagebox.showerror("Error", "Fun analysis results format error.")
                return

            # Add any other basic info needed by the template if not already present
            template_data['project_path'] = self.project_path.get()
            template_data['analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Ensure current_year is present if not added by fun_analyzer
            if 'current_year' not in template_data:
                template_data['current_year'] = datetime.now().year

            # --- Render and Write HTML ---
            template = jinja2.Template(FUN_HTML_TEMPLATE)  # Use the fun template defined earlier
            html_content = template.render(**template_data)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.write_to_console(f"Fun HTML report generated: {file_path}")

            # --- Open Report in Browser ---
            self.write_to_console("Opening report in browser...")
            self._open_report_in_browser(file_path)  # Use the helper method (defined below)

        # Handle missing Jinja2 specifically
        except ImportError:
            messagebox.showerror("Error", "Jinja2 package is required for HTML reports.")
            self.write_to_console("Error generating fun report: Jinja2 not found (install jinja2).")
        # Handle other potential errors during generation
        except Exception as e:
            self.write_to_console(f"Error generating fun report: {str(e)}")
            import traceback
            self.write_to_console(traceback.format_exc())  # Print detailed traceback
            messagebox.showerror("Error", f"Failed to generate fun report: {str(e)}")

    # --- New Helper Method ---
    # Action: Add this method as well. It avoids repeating code.
    # Place it right after generate_fun_report or generate_report.

    def _open_report_in_browser(self, file_path):
        """Helper function to open report file in browser across platforms."""
        # This code is copied directly from the original generate_report method's
        # browser opening logic to keep things DRY (Don't Repeat Yourself).
        try:
            # Try using the file URI scheme first
            # Use os.path.abspath to ensure the path is absolute
            abs_file_path = os.path.abspath(file_path)
            url = f"file://{abs_file_path}"

            if webbrowser.open(url):
                self.write_to_console("Report opened successfully using webbrowser!")
                return

            # Fallback to platform-specific methods if webbrowser.open fails
            system = platform.system().lower()

            if system == 'windows':
                try:
                    # os.startfile is often reliable on Windows
                    os.startfile(abs_file_path)
                    self.write_to_console("Report opened successfully with os.startfile!")
                    return
                except Exception:
                    # Try the 'start' command as a further fallback
                    subprocess.run(['start', '', abs_file_path], shell=True, check=True)
                    self.write_to_console("Report opened successfully with start command!")
                    return
            elif system == 'darwin':  # macOS
                subprocess.run(['open', abs_file_path], check=True)
                self.write_to_console("Report opened successfully with open command!")
                return
            elif system == 'linux':
                # xdg-open is the standard on most Linux distributions
                subprocess.run(['xdg-open', abs_file_path], check=True)
                self.write_to_console("Report opened successfully with xdg-open command!")
                return

        # Catch potential errors from any of the opening methods
        except Exception as e:
            self.write_to_console(f"Warning: Couldn't automatically open the report in browser: {str(e)}")
            self.write_to_console(f"Please open this file manually:\n{os.path.abspath(file_path)}")

    def collect_code_files(self, project_path):
        """Collect all code files in the project directory"""
        code_files = []

        for root, dirs, files in os.walk(project_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]

            for file in files:
                # Skip files starting with '.'
                if file.startswith('.'):
                    continue

                file_path = os.path.join(root, file)

                # Check if it's a code file based on extension
                ext = os.path.splitext(file)[1].lower()
                if self.get_language_from_extension(ext) != "Unknown":
                    code_files.append(file_path)

        return code_files

    def get_language_from_extension(self, extension):
        """Determine the programming language from file extension"""
        for language, extensions in CODE_EXTENSIONS.items():
            if extension in extensions:
                return language

        return "Unknown"

    def run_advanced_analysis(self):
        """Run advanced code analysis and generate detailed report"""
        if not self.analysis_results:
            messagebox.showerror("Error", "Please run the basic analysis first")
            return

        try:
            # Run advanced analysis in a separate thread
            self.write_to_console("\nStarting advanced analysis. Please wait...", delay=10)
            threading.Thread(target=self._run_advanced_analysis_thread, daemon=True).start()
        except Exception as e:
            self.write_to_console(f"\nError starting advanced analysis: {str(e)}")
            messagebox.showerror("Error", f"Failed to start advanced analysis: {str(e)}")

    def _run_advanced_analysis_thread(self):
        """Background thread for running advanced analysis"""
        try:
            project_path = self.project_path.get()

            # Create the advanced analyzer
            analyzer = AdvancedCodeAnalyzer(self.write_to_console)

            # Run the advanced analysis
            advanced_results = analyzer.analyze_project(
                project_path,
                self.analysis_results['file_stats']
            )

            # Display summary in console
            summary = analyzer.get_summary()
            recommendations = analyzer.get_recommendations()

            self.write_to_console("\n" + "=" * 40)
            self.write_to_console("ADVANCED ANALYSIS RESULTS")
            self.write_to_console("=" * 40)
            self.write_to_console("\n" + summary)
            self.write_to_console("\nRECOMMENDATIONS:")
            self.write_to_console(recommendations)

            # Generate an advanced HTML report
            self.write_to_console("\nGenerating advanced HTML report...")

            reporter = AdvancedReporter(self.write_to_console)
            report_path = reporter.generate_report(
                project_path,
                self.analysis_results,
                advanced_results
            )

            if report_path:
                self.write_to_console(f"Advanced HTML report generated: {report_path}")
                self.write_to_console("Opening report in browser...")
            else:
                self.write_to_console("Failed to generate advanced HTML report")

        except Exception as e:
            self.write_to_console(f"\nError during advanced analysis: {str(e)}")

    def run_fun_analysis(self):
        """Run fun code analysis."""
        if not self.analysis_results:
            messagebox.showerror("Error", "Please run the basic analysis first")
            return
        if not FUN_MODULE_AVAILABLE:
            messagebox.showerror("Error", "Fun Analyzer module (fun_analyzer.py) not found.")
            return

        try:
            # Run fun analysis in a separate thread
            self.write_to_console("\nStarting Fun Analysis. Let's get weird!", delay=10)
            threading.Thread(target=self._run_fun_analysis_thread, daemon=True).start()
        except Exception as e:
            self.write_to_console(f"\nError starting fun analysis: {str(e)}")
            messagebox.showerror("Error", f"Failed to start fun analysis: {str(e)}")

    def _run_fun_analysis_thread(self):
        """Background thread for running fun analysis."""
        try:
            project_path = self.project_path.get()
            analyzer = FunCodeAnalyzer(self.write_to_console)

            # --- CHANGE HERE ---
            # 1. Run the analysis
            # Note: analyzer.analyze_project returns the raw results dictionary
            # We don't strictly need to store this raw version unless used elsewhere.
            analyzer.analyze_project(
                project_path,
                self.analysis_results['file_stats']
            )

            # 2. Get the HTML-formatted data and store THAT
            self.fun_analysis_results = analyzer.get_html_report_data()
            # --- END OF CHANGE ---

            # Display summary in console (using the analyzer instance before it's gone)
            summary = analyzer.get_fun_summary()
            self.write_to_console("\n" + summary)

            self.write_to_console("\nFun analysis complete! Click 'GENERATE FUN REPORT' for the HTML version.")

            # Enable the fun report button (check it exists first)
            if hasattr(self, 'fun_report_button') and self.fun_report_button:
                self.after(0, lambda: self.fun_report_button.config(state=tk.NORMAL))

        except Exception as e:
            self.write_to_console(f"\nError during fun analysis: {str(e)}")
            import traceback
            self.write_to_console(traceback.format_exc())
            # Ensure button stays disabled on error
            if hasattr(self, 'fun_report_button') and self.fun_report_button:
                self.after(0, lambda: self.fun_report_button.config(state=tk.DISABLED))

            # Enable the fun report button
            self.after(0, lambda: self.fun_report_button.config(state=tk.NORMAL))

        except Exception as e:
            self.write_to_console(f"\nError during fun analysis: {str(e)}")
            # Ensure button stays disabled on error
            if hasattr(self, 'fun_report_button'):
                self.after(0, lambda: self.fun_report_button.config(state=tk.DISABLED))

if __name__ == "__main__":
    app = RetroConsole()
    app.mainloop()