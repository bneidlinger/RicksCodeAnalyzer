#!/usr/bin/env python3
# Advanced Reporter Module for Rick's Code Analyzer
# This module provides enhanced reporting capabilities

import os
import json
import random
import datetime
import webbrowser
import tempfile
from collections import defaultdict

# Required packages check
try:
    import jinja2
    from pygments import highlight
    from pygments.lexers import get_lexer_for_filename, guess_lexer
    from pygments.formatters import HtmlFormatter
    from pygments.util import ClassNotFound

    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

# More Rick quotes for reports
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
    "Your code has more issues than Rick's flask has liquor, and that's saying something!",
    "This code is like a time crystal - fundamentally unstable and likely to destroy the universe.",
    "You coded this like you're from a dimension where quality doesn't exist!",
    "I've synthesized mega-seeds with fewer complications than this codebase.",
    "Your variables are named worse than Unity's hive mind identifiers!",
    "This code's more twisted than my relationship with Bird Person... too soon?",
    "The Citadel has more order than your project structure... and I *burp* blew that place up!",
    "Looking at your code is like looking into the eyes of a gorgon... makes me want to turn to stone.",
    "Your error handling is about as effective as Jerry's job hunting.",
    "Even Simple Rick wouldn't be fooled by this code's fake simplicity.",
]

# Quality ratings and corresponding Rick comments
QUALITY_RATINGS = {
    'excellent': [
        "Holy *burp* crap! This code is cleaner than the Citadel's bathrooms. And those are CLEAN.",
        "I'd let this code drive my spaceship, and I don't let *anyone* drive my spaceship!",
        "This code's so good, I'm almost sober enough to appreciate it!",
        "Even Evil Morty couldn't find fault with this code. *burp* And he's a picky little sh*t.",
    ],
    'good': [
        "Not bad. Your code is like my Microverse battery. Efficient, but still has some dark secrets.",
        "I'd give this code a solid 'better than Jerry' rating. That's not saying much, but it's something.",
        "Your code works! I mean, it could be better, but, y'know... it's not the worst thing in the multiverse.",
        "This code is like Morty - mostly harmless and occasionally gets the job done."
    ],
    'fair': [
        "This code is like Jerry. It works, but nobody's excited about it.",
        "Your code is like the Vindicators - looks impressive until you look closely.",
        "The bar wasn't high, but you cleared it. Barely.",
        "This code is like a Plumbus – functional, but nobody knows why or how."
    ],
    'poor': [
        "Your code's a bigger mess than my garage. And I turn people into *burp* insects in there!",
        "This code is like a Meeseeks that's lived too long - painful to look at and desperately needs to end.",
        "Even the Zigerions could hack this code, and those guys are *burp* idiots!",
        "Your error handling reminds me of Morty's dating strategy: non-existent and bound to create problems."
    ],
    'very_poor': [
        "I've seen better code written by Gazorpazorps! And they eat their young!",
        "If your code were a person, I'd put it in Jerry daycare and forget about it.",
        "This code has more bugs than Anatomy Park after we miniaturized.",
        "Looking at this code hurts worse than when I have to be nice to Jerry."
    ]
}

# Report templates
HTML_REPORT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rick's Advanced Code Analysis Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=VT323&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');

        :root {
            --bg-color: #000000;
            --text-color: #00FF00;
            --highlight-color: #39FF14;
            --warning-color: #FF6000;
            --error-color: #FF0000;
            --critical-color: #FF00FF;
            --accent1-color: #00FFFF;
            --accent2-color: #FF00FF;
            --card-bg: rgba(0, 255, 0, 0.05);
            --code-bg: #1a1a1a;
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
            background-color: rgba(0, 20, 0, 0.8);
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
            background-color: var(--code-bg);
            border: 1px solid var(--text-color);
            border-radius: 5px;
            padding: 10px;
            overflow-x: auto;
            font-family: 'Roboto Mono', monospace;
            font-size: 14px;
        }

        code {
            font-family: 'Roboto Mono', monospace;
            background-color: rgba(0, 255, 0, 0.1);
            padding: 2px 4px;
            border-radius: 3px;
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
            background-color: var(--card-bg);
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.2);
        }

        .quote {
            font-style: italic;
            color: var(--warning-color);
            border-left: 3px solid var(--warning-color);
            padding-left: 15px;
            margin: 20px 0;
            font-size: 22px;
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

        .critical {
            color: var(--critical-color);
            font-weight: bold;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { text-shadow: 0 0 5px var(--critical-color); }
            50% { text-shadow: 0 0 20px var(--critical-color); }
            100% { text-shadow: 0 0 5px var(--critical-color); }
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

        .tab-container {
            margin-top: 20px;
        }

        .tab {
            overflow: hidden;
            border: 1px solid var(--text-color);
            background-color: var(--code-bg);
            border-radius: 5px 5px 0 0;
        }

        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 10px 15px;
            transition: 0.3s;
            font-family: 'VT323', monospace;
            font-size: 18px;
            color: var(--text-color);
        }

        .tab button:hover {
            background-color: rgba(0, 255, 0, 0.1);
        }

        .tab button.active {
            background-color: var(--card-bg);
            color: var(--accent1-color);
            text-shadow: 0 0 5px var(--accent1-color);
        }

        .tabcontent {
            display: none;
            padding: 15px;
            border: 1px solid var(--text-color);
            border-top: none;
            border-radius: 0 0 5px 5px;
            background-color: var(--card-bg);
        }

        .issue-card {
            margin-bottom: 15px;
            border: 1px solid var(--text-color);
            border-radius: 5px;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.4);
        }

        .issue-card h4 {
            margin: 0 0 10px 0;
            border-bottom: 1px solid var(--accent2-color);
            padding-bottom: 5px;
        }

        .issue-card p {
            margin: 5px 0;
        }

        .severity-badge {
            float: right;
            padding: 3px 8px;
            border-radius: 5px;
            font-size: 14px;
            font-weight: bold;
        }

        .severity-low {
            background-color: #004400;
            color: var(--text-color);
        }

        .severity-medium {
            background-color: #444400;
            color: #FFFF00;
        }

        .severity-high {
            background-color: #440000;
            color: var(--error-color);
        }

        .severity-critical {
            background-color: #440044;
            color: var(--critical-color);
            animation: pulse 2s infinite;
        }

        .metrics-chart {
            height: 300px;
            background-color: rgba(0, 0, 0, 0.4);
            border-radius: 5px;
            margin: 20px 0;
            position: relative;
        }

        .file-browser {
            height: 400px;
            overflow: auto;
            background-color: var(--code-bg);
            border: 1px solid var(--text-color);
            border-radius: 5px;
            padding: 10px;
            font-family: 'Roboto Mono', monospace;
            font-size: 14px;
        }

        .file-browser ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
        }

        .file-browser li {
            padding: 3px 10px;
            margin: 2px 0;
            cursor: pointer;
            border-radius: 3px;
        }

        .file-browser li:hover {
            background-color: rgba(0, 255, 0, 0.1);
        }

        .file-browser .file-issues {
            margin-left: 5px;
            padding: 0 5px;
            background-color: var(--warning-color);
            color: black;
            border-radius: 10px;
            font-size: 12px;
        }

        .file-browser .folder::before {
            content: "📁 ";
        }

        .file-browser .file::before {
            content: "📄 ";
        }

        .recommendations {
            list-style-type: none;
            padding: 0;
        }

        .recommendations li {
            margin-bottom: 15px;
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--text-color);
            border-radius: 5px;
            position: relative;
        }

        .recommendations li::before {
            content: "💡";
            margin-right: 10px;
            font-size: 20px;
        }

        .code-context {
            background-color: var(--code-bg);
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            font-family: 'Roboto Mono', monospace;
            font-size: 14px;
            overflow-x: auto;
        }

        .timeline {
            margin: 20px 0;
            position: relative;
            padding: 20px 0;
        }

        .timeline::before {
            content: '';
            position: absolute;
            width: 2px;
            background-color: var(--accent1-color);
            top: 0;
            bottom: 0;
            left: 50%;
            margin-left: -1px;
        }

        .timeline-item {
            position: relative;
            width: 45%;
            padding: 10px;
            background-color: var(--card-bg);
            border: 1px solid var(--text-color);
            border-radius: 5px;
            margin-bottom: 30px;
        }

        .timeline-item::after {
            content: '';
            position: absolute;
            top: 50%;
            width: 20px;
            height: 2px;
            background-color: var(--accent1-color);
        }

        .timeline-left {
            left: 0;
        }

        .timeline-right {
            left: 55%;
        }

        .timeline-left::after {
            right: -20px;
        }

        .timeline-right::after {
            left: -20px;
        }

        .timeline-date {
            color: var(--accent2-color);
            font-weight: bold;
        }

        @media (max-width: 768px) {
            .stat-container {
                flex-direction: column;
            }

            .stat-box {
                margin: 5px 0;
            }

            .timeline::before {
                left: 20px;
            }

            .timeline-item {
                width: calc(100% - 60px);
                left: 45px;
            }

            .timeline-item::after {
                left: -20px;
            }
        }
    </style>
    <script>
        // Will be populated during rendering
    </script>
</head>
<body>
    <div class="container">
        <div class="rickroll" onclick="alert('Never gonna give your code up, never gonna let your code down!')"></div>

        <h1>Rick's Advanced Code Analysis Report</h1>

        <div class="card">
            <h2>Project Quality Summary</h2>
            <div class="stat-container">
                <div class="stat-box">
                    <div class="stat-label">Maintainability</div>
                    <div class="stat-value">{{ maintainability_score }}/100</div>
                    <div>{{ maintainability_rating }}</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Technical Debt</div>
                    <div class="stat-value">{{ technical_debt_days }}</div>
                    <div>days to fix</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Code Issues</div>
                    <div class="stat-value">{{ total_issues }}</div>
                    <div>problems found</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">Files Analyzed</div>
                    <div class="stat-value">{{ total_files }}</div>
                    <div>{{ total_lines_of_code }} lines</div>
                </div>
            </div>

            <div class="quote">{{ rick_quote }}</div>

            <p>Project: <span class="highlight">{{ project_path }}</span></p>
            <p>Analysis Date: <span class="highlight">{{ analysis_date }}</span></p>
        </div>

        <div class="card">
            <h2>Project Metrics</h2>
            <div class="tab">
                <button class="tablinks active" onclick="openTab(event, 'OverallMetrics')">Overview</button>
                <button class="tablinks" onclick="openTab(event, 'LanguageStats')">Languages</button>
                <button class="tablinks" onclick="openTab(event, 'ComplexityMetrics')">Complexity</button>
                <button class="tablinks" onclick="openTab(event, 'FileMetrics')">Files</button>
            </div>

            <div id="OverallMetrics" class="tabcontent" style="display: block;">
                <div class="stat-container">
                    <div class="stat-box">
                        <div class="stat-label">Code Lines</div>
                        <div class="stat-value">{{ code_lines }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Comment Lines</div>
                        <div class="stat-value">{{ comment_lines }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Comment Density</div>
                        <div class="stat-value">{{ comment_density }}%</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Functions</div>
                        <div class="stat-value">{{ function_count }}</div>
                    </div>
                </div>
                <div class="metrics-chart" id="overallChart">
                    <!-- Chart will be rendered here -->
                </div>
            </div>

            <div id="LanguageStats" class="tabcontent">
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
                <div class="metrics-chart" id="languageChart">
                    <!-- Chart will be rendered here -->
                </div>
            </div>

            <div id="ComplexityMetrics" class="tabcontent">
                <div class="stat-container">
                    <div class="stat-box">
                        <div class="stat-label">Avg Function Complexity</div>
                        <div class="stat-value">{{ avg_function_complexity }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Avg Function Size</div>
                        <div class="stat-value">{{ avg_function_size }}</div>
                        <div>lines</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Avg Parameters</div>
                        <div class="stat-value">{{ avg_function_params }}</div>
                        <div>per function</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Duplicated Blocks</div>
                        <div class="stat-value">{{ duplicated_blocks }}</div>
                    </div>
                </div>
                <div class="metrics-chart" id="complexityChart">
                    <!-- Chart will be rendered here -->
                </div>
            </div>

            <div id="FileMetrics" class="tabcontent">
                <h3>Largest Files</h3>
                <table>
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Lines</th>
                            <th>Issues</th>
                            <th>Language</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for file in largest_files %}
                        <tr>
                            <td>{{ file.name }}</td>
                            <td>{{ file.lines }}</td>
                            <td>{{ file.issues }}</td>
                            <td>{{ file.language }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <h2>Issues Found</h2>
            <div class="tab">
                <button class="tablinks active" onclick="openTab(event, 'CodeSmells')">Code Smells</button>
                <button class="tablinks" onclick="openTab(event, 'SecurityIssues')">Security</button>
                <button class="tablinks" onclick="openTab(event, 'PerformanceIssues')">Performance</button>
                <button class="tablinks" onclick="openTab(event, 'StyleIssues')">Style</button>
                <button class="tablinks" onclick="openTab(event, 'DuplicatedCode')">Duplications</button>
            </div>

            <div id="CodeSmells" class="tabcontent" style="display: block;">
                <p>{{ code_smell_count }} code smells detected</p>

                {% for file_path, issues in code_smells.items() %}
                <div class="issue-card">
                    <h4>{{ file_path }}</h4>
                    {% for issue in issues %}
                    <p>
                        <span class="severity-badge severity-{{ issue.severity }}">{{ issue.severity }}</span>
                        Line {{ issue.line }}: {{ issue.description }}
                    </p>
                    {% if issue.context %}
                    <div class="code-context">{{ issue.context }}</div>
                    {% endif %}
                    {% endfor %}
                </div>
                {% endfor %}
            </div>

            <div id="SecurityIssues" class="tabcontent">
                <p>{{ security_issue_count }} security vulnerabilities detected</p>

                {% for file_path, issues in security_issues.items() %}
                <div class="issue-card">
                    <h4>{{ file_path }}</h4>
                    {% for issue in issues %}
                    <p>
                        <span class="severity-badge severity-{{ issue.severity }}">{{ issue.severity }}</span>
                        Line {{ issue.line }}: {{ issue.description }}
                    </p>
                    {% if issue.context %}
                    <div class="code-context">{{ issue.context }}</div>
                    {% endif %}
                    {% endfor %}
                </div>
                {% endfor %}
            </div>

            <div id="PerformanceIssues" class="tabcontent">
                <p>{{ performance_issue_count }} performance issues detected</p>

                {% for file_path, issues in performance_issues.items() %}
                <div class="issue-card">
                    <h4>{{ file_path }}</h4>
                    {% for issue in issues %}
                    <p>
                        <span class="severity-badge severity-{{ issue.severity }}">{{ issue.severity }}</span>
                        Line {{ issue.line }}: {{ issue.description }}
                    </p>
                    {% if issue.context %}
                    <div class="code-context">{{ issue.context }}</div>
                    {% endif %}
                    {% endfor %}
                </div>
                {% endfor %}
            </div>

            <div id="StyleIssues" class="tabcontent">
                <p>{{ style_issue_count }} style issues detected</p>

                {% for file_path, issues in style_issues.items() %}
                <div class="issue-card">
                    <h4>{{ file_path }}</h4>
                    {% for issue in issues %}
                    <p>
                        <span class="severity-badge severity-{{ issue.severity }}">{{ issue.severity }}</span>
                        Line {{ issue.line }}: {{ issue.description }}
                    </p>
                    {% if issue.context %}
                    <div class="code-context">{{ issue.context }}</div>
                    {% endif %}
                    {% endfor %}
                </div>
                {% endfor %}
            </div>

            <div id="DuplicatedCode" class="tabcontent">
                <p>{{ duplicated_blocks }} duplicated code blocks detected</p>

                {% for duplication in duplicated_code %}
                <div class="issue-card">
                    <h4>Duplicated Block ({{ duplication.size_lines }} lines)</h4>
                    <p>Found in:</p>
                    <ul>
                        {% for instance in duplication.instances %}
                        <li>{{ instance.file }} (lines {{ instance.start_line }}-{{ instance.end_line }})</li>
                        {% endfor %}
                    </ul>
                    <div class="code-context">{{ duplication.sample }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="card">
            <h2>Code Browser</h2>
            <div class="tab">
                <button class="tablinks active" onclick="openTab(event, 'FileBrowser')">Files</button>
                <button class="tablinks" onclick="openTab(event, 'DependencyGraph')">Dependencies</button>
            </div>

            <div id="FileBrowser" class="tabcontent" style="display: block;">
                <div class="file-browser">
                    <ul>
                        {% for file in file_tree %}
                        <li class="{{ file.type }}" onclick="showFileDetails('{{ file.path }}')">
                            {{ file.name }}
                            {% if file.issues > 0 %}
                            <span class="file-issues">{{ file.issues }}</span>
                            {% endif %}
                        </li>
                        {% endfor %}
                    </ul>
                </div>
                <div id="fileDetails" style="display: none;">
                    <h3 id="fileDetailsName"></h3>
                    <p id="fileDetailsInfo"></p>
                    <div id="fileDetailsIssues"></div>
                    {% if pygments_available %}
                    <div id="fileDetailsCode"></div>
                    {% endif %}
                </div>
            </div>

            <div id="DependencyGraph" class="tabcontent">
                <div id="dependencyGraphContainer" style="height: 500px; background-color: var(--code-bg);">
                    <!-- Dependency graph will be rendered here -->
                </div>
            </div>
        </div>

        <div class="card">
            <h2>Recommendations</h2>
            <ul class="recommendations">
                {% for recommendation in recommendations %}
                <li>{{ recommendation }}</li>
                {% endfor %}
            </ul>
        </div>

        {% if best_practices %}
        <div class="card">
            <h2>Best Practices</h2>
            <div class="tab">
                {% for language in best_practices.keys() %}
                <button class="tablinks {% if loop.first %}active{% endif %}" onclick="openTab(event, 'BestPractices{{ language|capitalize }}')">{{ language|capitalize }}</button>
                {% endfor %}
            </div>

            {% for language, practices in best_practices.items() %}
            <div id="BestPractices{{ language|capitalize }}" class="tabcontent" {% if loop.first %}style="display: block;"{% endif %}>
                <ul>
                    {% for practice in practices %}
                    <li>{{ practice }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <div class="footer">
            <p>Generated by Rick's Advanced Code Analyzer &copy; {{ current_year }} Wubba Lubba Dub Dub Inc.</p>
            <p>If this analysis seems wrong, remember that *burp* in an infinite multiverse, there's one where it's right.</p>
        </div>
    </div>

    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }

        function showFileDetails(filePath) {
            // This function will be replaced during rendering with actual file data
            console.log("Showing details for: " + filePath);
        }

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

        // Additional scripts for charts will be added during rendering
    </script>
</body>
</html>
'''


class AdvancedReporter:
    """Advanced report generation for Rick's Code Analyzer"""

    def __init__(self, callback_function=None):
        """Initialize the reporter

        Args:
            callback_function: Function to call for progress updates
        """
        self.callback = callback_function
        self.check_required_packages()

    def update_progress(self, message):
        """Update progress via callback"""
        if self.callback:
            self.callback(message)
        else:
            print(message)

    def check_required_packages(self):
        """Check for required packages for HTML report generation"""
        missing_packages = []

        try:
            import jinja2
        except ImportError:
            missing_packages.append("jinja2")

        if not PYGMENTS_AVAILABLE:
            missing_packages.append("pygments")

        if missing_packages:
            self.update_progress(
                f"Warning: Missing packages for full report functionality: {', '.join(missing_packages)}")
            self.update_progress(f"Install them with: pip install {' '.join(missing_packages)}")

    def generate_report(self, project_path, basic_analysis, advanced_analysis):
        """Generate an advanced HTML report

        Args:
            project_path: Path to the project directory
            basic_analysis: Basic analysis results dictionary
            advanced_analysis: Advanced analysis results dictionary

        Returns:
            Path to the generated report file
        """
        self.update_progress("Generating advanced HTML report...")

        try:
            import jinja2
        except ImportError:
            self.update_progress("Error: jinja2 is required for report generation")
            return None

        # Create a temporary directory for the report
        report_dir = tempfile.mkdtemp(prefix="ricks_analyzer_")
        self.update_progress(f"Created temporary directory: {report_dir}")

        # Create a filename based on the project name and timestamp
        project_name = os.path.basename(project_path)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(report_dir, f"rick_advanced_report_{project_name}_{timestamp}.html")

        # Prepare template data
        template_data = self._prepare_template_data(project_path, basic_analysis, advanced_analysis)

        # Render the template
        template = jinja2.Template(HTML_REPORT_TEMPLATE)
        html_content = template.render(**template_data)

        # Add dynamic JavaScript
        html_content = self._add_dynamic_javascript(html_content, template_data)

        # Write the HTML file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        self.update_progress(f"HTML report generated: {file_path}")

        # Open the report in the default browser
        try:
            webbrowser.open(f"file://{os.path.abspath(file_path)}")
            self.update_progress("Report opened in browser")
        except Exception as e:
            self.update_progress(f"Warning: Could not open browser automatically: {str(e)}")
            self.update_progress(f"Please open this file manually: {file_path}")

        return file_path

    def _prepare_template_data(self, project_path, basic_analysis, advanced_analysis):
        """Prepare data for the HTML template

        Args:
            project_path: Path to the project directory
            basic_analysis: Basic analysis results dictionary
            advanced_analysis: Advanced analysis results dictionary

        Returns:
            Dictionary of template data
        """
        # Extract metrics from advanced analysis
        metrics = advanced_analysis.get('complexity_metrics', {})

        # Get rating and quote
        maintainability_score = round(metrics.get('maintainability_index', 0))

        if maintainability_score >= 80:
            rating = "Excellent"
            quotes = QUALITY_RATINGS['excellent']
        elif maintainability_score >= 60:
            rating = "Good"
            quotes = QUALITY_RATINGS['good']
        elif maintainability_score >= 40:
            rating = "Fair"
            quotes = QUALITY_RATINGS['fair']
        elif maintainability_score >= 20:
            rating = "Poor"
            quotes = QUALITY_RATINGS['poor']
        else:
            rating = "Very Poor"
            quotes = QUALITY_RATINGS['very_poor']

        rick_quote = random.choice(quotes)

        # Count issues
        code_smell_count = sum(len(smells) for smells in advanced_analysis.get('code_smells', {}).values())
        security_issue_count = sum(len(issues) for issues in advanced_analysis.get('security_issues', {}).values())
        performance_issue_count = sum(
            len(issues) for issues in advanced_analysis.get('performance_issues', {}).values())
        style_issue_count = sum(len(issues) for issues in advanced_analysis.get('style_issues', {}).values())
        total_issues = code_smell_count + security_issue_count + performance_issue_count + style_issue_count

        # Create language stats list for the template
        language_stats = []
        for lang, count in basic_analysis.get('language_stats', {}).items():
            percentage = round((count / basic_analysis.get('total_files', 1)) * 100, 1)
            language_stats.append({
                'language': lang,
                'count': count,
                'percentage': percentage
            })

        # Sort by count descending
        language_stats.sort(key=lambda x: x['count'], reverse=True)

        # Get file statistics
        file_stats = basic_analysis.get('file_stats', {})

        # Add issue counts to file stats
        for file_path, stats in file_stats.items():
            issues = 0
            issues += len(advanced_analysis.get('code_smells', {}).get(file_path, []))
            issues += len(advanced_analysis.get('security_issues', {}).get(file_path, []))
            issues += len(advanced_analysis.get('performance_issues', {}).get(file_path, []))
            issues += len(advanced_analysis.get('style_issues', {}).get(file_path, []))
            stats['issues'] = issues

        # Get largest files
        largest_files = [
            {
                'name': os.path.basename(path),
                'lines': stats['lines'],
                'issues': stats.get('issues', 0),
                'language': stats['language']
            }
            for path, stats in sorted(file_stats.items(), key=lambda x: x[1]['lines'], reverse=True)[:10]
        ]

        # Create file tree for the browser
        file_tree = []
        for file_path, stats in file_stats.items():
            relative_path = os.path.relpath(file_path, project_path)
            file_tree.append({
                'name': os.path.basename(file_path),
                'path': relative_path,
                'type': 'file',
                'issues': stats.get('issues', 0),
                'language': stats['language']
            })

        # Sort by issue count (highest first)
        file_tree.sort(key=lambda x: x['issues'], reverse=True)

        # Prepare recommendations
        recommendations = []

        # Project quality recommendations
        if maintainability_score < 60:
            recommendations.append("Improve overall code maintainability by addressing technical debt")

        if metrics.get('comment_density', 0) < 0.1:
            recommendations.append("Increase code documentation - current comment density is too low")

        # Add language-specific recommendations
        for language, practices in advanced_analysis.get('best_practices', {}).items():
            if practices:
                for practice in practices[:1]:  # Just the first practice for each language
                    recommendations.append(f"For {language.capitalize()}: {practice}")

        # Find the top issue types
        issue_types = defaultdict(int)
        for issues in advanced_analysis.get('code_smells', {}).values():
            for issue in issues:
                issue_types[issue['type']] += 1

        for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:3]:
            if issue_type == 'long_function':
                recommendations.append(
                    f"Refactor {count} long functions by breaking them into smaller, more focused methods")
            elif issue_type == 'deep_nesting':
                recommendations.append(
                    f"Fix {count} instances of deep nesting by extracting methods or using early returns")
            elif issue_type == 'duplicate_code':
                recommendations.append(f"Eliminate {count} duplicated code blocks by creating reusable functions")

        # Security recommendations
        if security_issue_count > 0:
            recommendations.append("Address critical security vulnerabilities as a top priority")

        # Prepare data for JavaScript visualization
        # This will be added to the HTML as dynamic JavaScript

        return {
            'project_path': project_path,
            'analysis_date': advanced_analysis.get('analysis_metadata', {}).get('timestamp',
                                                                                datetime.datetime.now().isoformat()),
            'maintainability_score': maintainability_score,
            'maintainability_rating': rating,
            'technical_debt_days': metrics.get('technical_debt_days', 0),
            'total_issues': total_issues,
            'total_files': basic_analysis.get('total_files', 0),
            'total_lines_of_code': metrics.get('total_lines_of_code', 0),
            'code_lines': basic_analysis.get('code_lines', 0),
            'comment_lines': basic_analysis.get('comment_lines', 0),
            'comment_density': round(metrics.get('comment_density', 0) * 100, 1),
            'function_count': len(advanced_analysis.get('function_metrics', {})),
            'avg_function_complexity': round(metrics.get('avg_function_complexity', 0), 1),
            'avg_function_size': round(metrics.get('avg_function_size', 0), 1),
            'avg_function_params': round(metrics.get('avg_function_params', 0), 1),
            'duplicated_blocks': metrics.get('duplicated_code_blocks', 0),
            'language_stats': language_stats,
            'largest_files': largest_files,
            'file_tree': file_tree,
            'code_smell_count': code_smell_count,
            'security_issue_count': security_issue_count,
            'performance_issue_count': performance_issue_count,
            'style_issue_count': style_issue_count,
            'code_smells': advanced_analysis.get('code_smells', {}),
            'security_issues': advanced_analysis.get('security_issues', {}),
            'performance_issues': advanced_analysis.get('performance_issues', {}),
            'style_issues': advanced_analysis.get('style_issues', {}),
            'duplicated_code': advanced_analysis.get('duplicated_code', []),
            'recommendations': recommendations,
            'best_practices': advanced_analysis.get('best_practices', {}),
            'rick_quote': rick_quote,
            'current_year': datetime.datetime.now().year,
            'pygments_available': PYGMENTS_AVAILABLE,
            'file_details_json': json.dumps(file_stats)
        }

    def _add_dynamic_javascript(self, html_content, template_data):
        """Add dynamic JavaScript code to the HTML report

        Args:
            html_content: HTML content string
            template_data: Template data dictionary

        Returns:
            Updated HTML content with JavaScript
        """
        # Prepare charts data
        charts_js = self._generate_charts_js(template_data)

        # Prepare file details handler
        file_details_js = self._generate_file_details_js(template_data)

        # Insert JavaScript before the end of the script tag
        insert_pos = html_content.rfind('</script>')
        if insert_pos > 0:
            html_content = html_content[:insert_pos] + charts_js + file_details_js + html_content[insert_pos:]

        return html_content

    def _generate_charts_js(self, template_data):
        """Generate JavaScript code for charts

        Args:
            template_data: Template data dictionary

        Returns:
            JavaScript code for charts
        """
        # Create simple canvas-based charts (no external dependencies)
        js_code = """
        // Charts using canvas
        document.addEventListener('DOMContentLoaded', function() {
            // Function to create pie chart
            function createPieChart(canvasId, data, colors) {
                const canvas = document.getElementById(canvasId);
                if (!canvas) return;

                const ctx = canvas.getContext('2d');
                const width = canvas.width;
                const height = canvas.height;
                const centerX = width / 2;
                const centerY = height / 2;
                const radius = Math.min(centerX, centerY) * 0.8;

                let startAngle = 0;
                const total = data.reduce((sum, item) => sum + item.value, 0);

                // Draw the pie slices
                data.forEach((item, i) => {
                    const sliceAngle = 2 * Math.PI * item.value / total;
                    const endAngle = startAngle + sliceAngle;

                    ctx.beginPath();
                    ctx.moveTo(centerX, centerY);
                    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
                    ctx.closePath();

                    ctx.fillStyle = colors[i %% colors.length];
                    ctx.fill();

                    // Draw label
                    const labelAngle = startAngle + sliceAngle / 2;
                    const labelX = centerX + radius * 0.7 * Math.cos(labelAngle);
                    const labelY = centerY + radius * 0.7 * Math.sin(labelAngle);

                    ctx.fillStyle = '#00FF00';
                    ctx.font = '12px VT323';
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(item.label, labelX, labelY);

                    startAngle = endAngle;
                });

                // Draw legend
                const legendX = 10;
                let legendY = height - data.length * 20 - 10;

                data.forEach((item, i) => {
                    ctx.fillStyle = colors[i %% colors.length];
                    ctx.fillRect(legendX, legendY, 15, 15);

                    ctx.fillStyle = '#00FF00';
                    ctx.font = '14px VT323';
                    ctx.textAlign = 'left';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(`${item.label}: ${item.value}`, legendX + 25, legendY + 7);

                    legendY += 20;
                });
            }

            // Function to create bar chart
            function createBarChart(canvasId, data, title) {
                const canvas = document.getElementById(canvasId);
                if (!canvas) return;

                const ctx = canvas.getContext('2d');
                const width = canvas.width;
                const height = canvas.height;

                // Clear the canvas
                ctx.clearRect(0, 0, width, height);

                // Draw title
                ctx.fillStyle = '#00FFFF';
                ctx.font = '16px VT323';
                ctx.textAlign = 'center';
                ctx.fillText(title, width / 2, 20);

                // Set up chart dimensions
                const chartWidth = width - 60;
                const chartHeight = height - 80;
                const barSpacing = chartWidth / (data.length * 2 + 1);
                const barWidth = barSpacing;

                // Find max value for scaling
                const maxValue = Math.max(...data.map(item => item.value));

                // Draw bars
                data.forEach((item, i) => {
                    const barHeight = (item.value / maxValue) * chartHeight;
                    const x = 40 + barSpacing + (barSpacing * 2) * i;
                    const y = height - 40 - barHeight;

                    // Draw bar
                    ctx.fillStyle = '#00FFFF';
                    ctx.fillRect(x, y, barWidth, barHeight);

                    // Draw label
                    ctx.fillStyle = '#00FF00';
                    ctx.font = '12px VT323';
                    ctx.textAlign = 'center';
                    ctx.fillText(item.label, x + barWidth / 2, height - 25);

                    // Draw value
                    ctx.fillText(item.value.toString(), x + barWidth / 2, y - 10);
                });

                // Draw axes
                ctx.strokeStyle = '#00FF00';
                ctx.beginPath();
                ctx.moveTo(30, 40);
                ctx.lineTo(30, height - 40);
                ctx.lineTo(width - 20, height - 40);
                ctx.stroke();
            }

            // Overview chart - Issues by type
            const overallCanvas = document.createElement('canvas');
            overallCanvas.width = document.getElementById('overallChart').clientWidth;
            overallCanvas.height = document.getElementById('overallChart').clientHeight;
            document.getElementById('overallChart').appendChild(overallCanvas);

            createPieChart(overallCanvas.id, [
                { label: 'Code Smells', value: %d },
                { label: 'Security', value: %d },
                { label: 'Performance', value: %d },
                { label: 'Style', value: %d }
            ], ['#39FF14', '#FF00FF', '#00FFFF', '#FF6000']);

            // Language distribution chart
            const languageCanvas = document.createElement('canvas');
            languageCanvas.width = document.getElementById('languageChart').clientWidth;
            languageCanvas.height = document.getElementById('languageChart').clientHeight;
            document.getElementById('languageChart').appendChild(languageCanvas);

            createBarChart(languageCanvas.id, [
                %s
            ], 'Language Distribution');

            // Complexity metrics chart
            const complexityCanvas = document.createElement('canvas');
            complexityCanvas.width = document.getElementById('complexityChart').clientWidth;
            complexityCanvas.height = document.getElementById('complexityChart').clientHeight;
            document.getElementById('complexityChart').appendChild(complexityCanvas);

            createBarChart(complexityCanvas.id, [
                { label: 'Maintainability', value: %d },
                { label: 'Function Complexity', value: %d },
                { label: 'Avg Function Size', value: %d },
                { label: 'Technical Debt (days)', value: %d }
            ], 'Code Quality Metrics');
        });
        """ % (
            int(template_data['code_smell_count']),
            int(template_data['security_issue_count']),
            int(template_data['performance_issue_count']),
            int(template_data['style_issue_count']),
            ',\n                '.join([f"{{ label: '{lang['language']}', value: {lang['count']} }}" for lang in
                                        template_data['language_stats'][:5]]),
            int(float(template_data['maintainability_score'])),
            int(float(template_data['avg_function_complexity']) * 10),  # Scale for visualization
            int(float(template_data['avg_function_size'])),
            int(float(template_data['technical_debt_days']))
        )

        return js_code

    def _generate_file_details_js(self, template_data):
        """Generate JavaScript code for file details handling

        Args:
            template_data: Template data dictionary

        Returns:
            JavaScript code for file details
        """
        # Create handler for file details
        js_code = """
        // File details handler
        const fileDetails = %s;

        function showFileDetails(filePath) {
            const fileDetailsDiv = document.getElementById('fileDetails');
            const fileDetailsName = document.getElementById('fileDetailsName');
            const fileDetailsInfo = document.getElementById('fileDetailsInfo');
            const fileDetailsIssues = document.getElementById('fileDetailsIssues');

            // Find the file data
            const fileData = fileDetails[filePath];
            if (!fileData) {
                console.error('File data not found for', filePath);
                return;
            }

            // Show the details section
            fileDetailsDiv.style.display = 'block';

            // Update file name
            fileDetailsName.textContent = fileData.name;

            // Update file info
            fileDetailsInfo.innerHTML = `
                <p><span class="highlight">Language:</span> ${fileData.language}</p>
                <p><span class="highlight">Lines:</span> ${fileData.lines} total</p>
                <p><span class="highlight">Code:</span> ${fileData.code} lines</p>
                <p><span class="highlight">Comments:</span> ${fileData.comments} lines</p>
                <p><span class="highlight">Blank:</span> ${fileData.blank} lines</p>
            `;

            // Calculate issues for this file
            const codeSmells = document.querySelectorAll(`#CodeSmells .issue-card h4:contains('${filePath}')`).length;
            const securityIssues = document.querySelectorAll(`#SecurityIssues .issue-card h4:contains('${filePath}')`).length;
            const performanceIssues = document.querySelectorAll(`#PerformanceIssues .issue-card h4:contains('${filePath}')`).length;
            const styleIssues = document.querySelectorAll(`#StyleIssues .issue-card h4:contains('${filePath}')`).length;

            // Update issues section
            fileDetailsIssues.innerHTML = `
                <p><span class="highlight">Issues:</span></p>
                <ul>
                    <li><span class="highlight">Code Smells:</span> ${codeSmells}</li>
                    <li><span class="error">Security Issues:</span> ${securityIssues}</li>
                    <li><span class="warning">Performance Issues:</span> ${performanceIssues}</li>
                    <li>Style Issues: ${styleIssues}</li>
                </ul>
            `;
        }

        // Add contains selector for jQuery-like functionality
        document.querySelectorAll = function(selector) {
            try {
                return document.querySelectorAll(selector);
            } catch (e) {
                console.error('Error with selector:', selector, e);
                return [];
            }
        };

        Element.prototype.contains = function(text) {
            return this.innerText.includes(text);
        };
        """ % template_data.get('file_details_json', '{}')

        return js_code

    def generate_text_report(self, basic_analysis, advanced_analysis):
        """Generate a simple text report

        Args:
            basic_analysis: Basic analysis results dictionary
            advanced_analysis: Advanced analysis results dictionary

        Returns:
            Text report string
        """
        # Extract metrics from advanced analysis
        metrics = advanced_analysis.get('complexity_metrics', {})

        # Get rating and quote
        maintainability_score = round(metrics.get('maintainability_index', 0))

        if maintainability_score >= 80:
            rating = "Excellent"
            quotes = QUALITY_RATINGS['excellent']
        elif maintainability_score >= 60:
            rating = "Good"
            quotes = QUALITY_RATINGS['good']
        elif maintainability_score >= 40:
            rating = "Fair"
            quotes = QUALITY_RATINGS['fair']
        elif maintainability_score >= 20:
            rating = "Poor"
            quotes = QUALITY_RATINGS['poor']
        else:
            rating = "Very Poor"
            quotes = QUALITY_RATINGS['very_poor']

        rick_quote = random.choice(quotes)

        # Count issues
        code_smell_count = sum(len(smells) for smells in advanced_analysis.get('code_smells', {}).values())
        security_issue_count = sum(len(issues) for issues in advanced_analysis.get('security_issues', {}).values())
        performance_issue_count = sum(
            len(issues) for issues in advanced_analysis.get('performance_issues', {}).values())
        style_issue_count = sum(len(issues) for issues in advanced_analysis.get('style_issues', {}).values())

        # Build the text report
        report = [
            "==================================================",
            "           RICK'S ADVANCED CODE ANALYSIS          ",
            "==================================================",
            "",
            f"Project Quality: {rating} ({maintainability_score}/100)",
            f"Technical Debt: {metrics.get('technical_debt_days', 0)} days to fix",
            "",
            f"Rick says: \"{rick_quote}\"",
            "",
            "Issues Found:",
            f"- Code Smells: {code_smell_count}",
            f"- Security Issues: {security_issue_count}",
            f"- Performance Issues: {performance_issue_count}",
            f"- Style Issues: {style_issue_count}",
            "",
            "Project Metrics:",
            f"- Total Files: {basic_analysis.get('total_files', 0)}",
            f"- Total Lines: {metrics.get('total_lines_of_code', 0)}",
            f"- Code Lines: {basic_analysis.get('code_lines', 0)}",
            f"- Comment Lines: {basic_analysis.get('comment_lines', 0)}",
            f"- Comment Density: {round(metrics.get('comment_density', 0) * 100, 1)}%",
            f"- Duplicated Code Blocks: {metrics.get('duplicated_code_blocks', 0)}",
            f"- Avg Function Complexity: {round(metrics.get('avg_function_complexity', 0), 1)}",
            f"- Avg Function Size: {round(metrics.get('avg_function_size', 0), 1)} lines",
            ""
        ]

        # Add top issues
        if code_smell_count > 0:
            report.append("Top Code Smells:")
            issue_types = defaultdict(int)
            for issues in advanced_analysis.get('code_smells', {}).values():
                for issue in issues:
                    issue_types[issue['type']] += 1

            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:3]:
                report.append(f"- {issue_type}: {count} occurrences")

            report.append("")

        # Add security issues - these are important!
        if security_issue_count > 0:
            report.append("SECURITY VULNERABILITIES:")
            for file_path, issues in advanced_analysis.get('security_issues', {}).items():
                for issue in issues:
                    report.append(
                        f"- {os.path.basename(file_path)} (line {issue.get('line', '?')}): {issue.get('description', 'Unknown issue')}")

            report.append("")

        # Add recommendations
        report.append("Recommendations:")
        if maintainability_score < 60:
            report.append("- Improve overall code maintainability by addressing technical debt")

        if metrics.get('comment_density', 0) < 0.1:
            report.append("- Increase code documentation - current comment density is too low")

        # Find the top issue types
        if code_smell_count > 0:
            issue_types = defaultdict(int)
            for issues in advanced_analysis.get('code_smells', {}).values():
                for issue in issues:
                    issue_types[issue['type']] += 1

            for issue_type, count in sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:3]:
                if issue_type == 'long_function':
                    report.append(
                        f"- Refactor {count} long functions by breaking them into smaller, more focused methods")
                elif issue_type == 'deep_nesting':
                    report.append(
                        f"- Fix {count} instances of deep nesting by extracting methods or using early returns")
                elif issue_type == 'duplicate_code':
                    report.append(f"- Eliminate {count} duplicated code blocks by creating reusable functions")

        # Add language-specific best practices
        for language, practices in advanced_analysis.get('best_practices', {}).items():
            if practices:
                report.append(f"\nBest Practices for {language.capitalize()}:")
                for practice in practices[:3]:  # Top 3 practices
                    report.append(f"- {practice}")

        report.append("\nGenerated by Rick's Advanced Code Analyzer")
        report.append(
            "If this analysis seems wrong, remember that *burp* in an infinite multiverse, there's one where it's right.")

        return "\n".join(report)


# For standalone testing
if __name__ == "__main__":
    reporter = AdvancedReporter()

    # Sample data
    basic_analysis = {
        'total_files': 10,
        'total_lines': 1000,
        'code_lines': 800,
        'comment_lines': 100,
        'language_stats': {
            'Python': 5,
            'JavaScript': 3,
            'HTML': 2
        },
        'file_stats': {
            'test.py': {
                'name': 'test.py',
                'path': 'test.py',
                'lines': 100,
                'code': 80,
                'comments': 10,
                'blank': 10,
                'language': 'Python'
            }
        }
    }

    advanced_analysis = {
        'complexity_metrics': {
            'maintainability_index': 65,
            'technical_debt_days': 5,
            'total_lines_of_code': 1000,
            'comment_density': 0.1,
            'avg_function_complexity': 3.5,
            'avg_function_size': 15,
            'avg_function_params': 2.5,
            'duplicated_code_blocks': 2
        },
        'code_smells': {
            'test.py': [
                {
                    'type': 'long_function',
                    'description': 'Function is too long',
                    'severity': 'medium',
                    'line': 42
                }
            ]
        },
        'security_issues': {},
        'performance_issues': {},
        'style_issues': {},
        'best_practices': {
            'python': [
                'Use list comprehensions instead of map/filter when possible',
                'Follow PEP 8 style guide'
            ]
        }
    }

    text_report = reporter.generate_text_report(basic_analysis, advanced_analysis)
    print(text_report)

    # Uncomment to test HTML report generation
    # html_report = reporter.generate_report(".", basic_analysis, advanced_analysis)
    # print(f"HTML report: {html_report}")