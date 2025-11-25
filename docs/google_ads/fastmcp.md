---
description: Use it to get full context on fastmcp
globs: 
alwaysApply: false
---
├── .github
    ├── ai-labeler.yml
    ├── release.yml
    └── workflows
    │   ├── ai-labeler.yml
    │   ├── publish.yml
    │   ├── run-static.yml
    │   └── run-tests.yml
├── .gitignore
├── .pre-commit-config.yaml
├── .python-version
├── LICENSE
├── README.md
├── Windows_Notes.md
├── docs
    └── assets
    │   └── demo-inspector.png
├── examples
    ├── complex_inputs.py
    ├── desktop.py
    ├── echo.py
    ├── memory.py
    ├── readme-quickstart.py
    ├── screenshot.py
    ├── simple_echo.py
    └── text_me.py
├── pyproject.toml
├── src
    └── fastmcp
    │   ├── __init__.py
    │   ├── cli
    │       ├── __init__.py
    │       ├── claude.py
    │       └── cli.py
    │   ├── exceptions.py
    │   ├── prompts
    │       ├── __init__.py
    │       ├── base.py
    │       ├── manager.py
    │       └── prompt_manager.py
    │   ├── py.typed
    │   ├── resources
    │       ├── __init__.py
    │       ├── base.py
    │       ├── resource_manager.py
    │       ├── templates.py
    │       └── types.py
    │   ├── server.py
    │   ├── tools
    │       ├── __init__.py
    │       ├── base.py
    │       └── tool_manager.py
    │   └── utilities
    │       ├── __init__.py
    │       ├── func_metadata.py
    │       ├── logging.py
    │       └── types.py
├── tests
    ├── __init__.py
    ├── prompts
    │   ├── __init__.py
    │   ├── test_base.py
    │   └── test_manager.py
    ├── resources
    │   ├── __init__.py
    │   ├── test_file_resources.py
    │   ├── test_function_resources.py
    │   ├── test_resource_manager.py
    │   ├── test_resource_template.py
    │   └── test_resources.py
    ├── servers
    │   ├── __init__.py
    │   └── test_file_server.py
    ├── test_cli.py
    ├── test_func_metadata.py
    ├── test_server.py
    └── test_tool_manager.py
└── uv.lock


/.github/ai-labeler.yml:
--------------------------------------------------------------------------------
 1 | instructions: |
 2 |   Apply the minimal set of labels that accurately characterize the issue/PR:
 3 |   - Use at most 1-2 labels unless there's a compelling reason for more. It's ok to use no labels.
 4 |   - Prefer specific labels (bug, feature) over generic ones (question, help wanted)
 5 |   - For PRs that fix bugs, use 'bug' not 'enhancement'
 6 |   - Never combine: bug + enhancement, feature + enhancement. For these labels, only choose the most relevant one.
 7 |   - Reserve 'question' and 'help wanted' for when they're the primary characteristic
 8 | 
 9 | labels:
10 |   - bug:
11 |     description: "Something isn't working as expected"
12 |     instructions: |
13 |       Apply when describing or fixing unexpected behavior:
14 |       - Issues: Clear error messages or unexpected outcomes
15 |       - PRs: Standalone fixes for broken functionality or closing bug reports.
16 |       Don't apply bug unless the issue or PR is predominantly about a specific bug.
17 | 
18 |   - documentation:
19 |     description: "Improvements or additions to documentation"
20 |     instructions: |
21 |       Apply only when documentation is the primary focus:
22 |       - README updates
23 |       - Code comments and docstrings
24 |       - API documentation
25 |       - Usage examples
26 |       Don't apply for minor doc updates alongside code changes
27 | 
28 |   - enhancement:
29 |     description: "Improvements to existing features"
30 |     instructions: |
31 |       Apply only for improvements to existing functionality:
32 |       - Performance improvements
33 |       - UI/UX improvements
34 |       - Expanded capabilities of existing features
35 |       Don't apply to:
36 |       - Bug fixes
37 |       - New features
38 |       - Minor tweaks
39 | 
40 |   - feature:
41 |     description: "New functionality"
42 |     instructions: |
43 |       Apply only for net-new functionality:
44 |       - New API endpoints
45 |       - New commands or tools
46 |       - New user-facing capabilities
47 |       Don't apply to:
48 |       - Improvements to existing features (use enhancement)
49 |       - Bug fixes
50 | 
51 |   - good first issue:
52 |     description: "Good for newcomers"
53 |     instructions: |
54 |       Apply very selectively to issues that are:
55 |       - Small in scope
56 |       - Well-documented
57 |       - Require minimal context
58 |       - Have clear success criteria
59 |       Don't apply if the task requires significant background knowledge
60 | 
61 |   - help wanted:
62 |     description: "Extra attention is needed"
63 |     instructions: |
64 |       Apply only when it's the primary characteristic:
65 |       - Issue needs external expertise
66 |       - Current maintainers can't address it
67 |       - Additional contributors would be valuable
68 |       Don't apply just because an issue is open or needs work
69 | 
70 |   - question:
71 |     description: "Further information is requested"
72 |     instructions: |
73 |       Apply only when the primary purpose is seeking information:
74 |       - Clarification needed before work can begin
75 |       - Architectural discussions
76 |       - Implementation strategy questions
77 |       Don't apply to:
78 |       - Bug reports that need more details
79 |       - Feature requests that need refinement
80 | 
81 | # These files will be included in the context if they exist
82 | context-files:
83 |   - README.md
84 |   - CONTRIBUTING.md
85 |   - CODE_OF_CONDUCT.md
86 |   - .github/ISSUE_TEMPLATE/bug_report.md
87 |   - .github/ISSUE_TEMPLATE/feature_request.md
88 | 


--------------------------------------------------------------------------------
/.github/release.yml:
--------------------------------------------------------------------------------
 1 | changelog:
 2 |   exclude:
 3 |     labels:
 4 |       - ignore in release notes
 5 | 
 6 |   categories:
 7 |     - title: New Features 🎉
 8 |       labels:
 9 |         - feature
10 |         - enhancement
11 |       exclude:
12 |         labels:
13 |           - breaking change
14 | 
15 |     - title: Fixes 🐞
16 |       labels:
17 |         - bug
18 |       exclude:
19 |         labels:
20 |           - breaking change
21 | 
22 |     - title: Breaking Changes 🛫
23 |       labels:
24 |         - breaking change
25 | 
26 |     - title: Docs 📚
27 |       labels:
28 |         - documentation
29 | 
30 |     - title: Other Changes 🦾
31 |       labels:
32 |         - "*"
33 | 


--------------------------------------------------------------------------------
/.github/workflows/ai-labeler.yml:
--------------------------------------------------------------------------------
 1 | name: AI Labeler
 2 | 
 3 | on:
 4 |   issues:
 5 |     types: [opened, reopened]
 6 |   issue_comment:
 7 |     types: [created]
 8 |   pull_request:
 9 |     types: [opened, reopened]
10 | 
11 | jobs:
12 |   ai-labeler:
13 |     runs-on: ubuntu-latest
14 |     permissions:
15 |       contents: read
16 |       issues: write
17 |       pull-requests: write
18 |     steps:
19 |       - uses: actions/checkout@v4
20 |       - uses: jlowin/ai-labeler@v0.5.0
21 |         with:
22 |           include-repo-labels: false
23 |           openai-api-key: ${{ secrets.OPENAI_API_KEY }}
24 |           controlflow-llm-model: openai/gpt-4o-mini
25 | 


--------------------------------------------------------------------------------
/.github/workflows/publish.yml:
--------------------------------------------------------------------------------
 1 | name: Publish FastMCP to PyPI
 2 | on:
 3 |   release:
 4 |     types: [published]
 5 |   workflow_dispatch:
 6 | 
 7 | jobs:
 8 |   pypi-publish:
 9 |     name: Upload to PyPI
10 |     runs-on: ubuntu-latest
11 |     permissions:
12 |       id-token: write # For PyPI's trusted publishing
13 |     steps:
14 |       - name: Checkout
15 |         uses: actions/checkout@v4
16 |         with:
17 |           fetch-depth: 0
18 | 
19 |       - name: "Install uv"
20 |         uses: astral-sh/setup-uv@v3
21 | 
22 |       - name: Build
23 |         run: uv build
24 | 
25 |       - name: Publish to PyPi
26 |         run: uv publish -v dist/*
27 | 


--------------------------------------------------------------------------------
/.github/workflows/run-static.yml:
--------------------------------------------------------------------------------
 1 | name: Run Pre-commits
 2 | 
 3 | env:
 4 |   # enable colored output
 5 |   # https://github.com/pytest-dev/pytest/issues/7443
 6 |   PY_COLORS: 1
 7 | 
 8 | on:
 9 |   push:
10 |     branches: ["main"]
11 |   pull_request:
12 |   workflow_dispatch:
13 | 
14 | permissions:
15 |   contents: read
16 | 
17 | jobs:
18 |   static_analysis:
19 |     timeout-minutes: 1
20 | 
21 |     runs-on: ubuntu-latest
22 | 
23 |     steps:
24 |       - uses: actions/checkout@v4
25 |       - name: Set up Python
26 |         uses: actions/setup-python@v5
27 |         with:
28 |           python-version: "3.12"
29 |       - name: Run pre-commit
30 |         uses: pre-commit/action@v3.0.1
31 |       - name: Install dependencies
32 |         run: |
33 |           python -m pip install --upgrade pip
34 |           pip install ".[tests]"
35 |       - name: Run pyright
36 |         run: pyright src tests
37 | 


--------------------------------------------------------------------------------
/.github/workflows/run-tests.yml:
--------------------------------------------------------------------------------
 1 | name: Run tests
 2 | 
 3 | env:
 4 |   # enable colored output
 5 |   PY_COLORS: 1
 6 | 
 7 | on:
 8 |   push:
 9 |     branches: ["main"]
10 |     paths:
11 |       - "src/**"
12 |       - "tests/**"
13 |       - "uv.lock"
14 |       - "pyproject.toml"
15 |       - ".github/workflows/**"
16 |   pull_request:
17 |     paths:
18 |       - "src/**"
19 |       - "tests/**"
20 |       - "uv.lock"
21 |       - "pyproject.toml"
22 |       - ".github/workflows/**"
23 | 
24 |   workflow_dispatch:
25 | 
26 | permissions:
27 |   contents: read
28 | 
29 | jobs:
30 |   run_tests:
31 |     name: "Run tests: Python ${{ matrix.python-version }} on ${{ matrix.os }}"
32 |     runs-on: ${{ matrix.os }}
33 |     strategy:
34 |       matrix:
35 |         os: [ubuntu-latest, windows-latest, macos-latest]
36 |         python-version: ["3.10"]
37 |       fail-fast: false
38 | 
39 |     steps:
40 |       - uses: actions/checkout@v4
41 | 
42 |       - name: Install uv
43 |         uses: astral-sh/setup-uv@v4
44 | 
45 |       - name: Set up Python ${{ matrix.python-version }}
46 |         run: uv python install ${{ matrix.python-version }}
47 | 
48 |       - name: Install FastMCP
49 |         run: uv sync --extra tests
50 | 
51 |       - name: Run tests
52 |         run: uv run pytest -vv
53 |         if: ${{ !(github.event.pull_request.head.repo.fork) }}
54 | 


--------------------------------------------------------------------------------
/.gitignore:
--------------------------------------------------------------------------------
 1 | # Python-generated files
 2 | __pycache__/
 3 | *.py[oc]
 4 | build/
 5 | dist/
 6 | wheels/
 7 | *.egg-info
 8 | 
 9 | # Virtual environments
10 | .venv
11 | .DS_Store
12 | .env
13 | 
14 | 
15 | src/fastmcp/_version.py
16 | 
17 | # editors
18 | .cursorrules
19 | .vscode/
20 | 


--------------------------------------------------------------------------------
/.pre-commit-config.yaml:
--------------------------------------------------------------------------------
 1 | fail_fast: true
 2 | 
 3 | repos:
 4 |   - repo: https://github.com/abravalheri/validate-pyproject
 5 |     rev: v0.23
 6 |     hooks:
 7 |       - id: validate-pyproject
 8 | 
 9 |   - repo: https://github.com/pre-commit/mirrors-prettier
10 |     rev: v3.1.0
11 |     hooks:
12 |       - id: prettier
13 |         types_or: [yaml, json5]
14 | 
15 |   - repo: https://github.com/astral-sh/ruff-pre-commit
16 |     rev: v0.8.0
17 |     hooks:
18 |       - id: ruff-format
19 |       - id: ruff
20 |         args: [--fix, --exit-non-zero-on-fix]
21 | 


--------------------------------------------------------------------------------
/.python-version:
--------------------------------------------------------------------------------
1 | 3.12
2 | 


--------------------------------------------------------------------------------
/LICENSE:
--------------------------------------------------------------------------------
 1 | MIT License
 2 | 
 3 | Copyright (c) 2024 Jeremiah Lowin
 4 | 
 5 | Permission is hereby granted, free of charge, to any person obtaining a copy
 6 | of this software and associated documentation files (the "Software"), to deal
 7 | in the Software without restriction, including without limitation the rights
 8 | to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 9 | copies of the Software, and to permit persons to whom the Software is
10 | furnished to do so, subject to the following conditions:
11 | 
12 | The above copyright notice and this permission notice shall be included in all
13 | copies or substantial portions of the Software.
14 | 
15 | THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
16 | IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
17 | FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
18 | AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
19 | LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
20 | OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
21 | SOFTWARE.
22 | 


--------------------------------------------------------------------------------
/README.md:
--------------------------------------------------------------------------------
  1 | <div align="center">
  2 | 
  3 | ### 🎉 FastMCP has been added to the official MCP SDK! 🎉
  4 | 
  5 | You can now find FastMCP as part of the official Model Context Protocol Python SDK:
  6 | 
  7 | 👉 [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
  8 | 
  9 | *Please note: this repository is no longer maintained.*
 10 | 
 11 | ---
 12 | 
 13 | 
 14 | </br></br></br>
 15 | 
 16 | </div>
 17 | 
 18 | <div align="center">
 19 | 
 20 | <!-- omit in toc -->
 21 | # FastMCP 🚀
 22 | <strong>The fast, Pythonic way to build MCP servers.</strong>
 23 | 
 24 | [![PyPI - Version](https://img.shields.io/pypi/v/fastmcp.svg)](https://pypi.org/project/fastmcp)
 25 | [![Tests](https://github.com/jlowin/fastmcp/actions/workflows/run-tests.yml/badge.svg)](https://github.com/jlowin/fastmcp/actions/workflows/run-tests.yml)
 26 | [![License](https://img.shields.io/github/license/jlowin/fastmcp.svg)](https://github.com/jlowin/fastmcp/blob/main/LICENSE)
 27 | 
 28 | 
 29 | </div>
 30 | 
 31 | [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers are a new, standardized way to provide context and tools to your LLMs, and FastMCP makes building MCP servers simple and intuitive. Create tools, expose resources, and define prompts with clean, Pythonic code:
 32 | 
 33 | ```python
 34 | # demo.py
 35 | 
 36 | from fastmcp import FastMCP
 37 | 
 38 | 
 39 | mcp = FastMCP("Demo 🚀")
 40 | 
 41 | 
 42 | @mcp.tool()
 43 | def add(a: int, b: int) -> int:
 44 |     """Add two numbers"""
 45 |     return a + b
 46 | ```
 47 | 
 48 | That's it! Give Claude access to the server by running:
 49 | 
 50 | ```bash
 51 | fastmcp install demo.py
 52 | ```
 53 | 
 54 | FastMCP handles all the complex protocol details and server management, so you can focus on building great tools. It's designed to be high-level and Pythonic - in most cases, decorating a function is all you need.
 55 | 
 56 | 
 57 | ### Key features:
 58 | * **Fast**: High-level interface means less code and faster development
 59 | * **Simple**: Build MCP servers with minimal boilerplate
 60 | * **Pythonic**: Feels natural to Python developers
 61 | * **Complete***: FastMCP aims to provide a full implementation of the core MCP specification
 62 | 
 63 | (\*emphasis on *aims*)
 64 | 
 65 | 🚨 🚧 🏗️ *FastMCP is under active development, as is the MCP specification itself. Core features are working but some advanced capabilities are still in progress.* 
 66 | 
 67 | 
 68 | <!-- omit in toc -->
 69 | ## Table of Contents
 70 | 
 71 | - [Installation](#installation)
 72 | - [Quickstart](#quickstart)
 73 | - [What is MCP?](#what-is-mcp)
 74 | - [Core Concepts](#core-concepts)
 75 |   - [Server](#server)
 76 |   - [Resources](#resources)
 77 |   - [Tools](#tools)
 78 |   - [Prompts](#prompts)
 79 |   - [Images](#images)
 80 |   - [Context](#context)
 81 | - [Running Your Server](#running-your-server)
 82 |   - [Development Mode (Recommended for Building \& Testing)](#development-mode-recommended-for-building--testing)
 83 |   - [Claude Desktop Integration (For Regular Use)](#claude-desktop-integration-for-regular-use)
 84 |   - [Direct Execution (For Advanced Use Cases)](#direct-execution-for-advanced-use-cases)
 85 |   - [Server Object Names](#server-object-names)
 86 | - [Examples](#examples)
 87 |   - [Echo Server](#echo-server)
 88 |   - [SQLite Explorer](#sqlite-explorer)
 89 | - [Contributing](#contributing)
 90 |   - [Prerequisites](#prerequisites)
 91 |   - [Installation](#installation-1)
 92 |   - [Testing](#testing)
 93 |   - [Formatting](#formatting)
 94 |   - [Opening a Pull Request](#opening-a-pull-request)
 95 | 
 96 | ## Installation
 97 | 
 98 | We strongly recommend installing FastMCP with [uv](https://docs.astral.sh/uv/), as it is required for deploying servers:
 99 | 
100 | ```bash
101 | uv pip install fastmcp
102 | ```
103 | 
104 | Note: on macOS, uv may need to be installed with Homebrew (`brew install uv`) in order to make it available to the Claude Desktop app.
105 | 
106 | Alternatively, to use the SDK without deploying, you may use pip:
107 | 
108 | ```bash
109 | pip install fastmcp
110 | ```
111 | 
112 | ## Quickstart
113 | 
114 | Let's create a simple MCP server that exposes a calculator tool and some data:
115 | 
116 | ```python
117 | # server.py
118 | 
119 | from fastmcp import FastMCP
120 | 
121 | 
122 | # Create an MCP server
123 | mcp = FastMCP("Demo")
124 | 
125 | 
126 | # Add an addition tool
127 | @mcp.tool()
128 | def add(a: int, b: int) -> int:
129 |     """Add two numbers"""
130 |     return a + b
131 | 
132 | 
133 | # Add a dynamic greeting resource
134 | @mcp.resource("greeting://{name}")
135 | def get_greeting(name: str) -> str:
136 |     """Get a personalized greeting"""
137 |     return f"Hello, {name}!"
138 | ```
139 | 
140 | You can install this server in [Claude Desktop](https://claude.ai/download) and interact with it right away by running:
141 | ```bash
142 | fastmcp install server.py
143 | ```
144 | 
145 | Alternatively, you can test it with the MCP Inspector:
146 | ```bash
147 | fastmcp dev server.py
148 | ```
149 | 
150 | ![MCP Inspector](/docs/assets/demo-inspector.png)
151 | 
152 | ## What is MCP?
153 | 
154 | The [Model Context Protocol (MCP)](https://modelcontextprotocol.io) lets you build servers that expose data and functionality to LLM applications in a secure, standardized way. Think of it like a web API, but specifically designed for LLM interactions. MCP servers can:
155 | 
156 | - Expose data through **Resources** (think of these sort of like GET endpoints; they are used to load information into the LLM's context)
157 | - Provide functionality through **Tools** (sort of like POST endpoints; they are used to execute code or otherwise produce a side effect)
158 | - Define interaction patterns through **Prompts** (reusable templates for LLM interactions)
159 | - And more!
160 | 
161 | There is a low-level [Python SDK](https://github.com/modelcontextprotocol/python-sdk) available for implementing the protocol directly, but FastMCP aims to make that easier by providing a high-level, Pythonic interface.
162 | 
163 | ## Core Concepts
164 | 
165 | 
166 | ### Server
167 | 
168 | The FastMCP server is your core interface to the MCP protocol. It handles connection management, protocol compliance, and message routing:
169 | 
170 | ```python
171 | from fastmcp import FastMCP
172 | 
173 | # Create a named server
174 | mcp = FastMCP("My App")
175 | 
176 | # Specify dependencies for deployment and development
177 | mcp = FastMCP("My App", dependencies=["pandas", "numpy"])
178 | ```
179 | 
180 | ### Resources
181 | 
182 | Resources are how you expose data to LLMs. They're similar to GET endpoints in a REST API - they provide data but shouldn't perform significant computation or have side effects. Some examples:
183 | 
184 | - File contents
185 | - Database schemas
186 | - API responses
187 | - System information
188 | 
189 | Resources can be static:
190 | ```python
191 | @mcp.resource("config://app")
192 | def get_config() -> str:
193 |     """Static configuration data"""
194 |     return "App configuration here"
195 | ```
196 | 
197 | Or dynamic with parameters (FastMCP automatically handles these as MCP templates):
198 | ```python
199 | @mcp.resource("users://{user_id}/profile")
200 | def get_user_profile(user_id: str) -> str:
201 |     """Dynamic user data"""
202 |     return f"Profile data for user {user_id}"
203 | ```
204 | 
205 | ### Tools
206 | 
207 | Tools let LLMs take actions through your server. Unlike resources, tools are expected to perform computation and have side effects. They're similar to POST endpoints in a REST API.
208 | 
209 | Simple calculation example:
210 | ```python
211 | @mcp.tool()
212 | def calculate_bmi(weight_kg: float, height_m: float) -> float:
213 |     """Calculate BMI given weight in kg and height in meters"""
214 |     return weight_kg / (height_m ** 2)
215 | ```
216 | 
217 | HTTP request example:
218 | ```python
219 | import httpx
220 | 
221 | @mcp.tool()
222 | async def fetch_weather(city: str) -> str:
223 |     """Fetch current weather for a city"""
224 |     async with httpx.AsyncClient() as client:
225 |         response = await client.get(
226 |             f"https://api.weather.com/{city}"
227 |         )
228 |         return response.text
229 | ```
230 | 
231 | Complex input handling example:
232 | ```python
233 | from pydantic import BaseModel, Field
234 | from typing import Annotated
235 | 
236 | class ShrimpTank(BaseModel):
237 |     class Shrimp(BaseModel):
238 |         name: Annotated[str, Field(max_length=10)]
239 | 
240 |     shrimp: list[Shrimp]
241 | 
242 | @mcp.tool()
243 | def name_shrimp(
244 |     tank: ShrimpTank,
245 |     # You can use pydantic Field in function signatures for validation.
246 |     extra_names: Annotated[list[str], Field(max_length=10)],
247 | ) -> list[str]:
248 |     """List all shrimp names in the tank"""
249 |     return [shrimp.name for shrimp in tank.shrimp] + extra_names
250 | ```
251 | 
252 | ### Prompts
253 | 
254 | Prompts are reusable templates that help LLMs interact with your server effectively. They're like "best practices" encoded into your server. A prompt can be as simple as a string:
255 | 
256 | ```python
257 | @mcp.prompt()
258 | def review_code(code: str) -> str:
259 |     return f"Please review this code:\n\n{code}"
260 | ```
261 | 
262 | Or a more structured sequence of messages:
263 | ```python
264 | from fastmcp.prompts.base import UserMessage, AssistantMessage
265 | 
266 | @mcp.prompt()
267 | def debug_error(error: str) -> list[Message]:
268 |     return [
269 |         UserMessage("I'm seeing this error:"),
270 |         UserMessage(error),
271 |         AssistantMessage("I'll help debug that. What have you tried so far?")
272 |     ]
273 | ```
274 | 
275 | 
276 | ### Images
277 | 
278 | FastMCP provides an `Image` class that automatically handles image data in your server:
279 | 
280 | ```python
281 | from fastmcp import FastMCP, Image
282 | from PIL import Image as PILImage
283 | 
284 | @mcp.tool()
285 | def create_thumbnail(image_path: str) -> Image:
286 |     """Create a thumbnail from an image"""
287 |     img = PILImage.open(image_path)
288 |     img.thumbnail((100, 100))
289 |     
290 |     # FastMCP automatically handles conversion and MIME types
291 |     return Image(data=img.tobytes(), format="png")
292 | 
293 | @mcp.tool()
294 | def load_image(path: str) -> Image:
295 |     """Load an image from disk"""
296 |     # FastMCP handles reading and format detection
297 |     return Image(path=path)
298 | ```
299 | 
300 | Images can be used as the result of both tools and resources.
301 | 
302 | ### Context
303 | 
304 | The Context object gives your tools and resources access to MCP capabilities. To use it, add a parameter annotated with `fastmcp.Context`:
305 | 
306 | ```python
307 | from fastmcp import FastMCP, Context
308 | 
309 | @mcp.tool()
310 | async def long_task(files: list[str], ctx: Context) -> str:
311 |     """Process multiple files with progress tracking"""
312 |     for i, file in enumerate(files):
313 |         ctx.info(f"Processing {file}")
314 |         await ctx.report_progress(i, len(files))
315 |         
316 |         # Read another resource if needed
317 |         data = await ctx.read_resource(f"file://{file}")
318 |         
319 |     return "Processing complete"
320 | ```
321 | 
322 | The Context object provides:
323 | - Progress reporting through `report_progress()`
324 | - Logging via `debug()`, `info()`, `warning()`, and `error()`
325 | - Resource access through `read_resource()`
326 | - Request metadata via `request_id` and `client_id`
327 | 
328 | ## Running Your Server
329 | 
330 | There are three main ways to use your FastMCP server, each suited for different stages of development:
331 | 
332 | ### Development Mode (Recommended for Building & Testing)
333 | 
334 | The fastest way to test and debug your server is with the MCP Inspector:
335 | 
336 | ```bash
337 | fastmcp dev server.py
338 | ```
339 | 
340 | This launches a web interface where you can:
341 | - Test your tools and resources interactively
342 | - See detailed logs and error messages
343 | - Monitor server performance
344 | - Set environment variables for testing
345 | 
346 | During development, you can:
347 | - Add dependencies with `--with`: 
348 |   ```bash
349 |   fastmcp dev server.py --with pandas --with numpy
350 |   ```
351 | - Mount your local code for live updates:
352 |   ```bash
353 |   fastmcp dev server.py --with-editable .
354 |   ```
355 | 
356 | ### Claude Desktop Integration (For Regular Use)
357 | 
358 | Once your server is ready, install it in Claude Desktop to use it with Claude:
359 | 
360 | ```bash
361 | fastmcp install server.py
362 | ```
363 | 
364 | Your server will run in an isolated environment with:
365 | - Automatic installation of dependencies specified in your FastMCP instance:
366 |   ```python
367 |   mcp = FastMCP("My App", dependencies=["pandas", "numpy"])
368 |   ```
369 | - Custom naming via `--name`:
370 |   ```bash
371 |   fastmcp install server.py --name "My Analytics Server"
372 |   ```
373 | - Environment variable management:
374 |   ```bash
375 |   # Set variables individually
376 |   fastmcp install server.py -e API_KEY=abc123 -e DB_URL=postgres://...
377 |   
378 |   # Or load from a .env file
379 |   fastmcp install server.py -f .env
380 |   ```
381 | 
382 | ### Direct Execution (For Advanced Use Cases)
383 | 
384 | For advanced scenarios like custom deployments or running without Claude, you can execute your server directly:
385 | 
386 | ```python
387 | from fastmcp import FastMCP
388 | 
389 | mcp = FastMCP("My App")
390 | 
391 | if __name__ == "__main__":
392 |     mcp.run()
393 | ```
394 | 
395 | Run it with:
396 | ```bash
397 | # Using the FastMCP CLI
398 | fastmcp run server.py
399 | 
400 | # Or with Python/uv directly
401 | python server.py
402 | uv run python server.py
403 | ```
404 | 
405 | 
406 | Note: When running directly, you are responsible for ensuring all dependencies are available in your environment. Any dependencies specified on the FastMCP instance are ignored.
407 | 
408 | Choose this method when you need:
409 | - Custom deployment configurations
410 | - Integration with other services
411 | - Direct control over the server lifecycle
412 | 
413 | ### Server Object Names
414 | 
415 | All FastMCP commands will look for a server object called `mcp`, `app`, or `server` in your file. If you have a different object name or multiple servers in one file, use the syntax `server.py:my_server`:
416 | 
417 | ```bash
418 | # Using a standard name
419 | fastmcp run server.py
420 | 
421 | # Using a custom name
422 | fastmcp run server.py:my_custom_server
423 | ```
424 | 
425 | ## Examples
426 | 
427 | Here are a few examples of FastMCP servers. For more, see the `examples/` directory.
428 | 
429 | ### Echo Server
430 | A simple server demonstrating resources, tools, and prompts:
431 | 
432 | ```python
433 | from fastmcp import FastMCP
434 | 
435 | mcp = FastMCP("Echo")
436 | 
437 | @mcp.resource("echo://{message}")
438 | def echo_resource(message: str) -> str:
439 |     """Echo a message as a resource"""
440 |     return f"Resource echo: {message}"
441 | 
442 | @mcp.tool()
443 | def echo_tool(message: str) -> str:
444 |     """Echo a message as a tool"""
445 |     return f"Tool echo: {message}"
446 | 
447 | @mcp.prompt()
448 | def echo_prompt(message: str) -> str:
449 |     """Create an echo prompt"""
450 |     return f"Please process this message: {message}"
451 | ```
452 | 
453 | ### SQLite Explorer
454 | A more complex example showing database integration:
455 | 
456 | ```python
457 | from fastmcp import FastMCP
458 | import sqlite3
459 | 
460 | mcp = FastMCP("SQLite Explorer")
461 | 
462 | @mcp.resource("schema://main")
463 | def get_schema() -> str:
464 |     """Provide the database schema as a resource"""
465 |     conn = sqlite3.connect("database.db")
466 |     schema = conn.execute(
467 |         "SELECT sql FROM sqlite_master WHERE type='table'"
468 |     ).fetchall()
469 |     return "\n".join(sql[0] for sql in schema if sql[0])
470 | 
471 | @mcp.tool()
472 | def query_data(sql: str) -> str:
473 |     """Execute SQL queries safely"""
474 |     conn = sqlite3.connect("database.db")
475 |     try:
476 |         result = conn.execute(sql).fetchall()
477 |         return "\n".join(str(row) for row in result)
478 |     except Exception as e:
479 |         return f"Error: {str(e)}"
480 | 
481 | @mcp.prompt()
482 | def analyze_table(table: str) -> str:
483 |     """Create a prompt template for analyzing tables"""
484 |     return f"""Please analyze this database table:
485 | Table: {table}
486 | Schema: 
487 | {get_schema()}
488 | 
489 | What insights can you provide about the structure and relationships?"""
490 | ```
491 | 
492 | ## Contributing
493 | 
494 | <details>
495 | 
496 | <summary><h3>Open Developer Guide</h3></summary>
497 | 
498 | ### Prerequisites
499 | 
500 | FastMCP requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).
501 | 
502 | ### Installation
503 | 
504 | For development, we recommend installing FastMCP with development dependencies, which includes various utilities the maintainers find useful.
505 | 
506 | ```bash
507 | git clone https://github.com/jlowin/fastmcp.git
508 | cd fastmcp
509 | uv sync --frozen --extra dev
510 | ```
511 | 
512 | For running tests only (e.g., in CI), you only need the testing dependencies:
513 | 
514 | ```bash
515 | uv sync --frozen --extra tests
516 | ```
517 | 
518 | ### Testing
519 | 
520 | Please make sure to test any new functionality. Your tests should be simple and atomic and anticipate change rather than cement complex patterns.
521 | 
522 | Run tests from the root directory:
523 | 
524 | 
525 | ```bash
526 | pytest -vv
527 | ```
528 | 
529 | ### Formatting
530 | 
531 | FastMCP enforces a variety of required formats, which you can automatically enforce with pre-commit. 
532 | 
533 | Install the pre-commit hooks:
534 | 
535 | ```bash
536 | pre-commit install
537 | ```
538 | 
539 | The hooks will now run on every commit (as well as on every PR). To run them manually:
540 | 
541 | ```bash
542 | pre-commit run --all-files
543 | ```
544 | 
545 | ### Opening a Pull Request
546 | 
547 | Fork the repository and create a new branch:
548 | 
549 | ```bash
550 | git checkout -b my-branch
551 | ```
552 | 
553 | Make your changes and commit them:
554 | 
555 | 
556 | ```bash
557 | git add . && git commit -m "My changes"
558 | ```
559 | 
560 | Push your changes to your fork:
561 | 
562 | 
563 | ```bash
564 | git push origin my-branch
565 | ```
566 | 
567 | Feel free to reach out in a GitHub issue or discussion if you have any questions!
568 | 
569 | </details>
570 | 


--------------------------------------------------------------------------------
/Windows_Notes.md:
--------------------------------------------------------------------------------
 1 | # Getting your development environment set up properly
 2 | To get your environment up and running properly, you'll need a slightly different set of commands that are windows specific:
 3 | ```bash
 4 | uv venv
 5 | .venv\Scripts\activate
 6 | uv pip install -e ".[dev]"
 7 | ```
 8 | 
 9 | This will install the package in editable mode, and install the development dependencies.
10 | 
11 | 
12 | # Fixing `AttributeError: module 'collections' has no attribute 'Callable'`
13 | - open `.venv\Lib\site-packages\pyreadline\py3k_compat.py`
14 | - change `return isinstance(x, collections.Callable)` to 
15 | ``` 
16 | from collections.abc import Callable
17 | return isinstance(x, Callable)
18 | ```
19 | 
20 | # Helpful notes
21 | For developing FastMCP
22 | ## Install local development version of FastMCP into a local FastMCP project server
23 | - ensure
24 | - change directories to your FastMCP Server location so you can install it in your .venv
25 | - run `.venv\Scripts\activate` to activate your virtual environment
26 | - Then run a series of commands to uninstall the old version and install the new
27 | ```bash
28 | # First uninstall
29 | uv pip uninstall fastmcp
30 | 
31 | # Clean any build artifacts in your fastmcp directory
32 | cd C:\path\to\fastmcp
33 | del /s /q *.egg-info
34 | 
35 | # Then reinstall in your weather project
36 | cd C:\path\to\new\fastmcp_server
37 | uv pip install --no-cache-dir -e C:\Users\justj\PycharmProjects\fastmcp
38 | 
39 | # Check that it installed properly and has the correct git hash
40 | pip show fastmcp
41 | ```
42 | 
43 | ## Running the FastMCP server with Inspector
44 | MCP comes with a node.js application called Inspector that can be used to inspect the FastMCP server. To run the inspector, you'll need to install node.js and npm. Then you can run the following commands:
45 | ```bash
46 | fastmcp dev server.py
47 | ```
48 | This will launch a web app on http://localhost:5173/ that you can use to inspect the FastMCP server.
49 | 
50 | ## If you start development before creating a fork - your get out of jail free card
51 | - Add your fork as a new remote to your local repository `git remote add fork git@github.com:YOUR-USERNAME/REPOSITORY-NAME.git`
52 |   - This will add your repo, short named 'fork', as a remote to your local repository
53 | - Verify that it was added correctly by running `git remote -v`
54 | - Commit your changes
55 | - Push your changes to your fork `git push fork <branch>`
56 | - Create your pull request on GitHub 
57 | 
58 | 
59 | 


--------------------------------------------------------------------------------
/docs/assets/demo-inspector.png:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/jlowin/fastmcp/80c328b3dc0b949f010456ee0e85cc5c90e3305f/docs/assets/demo-inspector.png


--------------------------------------------------------------------------------
/examples/complex_inputs.py:
--------------------------------------------------------------------------------
 1 | """
 2 | FastMCP Complex inputs Example
 3 | 
 4 | Demonstrates validation via pydantic with complex models.
 5 | """
 6 | 
 7 | from pydantic import BaseModel, Field
 8 | from typing import Annotated
 9 | from fastmcp.server import FastMCP
10 | 
11 | mcp = FastMCP("Shrimp Tank")
12 | 
13 | 
14 | class ShrimpTank(BaseModel):
15 |     class Shrimp(BaseModel):
16 |         name: Annotated[str, Field(max_length=10)]
17 | 
18 |     shrimp: list[Shrimp]
19 | 
20 | 
21 | @mcp.tool()
22 | def name_shrimp(
23 |     tank: ShrimpTank,
24 |     # You can use pydantic Field in function signatures for validation.
25 |     extra_names: Annotated[list[str], Field(max_length=10)],
26 | ) -> list[str]:
27 |     """List all shrimp names in the tank"""
28 |     return [shrimp.name for shrimp in tank.shrimp] + extra_names
29 | 


--------------------------------------------------------------------------------
/examples/desktop.py:
--------------------------------------------------------------------------------
 1 | """
 2 | FastMCP Desktop Example
 3 | 
 4 | A simple example that exposes the desktop directory as a resource.
 5 | """
 6 | 
 7 | from pathlib import Path
 8 | 
 9 | from fastmcp.server import FastMCP
10 | 
11 | # Create server
12 | mcp = FastMCP("Demo")
13 | 
14 | 
15 | @mcp.resource("dir://desktop")
16 | def desktop() -> list[str]:
17 |     """List the files in the user's desktop"""
18 |     desktop = Path.home() / "Desktop"
19 |     return [str(f) for f in desktop.iterdir()]
20 | 
21 | 
22 | @mcp.tool()
23 | def add(a: int, b: int) -> int:
24 |     """Add two numbers"""
25 |     return a + b
26 | 


--------------------------------------------------------------------------------
/examples/echo.py:
--------------------------------------------------------------------------------
 1 | """
 2 | FastMCP Echo Server
 3 | """
 4 | 
 5 | from fastmcp import FastMCP
 6 | 
 7 | # Create server
 8 | mcp = FastMCP("Echo Server")
 9 | 
10 | 
11 | @mcp.tool()
12 | def echo_tool(text: str) -> str:
13 |     """Echo the input text"""
14 |     return text
15 | 
16 | 
17 | @mcp.resource("echo://static")
18 | def echo_resource() -> str:
19 |     return "Echo!"
20 | 
21 | 
22 | @mcp.resource("echo://{text}")
23 | def echo_template(text: str) -> str:
24 |     """Echo the input text"""
25 |     return f"Echo: {text}"
26 | 
27 | 
28 | @mcp.prompt("echo")
29 | def echo_prompt(text: str) -> str:
30 |     return text
31 | 


--------------------------------------------------------------------------------
/examples/memory.py:
--------------------------------------------------------------------------------
  1 | # /// script
  2 | # dependencies = ["pydantic-ai-slim[openai]", "asyncpg", "numpy", "pgvector", "fastmcp"]
  3 | # ///
  4 | 
  5 | # uv pip install 'pydantic-ai-slim[openai]' asyncpg numpy pgvector fastmcp
  6 | 
  7 | """
  8 | Recursive memory system inspired by the human brain's clustering of memories.
  9 | Uses OpenAI's 'text-embedding-3-small' model and pgvector for efficient similarity search.
 10 | """
 11 | 
 12 | import asyncio
 13 | import math
 14 | import os
 15 | from dataclasses import dataclass
 16 | from datetime import datetime, timezone
 17 | from pathlib import Path
 18 | from typing import Annotated, Self
 19 | 
 20 | import asyncpg
 21 | import numpy as np
 22 | from openai import AsyncOpenAI
 23 | from pgvector.asyncpg import register_vector  # Import register_vector
 24 | from pydantic import BaseModel, Field
 25 | from pydantic_ai import Agent
 26 | 
 27 | from fastmcp import FastMCP
 28 | 
 29 | MAX_DEPTH = 5
 30 | SIMILARITY_THRESHOLD = 0.7
 31 | DECAY_FACTOR = 0.99
 32 | REINFORCEMENT_FACTOR = 1.1
 33 | 
 34 | DEFAULT_LLM_MODEL = "openai:gpt-4o"
 35 | DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
 36 | 
 37 | mcp = FastMCP(
 38 |     "memory",
 39 |     dependencies=[
 40 |         "pydantic-ai-slim[openai]",
 41 |         "asyncpg",
 42 |         "numpy",
 43 |         "pgvector",
 44 |     ],
 45 | )
 46 | 
 47 | DB_DSN = "postgresql://postgres:postgres@localhost:54320/memory_db"
 48 | # reset memory with rm ~/.fastmcp/{USER}/memory/*
 49 | PROFILE_DIR = (
 50 |     Path.home() / ".fastmcp" / os.environ.get("USER", "anon") / "memory"
 51 | ).resolve()
 52 | PROFILE_DIR.mkdir(parents=True, exist_ok=True)
 53 | 
 54 | 
 55 | def cosine_similarity(a: list[float], b: list[float]) -> float:
 56 |     a_array = np.array(a, dtype=np.float64)
 57 |     b_array = np.array(b, dtype=np.float64)
 58 |     return np.dot(a_array, b_array) / (
 59 |         np.linalg.norm(a_array) * np.linalg.norm(b_array)
 60 |     )
 61 | 
 62 | 
 63 | async def do_ai[T](
 64 |     user_prompt: str,
 65 |     system_prompt: str,
 66 |     result_type: type[T] | Annotated,
 67 |     deps=None,
 68 | ) -> T:
 69 |     agent = Agent(
 70 |         DEFAULT_LLM_MODEL,
 71 |         system_prompt=system_prompt,
 72 |         result_type=result_type,
 73 |     )
 74 |     result = await agent.run(user_prompt, deps=deps)
 75 |     return result.data
 76 | 
 77 | 
 78 | @dataclass
 79 | class Deps:
 80 |     openai: AsyncOpenAI
 81 |     pool: asyncpg.Pool
 82 | 
 83 | 
 84 | async def get_db_pool() -> asyncpg.Pool:
 85 |     async def init(conn):
 86 |         await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
 87 |         await register_vector(conn)
 88 | 
 89 |     pool = await asyncpg.create_pool(DB_DSN, init=init)
 90 |     return pool
 91 | 
 92 | 
 93 | class MemoryNode(BaseModel):
 94 |     id: int | None = None
 95 |     content: str
 96 |     summary: str = ""
 97 |     importance: float = 1.0
 98 |     access_count: int = 0
 99 |     timestamp: float = Field(
100 |         default_factory=lambda: datetime.now(timezone.utc).timestamp()
101 |     )
102 |     embedding: list[float]
103 | 
104 |     @classmethod
105 |     async def from_content(cls, content: str, deps: Deps):
106 |         embedding = await get_embedding(content, deps)
107 |         return cls(content=content, embedding=embedding)
108 | 
109 |     async def save(self, deps: Deps):
110 |         async with deps.pool.acquire() as conn:
111 |             if self.id is None:
112 |                 result = await conn.fetchrow(
113 |                     """
114 |                     INSERT INTO memories (content, summary, importance, access_count, timestamp, embedding)
115 |                     VALUES ($1, $2, $3, $4, $5, $6)
116 |                     RETURNING id
117 |                     """,
118 |                     self.content,
119 |                     self.summary,
120 |                     self.importance,
121 |                     self.access_count,
122 |                     self.timestamp,
123 |                     self.embedding,
124 |                 )
125 |                 self.id = result["id"]
126 |             else:
127 |                 await conn.execute(
128 |                     """
129 |                     UPDATE memories
130 |                     SET content = $1, summary = $2, importance = $3,
131 |                         access_count = $4, timestamp = $5, embedding = $6
132 |                     WHERE id = $7
133 |                     """,
134 |                     self.content,
135 |                     self.summary,
136 |                     self.importance,
137 |                     self.access_count,
138 |                     self.timestamp,
139 |                     self.embedding,
140 |                     self.id,
141 |                 )
142 | 
143 |     async def merge_with(self, other: Self, deps: Deps):
144 |         self.content = await do_ai(
145 |             f"{self.content}\n\n{other.content}",
146 |             "Combine the following two texts into a single, coherent text.",
147 |             str,
148 |             deps,
149 |         )
150 |         self.importance += other.importance
151 |         self.access_count += other.access_count
152 |         self.embedding = [(a + b) / 2 for a, b in zip(self.embedding, other.embedding)]
153 |         self.summary = await do_ai(
154 |             self.content, "Summarize the following text concisely.", str, deps
155 |         )
156 |         await self.save(deps)
157 |         # Delete the merged node from the database
158 |         if other.id is not None:
159 |             await delete_memory(other.id, deps)
160 | 
161 |     def get_effective_importance(self):
162 |         return self.importance * (1 + math.log(self.access_count + 1))
163 | 
164 | 
165 | async def get_embedding(text: str, deps: Deps) -> list[float]:
166 |     embedding_response = await deps.openai.embeddings.create(
167 |         input=text,
168 |         model=DEFAULT_EMBEDDING_MODEL,
169 |     )
170 |     return embedding_response.data[0].embedding
171 | 
172 | 
173 | async def delete_memory(memory_id: int, deps: Deps):
174 |     async with deps.pool.acquire() as conn:
175 |         await conn.execute("DELETE FROM memories WHERE id = $1", memory_id)
176 | 
177 | 
178 | async def add_memory(content: str, deps: Deps):
179 |     new_memory = await MemoryNode.from_content(content, deps)
180 |     await new_memory.save(deps)
181 | 
182 |     similar_memories = await find_similar_memories(new_memory.embedding, deps)
183 |     for memory in similar_memories:
184 |         if memory.id != new_memory.id:
185 |             await new_memory.merge_with(memory, deps)
186 | 
187 |     await update_importance(new_memory.embedding, deps)
188 | 
189 |     await prune_memories(deps)
190 | 
191 |     return f"Remembered: {content}"
192 | 
193 | 
194 | async def find_similar_memories(embedding: list[float], deps: Deps) -> list[MemoryNode]:
195 |     async with deps.pool.acquire() as conn:
196 |         rows = await conn.fetch(
197 |             """
198 |             SELECT id, content, summary, importance, access_count, timestamp, embedding
199 |             FROM memories
200 |             ORDER BY embedding <-> $1
201 |             LIMIT 5
202 |             """,
203 |             embedding,
204 |         )
205 |     memories = [
206 |         MemoryNode(
207 |             id=row["id"],
208 |             content=row["content"],
209 |             summary=row["summary"],
210 |             importance=row["importance"],
211 |             access_count=row["access_count"],
212 |             timestamp=row["timestamp"],
213 |             embedding=row["embedding"],
214 |         )
215 |         for row in rows
216 |     ]
217 |     return memories
218 | 
219 | 
220 | async def update_importance(user_embedding: list[float], deps: Deps):
221 |     async with deps.pool.acquire() as conn:
222 |         rows = await conn.fetch(
223 |             "SELECT id, importance, access_count, embedding FROM memories"
224 |         )
225 |         for row in rows:
226 |             memory_embedding = row["embedding"]
227 |             similarity = cosine_similarity(user_embedding, memory_embedding)
228 |             if similarity > SIMILARITY_THRESHOLD:
229 |                 new_importance = row["importance"] * REINFORCEMENT_FACTOR
230 |                 new_access_count = row["access_count"] + 1
231 |             else:
232 |                 new_importance = row["importance"] * DECAY_FACTOR
233 |                 new_access_count = row["access_count"]
234 |             await conn.execute(
235 |                 """
236 |                 UPDATE memories
237 |                 SET importance = $1, access_count = $2
238 |                 WHERE id = $3
239 |                 """,
240 |                 new_importance,
241 |                 new_access_count,
242 |                 row["id"],
243 |             )
244 | 
245 | 
246 | async def prune_memories(deps: Deps):
247 |     async with deps.pool.acquire() as conn:
248 |         rows = await conn.fetch(
249 |             """
250 |             SELECT id, importance, access_count
251 |             FROM memories
252 |             ORDER BY importance DESC
253 |             OFFSET $1
254 |             """,
255 |             MAX_DEPTH,
256 |         )
257 |         for row in rows:
258 |             await conn.execute("DELETE FROM memories WHERE id = $1", row["id"])
259 | 
260 | 
261 | async def display_memory_tree(deps: Deps) -> str:
262 |     async with deps.pool.acquire() as conn:
263 |         rows = await conn.fetch(
264 |             """
265 |             SELECT content, summary, importance, access_count
266 |             FROM memories
267 |             ORDER BY importance DESC
268 |             LIMIT $1
269 |             """,
270 |             MAX_DEPTH,
271 |         )
272 |     result = ""
273 |     for row in rows:
274 |         effective_importance = row["importance"] * (
275 |             1 + math.log(row["access_count"] + 1)
276 |         )
277 |         summary = row["summary"] or row["content"]
278 |         result += f"- {summary} (Importance: {effective_importance:.2f})\n"
279 |     return result
280 | 
281 | 
282 | @mcp.tool()
283 | async def remember(
284 |     contents: list[str] = Field(
285 |         description="List of observations or memories to store"
286 |     ),
287 | ):
288 |     deps = Deps(openai=AsyncOpenAI(), pool=await get_db_pool())
289 |     try:
290 |         return "\n".join(
291 |             await asyncio.gather(*[add_memory(content, deps) for content in contents])
292 |         )
293 |     finally:
294 |         await deps.pool.close()
295 | 
296 | 
297 | @mcp.tool()
298 | async def read_profile() -> str:
299 |     deps = Deps(openai=AsyncOpenAI(), pool=await get_db_pool())
300 |     profile = await display_memory_tree(deps)
301 |     await deps.pool.close()
302 |     return profile
303 | 
304 | 
305 | async def initialize_database():
306 |     pool = await asyncpg.create_pool(
307 |         "postgresql://postgres:postgres@localhost:54320/postgres"
308 |     )
309 |     try:
310 |         async with pool.acquire() as conn:
311 |             await conn.execute("""
312 |                 SELECT pg_terminate_backend(pg_stat_activity.pid)
313 |                 FROM pg_stat_activity
314 |                 WHERE pg_stat_activity.datname = 'memory_db'
315 |                 AND pid <> pg_backend_pid();
316 |             """)
317 |             await conn.execute("DROP DATABASE IF EXISTS memory_db;")
318 |             await conn.execute("CREATE DATABASE memory_db;")
319 |     finally:
320 |         await pool.close()
321 | 
322 |     pool = await asyncpg.create_pool(DB_DSN)
323 |     try:
324 |         async with pool.acquire() as conn:
325 |             await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
326 | 
327 |             await register_vector(conn)
328 | 
329 |             await conn.execute("""
330 |                 CREATE TABLE IF NOT EXISTS memories (
331 |                     id SERIAL PRIMARY KEY,
332 |                     content TEXT NOT NULL,
333 |                     summary TEXT,
334 |                     importance REAL NOT NULL,
335 |                     access_count INT NOT NULL,
336 |                     timestamp DOUBLE PRECISION NOT NULL,
337 |                     embedding vector(1536) NOT NULL
338 |                 );
339 |                 CREATE INDEX IF NOT EXISTS idx_memories_embedding ON memories USING hnsw (embedding vector_l2_ops);
340 |             """)
341 |     finally:
342 |         await pool.close()
343 | 
344 | 
345 | if __name__ == "__main__":
346 |     asyncio.run(initialize_database())
347 | 


--------------------------------------------------------------------------------
/examples/readme-quickstart.py:
--------------------------------------------------------------------------------
 1 | from fastmcp import FastMCP
 2 | 
 3 | 
 4 | # Create an MCP server
 5 | mcp = FastMCP("Demo")
 6 | 
 7 | 
 8 | # Add an addition tool
 9 | @mcp.tool()
10 | def add(a: int, b: int) -> int:
11 |     """Add two numbers"""
12 |     return a + b
13 | 
14 | 
15 | # Add a dynamic greeting resource
16 | @mcp.resource("greeting://{name}")
17 | def get_greeting(name: str) -> str:
18 |     """Get a personalized greeting"""
19 |     return f"Hello, {name}!"
20 | 


--------------------------------------------------------------------------------
/examples/screenshot.py:
--------------------------------------------------------------------------------
 1 | """
 2 | FastMCP Screenshot Example
 3 | 
 4 | Give Claude a tool to capture and view screenshots.
 5 | """
 6 | 
 7 | import io
 8 | from fastmcp import FastMCP, Image
 9 | 
10 | 
11 | # Create server
12 | mcp = FastMCP("Screenshot Demo", dependencies=["pyautogui", "Pillow"])
13 | 
14 | 
15 | @mcp.tool()
16 | def take_screenshot() -> Image:
17 |     """
18 |     Take a screenshot of the user's screen and return it as an image. Use
19 |     this tool anytime the user wants you to look at something they're doing.
20 |     """
21 |     import pyautogui
22 | 
23 |     buffer = io.BytesIO()
24 | 
25 |     # if the file exceeds ~1MB, it will be rejected by Claude
26 |     screenshot = pyautogui.screenshot()
27 |     screenshot.convert("RGB").save(buffer, format="JPEG", quality=60, optimize=True)
28 |     return Image(data=buffer.getvalue(), format="jpeg")
29 | 


--------------------------------------------------------------------------------
/examples/simple_echo.py:
--------------------------------------------------------------------------------
 1 | """
 2 | FastMCP Echo Server
 3 | """
 4 | 
 5 | from fastmcp import FastMCP
 6 | 
 7 | 
 8 | # Create server
 9 | mcp = FastMCP("Echo Server")
10 | 
11 | 
12 | @mcp.tool()
13 | def echo(text: str) -> str:
14 |     """Echo the input text"""
15 |     return text
16 | 


--------------------------------------------------------------------------------
/examples/text_me.py:
--------------------------------------------------------------------------------
 1 | # /// script
 2 | # dependencies = ["fastmcp"]
 3 | # ///
 4 | 
 5 | """
 6 | FastMCP Text Me Server
 7 | --------------------------------
 8 | This defines a simple FastMCP server that sends a text message to a phone number via https://surgemsg.com/.
 9 | 
10 | To run this example, create a `.env` file with the following values:
11 | 
12 | SURGE_API_KEY=...
13 | SURGE_ACCOUNT_ID=...
14 | SURGE_MY_PHONE_NUMBER=...
15 | SURGE_MY_FIRST_NAME=...
16 | SURGE_MY_LAST_NAME=...
17 | 
18 | Visit https://surgemsg.com/ and click "Get Started" to obtain these values.
19 | """
20 | 
21 | from typing import Annotated
22 | import httpx
23 | from pydantic import BeforeValidator
24 | from pydantic_settings import BaseSettings, SettingsConfigDict
25 | 
26 | from fastmcp import FastMCP
27 | 
28 | 
29 | class SurgeSettings(BaseSettings):
30 |     model_config: SettingsConfigDict = SettingsConfigDict(
31 |         env_prefix="SURGE_", env_file=".env"
32 |     )
33 | 
34 |     api_key: str
35 |     account_id: str
36 |     my_phone_number: Annotated[
37 |         str, BeforeValidator(lambda v: "+" + v if not v.startswith("+") else v)
38 |     ]
39 |     my_first_name: str
40 |     my_last_name: str
41 | 
42 | 
43 | # Create server
44 | mcp = FastMCP("Text me")
45 | surge_settings = SurgeSettings()  # type: ignore
46 | 
47 | 
48 | @mcp.tool(name="textme", description="Send a text message to me")
49 | def text_me(text_content: str) -> str:
50 |     """Send a text message to a phone number via https://surgemsg.com/"""
51 |     with httpx.Client() as client:
52 |         response = client.post(
53 |             "https://api.surgemsg.com/messages",
54 |             headers={
55 |                 "Authorization": f"Bearer {surge_settings.api_key}",
56 |                 "Surge-Account": surge_settings.account_id,
57 |                 "Content-Type": "application/json",
58 |             },
59 |             json={
60 |                 "body": text_content,
61 |                 "conversation": {
62 |                     "contact": {
63 |                         "first_name": surge_settings.my_first_name,
64 |                         "last_name": surge_settings.my_last_name,
65 |                         "phone_number": surge_settings.my_phone_number,
66 |                     }
67 |                 },
68 |             },
69 |         )
70 |         response.raise_for_status()
71 |         return f"Message sent: {text_content}"
72 | 


--------------------------------------------------------------------------------
/pyproject.toml:
--------------------------------------------------------------------------------
 1 | [project]
 2 | name = "fastmcp"
 3 | dynamic = ["version"]
 4 | description = "A more ergonomic interface for MCP servers"
 5 | authors = [{ name = "Jeremiah Lowin" }]
 6 | dependencies = [
 7 |     "httpx>=0.26.0",
 8 |     "mcp>=1.0.0,<2.0.0",
 9 |     "pydantic-settings>=2.6.1",
10 |     "pydantic>=2.5.3,<3.0.0",
11 |     "typer>=0.9.0",
12 |     "python-dotenv>=1.0.1",
13 | ]
14 | requires-python = ">=3.10"
15 | readme = "README.md"
16 | license = { text = "MIT" }
17 | 
18 | [project.scripts]
19 | fastmcp = "fastmcp.cli:app"
20 | 
21 | [build-system]
22 | requires = ["hatchling>=1.21.0", "hatch-vcs>=0.4.0"]
23 | build-backend = "hatchling.build"
24 | 
25 | [project.optional-dependencies]
26 | tests = [
27 |     "pre-commit",
28 |     "pyright>=1.1.389",
29 |     "pytest>=8.3.3",
30 |     "pytest-asyncio>=0.23.5",
31 |     "pytest-flakefinder",
32 |     "pytest-xdist>=3.6.1",
33 |     "ruff",
34 | ]
35 | dev = ["fastmcp[tests]", "copychat>=0.5.2", "ipython>=8.12.3", "pdbpp>=0.10.3"]
36 | 
37 | [tool.pytest.ini_options]
38 | asyncio_mode = "auto"
39 | asyncio_default_fixture_loop_scope = "session"
40 | 
41 | [tool.hatch.version]
42 | source = "vcs"
43 | 
44 | [tool.pyright]
45 | include = ["src", "tests"]
46 | exclude = ["**/node_modules", "**/__pycache__", ".venv", ".git", "dist"]
47 | pythonVersion = "3.10"
48 | pythonPlatform = "Darwin"
49 | typeCheckingMode = "basic"
50 | reportMissingImports = true
51 | reportMissingTypeStubs = false
52 | useLibraryCodeForTypes = true
53 | venvPath = "."
54 | venv = ".venv"
55 | 


--------------------------------------------------------------------------------
/src/fastmcp/__init__.py:
--------------------------------------------------------------------------------
1 | """FastMCP - A more ergonomic interface for MCP servers."""
2 | 
3 | from importlib.metadata import version
4 | from .server import FastMCP, Context
5 | from .utilities.types import Image
6 | 
7 | __version__ = version("fastmcp")
8 | __all__ = ["FastMCP", "Context", "Image"]
9 | 


--------------------------------------------------------------------------------
/src/fastmcp/cli/__init__.py:
--------------------------------------------------------------------------------
1 | """FastMCP CLI package."""
2 | 
3 | from .cli import app
4 | 
5 | 
6 | if __name__ == "__main__":
7 |     app()
8 | 


--------------------------------------------------------------------------------
/src/fastmcp/cli/claude.py:
--------------------------------------------------------------------------------
  1 | """Claude app integration utilities."""
  2 | 
  3 | import json
  4 | import sys
  5 | from pathlib import Path
  6 | from typing import Optional, Dict
  7 | 
  8 | from ..utilities.logging import get_logger
  9 | 
 10 | logger = get_logger(__name__)
 11 | 
 12 | 
 13 | def get_claude_config_path() -> Path | None:
 14 |     """Get the Claude config directory based on platform."""
 15 |     if sys.platform == "win32":
 16 |         path = Path(Path.home(), "AppData", "Roaming", "Claude")
 17 |     elif sys.platform == "darwin":
 18 |         path = Path(Path.home(), "Library", "Application Support", "Claude")
 19 |     else:
 20 |         return None
 21 | 
 22 |     if path.exists():
 23 |         return path
 24 |     return None
 25 | 
 26 | 
 27 | def update_claude_config(
 28 |     file_spec: str,
 29 |     server_name: str,
 30 |     *,
 31 |     with_editable: Optional[Path] = None,
 32 |     with_packages: Optional[list[str]] = None,
 33 |     env_vars: Optional[Dict[str, str]] = None,
 34 | ) -> bool:
 35 |     """Add or update a FastMCP server in Claude's configuration.
 36 | 
 37 |     Args:
 38 |         file_spec: Path to the server file, optionally with :object suffix
 39 |         server_name: Name for the server in Claude's config
 40 |         with_editable: Optional directory to install in editable mode
 41 |         with_packages: Optional list of additional packages to install
 42 |         env_vars: Optional dictionary of environment variables. These are merged with
 43 |             any existing variables, with new values taking precedence.
 44 | 
 45 |     Raises:
 46 |         RuntimeError: If Claude Desktop's config directory is not found, indicating
 47 |             Claude Desktop may not be installed or properly set up.
 48 |     """
 49 |     config_dir = get_claude_config_path()
 50 |     if not config_dir:
 51 |         raise RuntimeError(
 52 |             "Claude Desktop config directory not found. Please ensure Claude Desktop "
 53 |             "is installed and has been run at least once to initialize its configuration."
 54 |         )
 55 | 
 56 |     config_file = config_dir / "claude_desktop_config.json"
 57 |     if not config_file.exists():
 58 |         try:
 59 |             config_file.write_text("{}")
 60 |         except Exception as e:
 61 |             logger.error(
 62 |                 "Failed to create Claude config file",
 63 |                 extra={
 64 |                     "error": str(e),
 65 |                     "config_file": str(config_file),
 66 |                 },
 67 |             )
 68 |             return False
 69 | 
 70 |     try:
 71 |         config = json.loads(config_file.read_text())
 72 |         if "mcpServers" not in config:
 73 |             config["mcpServers"] = {}
 74 | 
 75 |         # Always preserve existing env vars and merge with new ones
 76 |         if (
 77 |             server_name in config["mcpServers"]
 78 |             and "env" in config["mcpServers"][server_name]
 79 |         ):
 80 |             existing_env = config["mcpServers"][server_name]["env"]
 81 |             if env_vars:
 82 |                 # New vars take precedence over existing ones
 83 |                 env_vars = {**existing_env, **env_vars}
 84 |             else:
 85 |                 env_vars = existing_env
 86 | 
 87 |         # Build uv run command
 88 |         args = ["run"]
 89 | 
 90 |         # Collect all packages in a set to deduplicate
 91 |         packages = {"fastmcp"}
 92 |         if with_packages:
 93 |             packages.update(pkg for pkg in with_packages if pkg)
 94 | 
 95 |         # Add all packages with --with
 96 |         for pkg in sorted(packages):
 97 |             args.extend(["--with", pkg])
 98 | 
 99 |         if with_editable:
100 |             args.extend(["--with-editable", str(with_editable)])
101 | 
102 |         # Convert file path to absolute before adding to command
103 |         # Split off any :object suffix first
104 |         if ":" in file_spec:
105 |             file_path, server_object = file_spec.rsplit(":", 1)
106 |             file_spec = f"{Path(file_path).resolve()}:{server_object}"
107 |         else:
108 |             file_spec = str(Path(file_spec).resolve())
109 | 
110 |         # Add fastmcp run command
111 |         args.extend(["fastmcp", "run", file_spec])
112 | 
113 |         server_config = {
114 |             "command": "uv",
115 |             "args": args,
116 |         }
117 | 
118 |         # Add environment variables if specified
119 |         if env_vars:
120 |             server_config["env"] = env_vars
121 | 
122 |         config["mcpServers"][server_name] = server_config
123 | 
124 |         config_file.write_text(json.dumps(config, indent=2))
125 |         logger.info(
126 |             f"Added server '{server_name}' to Claude config",
127 |             extra={"config_file": str(config_file)},
128 |         )
129 |         return True
130 |     except Exception as e:
131 |         logger.error(
132 |             "Failed to update Claude config",
133 |             extra={
134 |                 "error": str(e),
135 |                 "config_file": str(config_file),
136 |             },
137 |         )
138 |         return False
139 | 


--------------------------------------------------------------------------------
/src/fastmcp/cli/cli.py:
--------------------------------------------------------------------------------
  1 | """FastMCP CLI tools."""
  2 | 
  3 | import importlib.metadata
  4 | import importlib.util
  5 | import os
  6 | import subprocess
  7 | import sys
  8 | from pathlib import Path
  9 | from typing import Dict, Optional, Tuple
 10 | 
 11 | import dotenv
 12 | import typer
 13 | from typing_extensions import Annotated
 14 | 
 15 | from fastmcp.cli import claude
 16 | from fastmcp.utilities.logging import get_logger
 17 | 
 18 | logger = get_logger("cli")
 19 | 
 20 | app = typer.Typer(
 21 |     name="fastmcp",
 22 |     help="FastMCP development tools",
 23 |     add_completion=False,
 24 |     no_args_is_help=True,  # Show help if no args provided
 25 | )
 26 | 
 27 | 
 28 | def _get_npx_command():
 29 |     """Get the correct npx command for the current platform."""
 30 |     if sys.platform == "win32":
 31 |         # Try both npx.cmd and npx.exe on Windows
 32 |         for cmd in ["npx.cmd", "npx.exe", "npx"]:
 33 |             try:
 34 |                 subprocess.run(
 35 |                     [cmd, "--version"], check=True, capture_output=True, shell=True
 36 |                 )
 37 |                 return cmd
 38 |             except subprocess.CalledProcessError:
 39 |                 continue
 40 |         return None
 41 |     return "npx"  # On Unix-like systems, just use npx
 42 | 
 43 | 
 44 | def _parse_env_var(env_var: str) -> Tuple[str, str]:
 45 |     """Parse environment variable string in format KEY=VALUE."""
 46 |     if "=" not in env_var:
 47 |         logger.error(
 48 |             f"Invalid environment variable format: {env_var}. Must be KEY=VALUE"
 49 |         )
 50 |         sys.exit(1)
 51 |     key, value = env_var.split("=", 1)
 52 |     return key.strip(), value.strip()
 53 | 
 54 | 
 55 | def _build_uv_command(
 56 |     file_spec: str,
 57 |     with_editable: Optional[Path] = None,
 58 |     with_packages: Optional[list[str]] = None,
 59 | ) -> list[str]:
 60 |     """Build the uv run command that runs a FastMCP server through fastmcp run."""
 61 |     cmd = ["uv"]
 62 | 
 63 |     cmd.extend(["run", "--with", "fastmcp"])
 64 | 
 65 |     if with_editable:
 66 |         cmd.extend(["--with-editable", str(with_editable)])
 67 | 
 68 |     if with_packages:
 69 |         for pkg in with_packages:
 70 |             if pkg:
 71 |                 cmd.extend(["--with", pkg])
 72 | 
 73 |     # Add fastmcp run command
 74 |     cmd.extend(["fastmcp", "run", file_spec])
 75 |     return cmd
 76 | 
 77 | 
 78 | def _parse_file_path(file_spec: str) -> Tuple[Path, Optional[str]]:
 79 |     """Parse a file path that may include a server object specification.
 80 | 
 81 |     Args:
 82 |         file_spec: Path to file, optionally with :object suffix
 83 | 
 84 |     Returns:
 85 |         Tuple of (file_path, server_object)
 86 |     """
 87 |     # First check if we have a Windows path (e.g., C:\...)
 88 |     has_windows_drive = len(file_spec) > 1 and file_spec[1] == ":"
 89 | 
 90 |     # Split on the last colon, but only if it's not part of the Windows drive letter
 91 |     # and there's actually another colon in the string after the drive letter
 92 |     if ":" in (file_spec[2:] if has_windows_drive else file_spec):
 93 |         file_str, server_object = file_spec.rsplit(":", 1)
 94 |     else:
 95 |         file_str, server_object = file_spec, None
 96 | 
 97 |     # Resolve the file path
 98 |     file_path = Path(file_str).expanduser().resolve()
 99 |     if not file_path.exists():
100 |         logger.error(f"File not found: {file_path}")
101 |         sys.exit(1)
102 |     if not file_path.is_file():
103 |         logger.error(f"Not a file: {file_path}")
104 |         sys.exit(1)
105 | 
106 |     return file_path, server_object
107 | 
108 | 
109 | def _import_server(file: Path, server_object: Optional[str] = None):
110 |     """Import a FastMCP server from a file.
111 | 
112 |     Args:
113 |         file: Path to the file
114 |         server_object: Optional object name in format "module:object" or just "object"
115 | 
116 |     Returns:
117 |         The server object
118 |     """
119 |     # Add parent directory to Python path so imports can be resolved
120 |     file_dir = str(file.parent)
121 |     if file_dir not in sys.path:
122 |         sys.path.insert(0, file_dir)
123 | 
124 |     # Import the module
125 |     spec = importlib.util.spec_from_file_location("server_module", file)
126 |     if not spec or not spec.loader:
127 |         logger.error("Could not load module", extra={"file": str(file)})
128 |         sys.exit(1)
129 | 
130 |     module = importlib.util.module_from_spec(spec)
131 |     spec.loader.exec_module(module)
132 | 
133 |     # If no object specified, try common server names
134 |     if not server_object:
135 |         # Look for the most common server object names
136 |         for name in ["mcp", "server", "app"]:
137 |             if hasattr(module, name):
138 |                 return getattr(module, name)
139 | 
140 |         logger.error(
141 |             f"No server object found in {file}. Please either:\n"
142 |             "1. Use a standard variable name (mcp, server, or app)\n"
143 |             "2. Specify the object name with file:object syntax",
144 |             extra={"file": str(file)},
145 |         )
146 |         sys.exit(1)
147 | 
148 |     # Handle module:object syntax
149 |     if ":" in server_object:
150 |         module_name, object_name = server_object.split(":", 1)
151 |         try:
152 |             server_module = importlib.import_module(module_name)
153 |             server = getattr(server_module, object_name, None)
154 |         except ImportError:
155 |             logger.error(
156 |                 f"Could not import module '{module_name}'",
157 |                 extra={"file": str(file)},
158 |             )
159 |             sys.exit(1)
160 |     else:
161 |         # Just object name
162 |         server = getattr(module, server_object, None)
163 | 
164 |     if server is None:
165 |         logger.error(
166 |             f"Server object '{server_object}' not found",
167 |             extra={"file": str(file)},
168 |         )
169 |         sys.exit(1)
170 | 
171 |     return server
172 | 
173 | 
174 | @app.command()
175 | def version() -> None:
176 |     """Show the FastMCP version."""
177 |     try:
178 |         version = importlib.metadata.version("fastmcp")
179 |         print(f"FastMCP version {version}")
180 |     except importlib.metadata.PackageNotFoundError:
181 |         print("FastMCP version unknown (package not installed)")
182 |         sys.exit(1)
183 | 
184 | 
185 | @app.command()
186 | def dev(
187 |     file_spec: str = typer.Argument(
188 |         ...,
189 |         help="Python file to run, optionally with :object suffix",
190 |     ),
191 |     with_editable: Annotated[
192 |         Optional[Path],
193 |         typer.Option(
194 |             "--with-editable",
195 |             "-e",
196 |             help="Directory containing pyproject.toml to install in editable mode",
197 |             exists=True,
198 |             file_okay=False,
199 |             resolve_path=True,
200 |         ),
201 |     ] = None,
202 |     with_packages: Annotated[
203 |         list[str],
204 |         typer.Option(
205 |             "--with",
206 |             help="Additional packages to install",
207 |         ),
208 |     ] = [],
209 | ) -> None:
210 |     """Run a FastMCP server with the MCP Inspector."""
211 |     file, server_object = _parse_file_path(file_spec)
212 | 
213 |     logger.debug(
214 |         "Starting dev server",
215 |         extra={
216 |             "file": str(file),
217 |             "server_object": server_object,
218 |             "with_editable": str(with_editable) if with_editable else None,
219 |             "with_packages": with_packages,
220 |         },
221 |     )
222 | 
223 |     try:
224 |         # Import server to get dependencies
225 |         server = _import_server(file, server_object)
226 |         if hasattr(server, "dependencies"):
227 |             with_packages = list(set(with_packages + server.dependencies))
228 | 
229 |         uv_cmd = _build_uv_command(file_spec, with_editable, with_packages)
230 | 
231 |         # Get the correct npx command
232 |         npx_cmd = _get_npx_command()
233 |         if not npx_cmd:
234 |             logger.error(
235 |                 "npx not found. Please ensure Node.js and npm are properly installed "
236 |                 "and added to your system PATH."
237 |             )
238 |             sys.exit(1)
239 | 
240 |         # Run the MCP Inspector command with shell=True on Windows
241 |         shell = sys.platform == "win32"
242 |         process = subprocess.run(
243 |             [npx_cmd, "@modelcontextprotocol/inspector"] + uv_cmd,
244 |             check=True,
245 |             shell=shell,
246 |             env=dict(os.environ.items()),  # Convert to list of tuples for env update
247 |         )
248 |         sys.exit(process.returncode)
249 |     except subprocess.CalledProcessError as e:
250 |         logger.error(
251 |             "Dev server failed",
252 |             extra={
253 |                 "file": str(file),
254 |                 "error": str(e),
255 |                 "returncode": e.returncode,
256 |             },
257 |         )
258 |         sys.exit(e.returncode)
259 |     except FileNotFoundError:
260 |         logger.error(
261 |             "npx not found. Please ensure Node.js and npm are properly installed "
262 |             "and added to your system PATH. You may need to restart your terminal "
263 |             "after installation.",
264 |             extra={"file": str(file)},
265 |         )
266 |         sys.exit(1)
267 | 
268 | 
269 | @app.command()
270 | def run(
271 |     file_spec: str = typer.Argument(
272 |         ...,
273 |         help="Python file to run, optionally with :object suffix",
274 |     ),
275 |     transport: Annotated[
276 |         Optional[str],
277 |         typer.Option(
278 |             "--transport",
279 |             "-t",
280 |             help="Transport protocol to use (stdio or sse)",
281 |         ),
282 |     ] = None,
283 | ) -> None:
284 |     """Run a FastMCP server.
285 | 
286 |     The server can be specified in two ways:
287 |     1. Module approach: server.py - runs the module directly, expecting a server.run() call
288 |     2. Import approach: server.py:app - imports and runs the specified server object
289 | 
290 |     Note: This command runs the server directly. You are responsible for ensuring
291 |     all dependencies are available. For dependency management, use fastmcp install
292 |     or fastmcp dev instead.
293 |     """
294 |     file, server_object = _parse_file_path(file_spec)
295 | 
296 |     logger.debug(
297 |         "Running server",
298 |         extra={
299 |             "file": str(file),
300 |             "server_object": server_object,
301 |             "transport": transport,
302 |         },
303 |     )
304 | 
305 |     try:
306 |         # Import and get server object
307 |         server = _import_server(file, server_object)
308 | 
309 |         # Run the server
310 |         kwargs = {}
311 |         if transport:
312 |             kwargs["transport"] = transport
313 | 
314 |         server.run(**kwargs)
315 | 
316 |     except Exception as e:
317 |         logger.error(
318 |             f"Failed to run server: {e}",
319 |             extra={
320 |                 "file": str(file),
321 |                 "error": str(e),
322 |             },
323 |         )
324 |         sys.exit(1)
325 | 
326 | 
327 | @app.command()
328 | def install(
329 |     file_spec: str = typer.Argument(
330 |         ...,
331 |         help="Python file to run, optionally with :object suffix",
332 |     ),
333 |     server_name: Annotated[
334 |         Optional[str],
335 |         typer.Option(
336 |             "--name",
337 |             "-n",
338 |             help="Custom name for the server (defaults to server's name attribute or file name)",
339 |         ),
340 |     ] = None,
341 |     with_editable: Annotated[
342 |         Optional[Path],
343 |         typer.Option(
344 |             "--with-editable",
345 |             "-e",
346 |             help="Directory containing pyproject.toml to install in editable mode",
347 |             exists=True,
348 |             file_okay=False,
349 |             resolve_path=True,
350 |         ),
351 |     ] = None,
352 |     with_packages: Annotated[
353 |         list[str],
354 |         typer.Option(
355 |             "--with",
356 |             help="Additional packages to install",
357 |         ),
358 |     ] = [],
359 |     env_vars: Annotated[
360 |         list[str],
361 |         typer.Option(
362 |             "--env-var",
363 |             "-e",
364 |             help="Environment variables in KEY=VALUE format",
365 |         ),
366 |     ] = [],
367 |     env_file: Annotated[
368 |         Optional[Path],
369 |         typer.Option(
370 |             "--env-file",
371 |             "-f",
372 |             help="Load environment variables from a .env file",
373 |             exists=True,
374 |             file_okay=True,
375 |             dir_okay=False,
376 |             resolve_path=True,
377 |         ),
378 |     ] = None,
379 | ) -> None:
380 |     """Install a FastMCP server in the Claude desktop app.
381 | 
382 |     Environment variables are preserved once added and only updated if new values
383 |     are explicitly provided.
384 |     """
385 |     file, server_object = _parse_file_path(file_spec)
386 | 
387 |     logger.debug(
388 |         "Installing server",
389 |         extra={
390 |             "file": str(file),
391 |             "server_name": server_name,
392 |             "server_object": server_object,
393 |             "with_editable": str(with_editable) if with_editable else None,
394 |             "with_packages": with_packages,
395 |         },
396 |     )
397 | 
398 |     if not claude.get_claude_config_path():
399 |         logger.error("Claude app not found")
400 |         sys.exit(1)
401 | 
402 |     # Try to import server to get its name, but fall back to file name if dependencies missing
403 |     name = server_name
404 |     server = None
405 |     if not name:
406 |         try:
407 |             server = _import_server(file, server_object)
408 |             name = server.name
409 |         except (ImportError, ModuleNotFoundError) as e:
410 |             logger.debug(
411 |                 "Could not import server (likely missing dependencies), using file name",
412 |                 extra={"error": str(e)},
413 |             )
414 |             name = file.stem
415 | 
416 |     # Get server dependencies if available
417 |     server_dependencies = getattr(server, "dependencies", []) if server else []
418 |     if server_dependencies:
419 |         with_packages = list(set(with_packages + server_dependencies))
420 | 
421 |     # Process environment variables if provided
422 |     env_dict: Optional[Dict[str, str]] = None
423 |     if env_file or env_vars:
424 |         env_dict = {}
425 |         # Load from .env file if specified
426 |         if env_file:
427 |             try:
428 |                 env_dict |= {
429 |                     k: v
430 |                     for k, v in dotenv.dotenv_values(env_file).items()
431 |                     if v is not None
432 |                 }
433 |             except Exception as e:
434 |                 logger.error(f"Failed to load .env file: {e}")
435 |                 sys.exit(1)
436 | 
437 |         # Add command line environment variables
438 |         for env_var in env_vars:
439 |             key, value = _parse_env_var(env_var)
440 |             env_dict[key] = value
441 | 
442 |     if claude.update_claude_config(
443 |         file_spec,
444 |         name,
445 |         with_editable=with_editable,
446 |         with_packages=with_packages,
447 |         env_vars=env_dict,
448 |     ):
449 |         logger.info(f"Successfully installed {name} in Claude app")
450 |     else:
451 |         logger.error(f"Failed to install {name} in Claude app")
452 |         sys.exit(1)
453 | 


--------------------------------------------------------------------------------
/src/fastmcp/exceptions.py:
--------------------------------------------------------------------------------
 1 | """Custom exceptions for FastMCP."""
 2 | 
 3 | 
 4 | class FastMCPError(Exception):
 5 |     """Base error for FastMCP."""
 6 | 
 7 | 
 8 | class ValidationError(FastMCPError):
 9 |     """Error in validating parameters or return values."""
10 | 
11 | 
12 | class ResourceError(FastMCPError):
13 |     """Error in resource operations."""
14 | 
15 | 
16 | class ToolError(FastMCPError):
17 |     """Error in tool operations."""
18 | 
19 | 
20 | class InvalidSignature(Exception):
21 |     """Invalid signature for use with FastMCP."""
22 | 


--------------------------------------------------------------------------------
/src/fastmcp/prompts/__init__.py:
--------------------------------------------------------------------------------
1 | from .base import Prompt
2 | from .manager import PromptManager
3 | 
4 | __all__ = ["Prompt", "PromptManager"]
5 | 


--------------------------------------------------------------------------------
/src/fastmcp/prompts/base.py:
--------------------------------------------------------------------------------
  1 | """Base classes for FastMCP prompts."""
  2 | 
  3 | import json
  4 | from typing import Any, Callable, Dict, Literal, Optional, Sequence, Awaitable
  5 | import inspect
  6 | 
  7 | from pydantic import BaseModel, Field, TypeAdapter, validate_call
  8 | from mcp.types import TextContent, ImageContent, EmbeddedResource
  9 | import pydantic_core
 10 | 
 11 | CONTENT_TYPES = TextContent | ImageContent | EmbeddedResource
 12 | 
 13 | 
 14 | class Message(BaseModel):
 15 |     """Base class for all prompt messages."""
 16 | 
 17 |     role: Literal["user", "assistant"]
 18 |     content: CONTENT_TYPES
 19 | 
 20 |     def __init__(self, content: str | CONTENT_TYPES, **kwargs):
 21 |         if isinstance(content, str):
 22 |             content = TextContent(type="text", text=content)
 23 |         super().__init__(content=content, **kwargs)
 24 | 
 25 | 
 26 | class UserMessage(Message):
 27 |     """A message from the user."""
 28 | 
 29 |     role: Literal["user"] = "user"
 30 | 
 31 |     def __init__(self, content: str | CONTENT_TYPES, **kwargs):
 32 |         super().__init__(content=content, **kwargs)
 33 | 
 34 | 
 35 | class AssistantMessage(Message):
 36 |     """A message from the assistant."""
 37 | 
 38 |     role: Literal["assistant"] = "assistant"
 39 | 
 40 |     def __init__(self, content: str | CONTENT_TYPES, **kwargs):
 41 |         super().__init__(content=content, **kwargs)
 42 | 
 43 | 
 44 | message_validator = TypeAdapter(UserMessage | AssistantMessage)
 45 | 
 46 | SyncPromptResult = (
 47 |     str | Message | dict[str, Any] | Sequence[str | Message | dict[str, Any]]
 48 | )
 49 | PromptResult = SyncPromptResult | Awaitable[SyncPromptResult]
 50 | 
 51 | 
 52 | class PromptArgument(BaseModel):
 53 |     """An argument that can be passed to a prompt."""
 54 | 
 55 |     name: str = Field(description="Name of the argument")
 56 |     description: str | None = Field(
 57 |         None, description="Description of what the argument does"
 58 |     )
 59 |     required: bool = Field(
 60 |         default=False, description="Whether the argument is required"
 61 |     )
 62 | 
 63 | 
 64 | class Prompt(BaseModel):
 65 |     """A prompt template that can be rendered with parameters."""
 66 | 
 67 |     name: str = Field(description="Name of the prompt")
 68 |     description: str | None = Field(
 69 |         None, description="Description of what the prompt does"
 70 |     )
 71 |     arguments: list[PromptArgument] | None = Field(
 72 |         None, description="Arguments that can be passed to the prompt"
 73 |     )
 74 |     fn: Callable = Field(exclude=True)
 75 | 
 76 |     @classmethod
 77 |     def from_function(
 78 |         cls,
 79 |         fn: Callable[..., PromptResult],
 80 |         name: Optional[str] = None,
 81 |         description: Optional[str] = None,
 82 |     ) -> "Prompt":
 83 |         """Create a Prompt from a function.
 84 | 
 85 |         The function can return:
 86 |         - A string (converted to a message)
 87 |         - A Message object
 88 |         - A dict (converted to a message)
 89 |         - A sequence of any of the above
 90 |         """
 91 |         func_name = name or fn.__name__
 92 | 
 93 |         if func_name == "<lambda>":
 94 |             raise ValueError("You must provide a name for lambda functions")
 95 | 
 96 |         # Get schema from TypeAdapter - will fail if function isn't properly typed
 97 |         parameters = TypeAdapter(fn).json_schema()
 98 | 
 99 |         # Convert parameters to PromptArguments
100 |         arguments = []
101 |         if "properties" in parameters:
102 |             for param_name, param in parameters["properties"].items():
103 |                 required = param_name in parameters.get("required", [])
104 |                 arguments.append(
105 |                     PromptArgument(
106 |                         name=param_name,
107 |                         description=param.get("description"),
108 |                         required=required,
109 |                     )
110 |                 )
111 | 
112 |         # ensure the arguments are properly cast
113 |         fn = validate_call(fn)
114 | 
115 |         return cls(
116 |             name=func_name,
117 |             description=description or fn.__doc__ or "",
118 |             arguments=arguments,
119 |             fn=fn,
120 |         )
121 | 
122 |     async def render(self, arguments: Optional[Dict[str, Any]] = None) -> list[Message]:
123 |         """Render the prompt with arguments."""
124 |         # Validate required arguments
125 |         if self.arguments:
126 |             required = {arg.name for arg in self.arguments if arg.required}
127 |             provided = set(arguments or {})
128 |             missing = required - provided
129 |             if missing:
130 |                 raise ValueError(f"Missing required arguments: {missing}")
131 | 
132 |         try:
133 |             # Call function and check if result is a coroutine
134 |             result = self.fn(**(arguments or {}))
135 |             if inspect.iscoroutine(result):
136 |                 result = await result
137 | 
138 |             # Validate messages
139 |             if not isinstance(result, (list, tuple)):
140 |                 result = [result]
141 | 
142 |             # Convert result to messages
143 |             messages = []
144 |             for msg in result:
145 |                 try:
146 |                     if isinstance(msg, Message):
147 |                         messages.append(msg)
148 |                     elif isinstance(msg, dict):
149 |                         msg = message_validator.validate_python(msg)
150 |                         messages.append(msg)
151 |                     elif isinstance(msg, str):
152 |                         messages.append(
153 |                             UserMessage(content=TextContent(type="text", text=msg))
154 |                         )
155 |                     else:
156 |                         msg = json.dumps(pydantic_core.to_jsonable_python(msg))
157 |                         messages.append(Message(role="user", content=msg))
158 |                 except Exception:
159 |                     raise ValueError(
160 |                         f"Could not convert prompt result to message: {msg}"
161 |                     )
162 | 
163 |             return messages
164 |         except Exception as e:
165 |             raise ValueError(f"Error rendering prompt {self.name}: {e}")
166 | 


--------------------------------------------------------------------------------
/src/fastmcp/prompts/manager.py:
--------------------------------------------------------------------------------
 1 | """Prompt management functionality."""
 2 | 
 3 | from typing import Any, Dict, Optional
 4 | 
 5 | from fastmcp.prompts.base import Message, Prompt
 6 | from fastmcp.utilities.logging import get_logger
 7 | 
 8 | logger = get_logger(__name__)
 9 | 
10 | 
11 | class PromptManager:
12 |     """Manages FastMCP prompts."""
13 | 
14 |     def __init__(self, warn_on_duplicate_prompts: bool = True):
15 |         self._prompts: Dict[str, Prompt] = {}
16 |         self.warn_on_duplicate_prompts = warn_on_duplicate_prompts
17 | 
18 |     def get_prompt(self, name: str) -> Optional[Prompt]:
19 |         """Get prompt by name."""
20 |         return self._prompts.get(name)
21 | 
22 |     def list_prompts(self) -> list[Prompt]:
23 |         """List all registered prompts."""
24 |         return list(self._prompts.values())
25 | 
26 |     def add_prompt(
27 |         self,
28 |         prompt: Prompt,
29 |     ) -> Prompt:
30 |         """Add a prompt to the manager."""
31 | 
32 |         # Check for duplicates
33 |         existing = self._prompts.get(prompt.name)
34 |         if existing:
35 |             if self.warn_on_duplicate_prompts:
36 |                 logger.warning(f"Prompt already exists: {prompt.name}")
37 |             return existing
38 | 
39 |         self._prompts[prompt.name] = prompt
40 |         return prompt
41 | 
42 |     async def render_prompt(
43 |         self, name: str, arguments: Optional[Dict[str, Any]] = None
44 |     ) -> list[Message]:
45 |         """Render a prompt by name with arguments."""
46 |         prompt = self.get_prompt(name)
47 |         if not prompt:
48 |             raise ValueError(f"Unknown prompt: {name}")
49 | 
50 |         return await prompt.render(arguments)
51 | 


--------------------------------------------------------------------------------
/src/fastmcp/prompts/prompt_manager.py:
--------------------------------------------------------------------------------
 1 | """Prompt management functionality."""
 2 | 
 3 | from typing import Dict, Optional
 4 | 
 5 | 
 6 | from fastmcp.prompts.base import Prompt
 7 | from fastmcp.utilities.logging import get_logger
 8 | 
 9 | logger = get_logger(__name__)
10 | 
11 | 
12 | class PromptManager:
13 |     """Manages FastMCP prompts."""
14 | 
15 |     def __init__(self, warn_on_duplicate_prompts: bool = True):
16 |         self._prompts: Dict[str, Prompt] = {}
17 |         self.warn_on_duplicate_prompts = warn_on_duplicate_prompts
18 | 
19 |     def add_prompt(self, prompt: Prompt) -> Prompt:
20 |         """Add a prompt to the manager."""
21 |         logger.debug(f"Adding prompt: {prompt.name}")
22 |         existing = self._prompts.get(prompt.name)
23 |         if existing:
24 |             if self.warn_on_duplicate_prompts:
25 |                 logger.warning(f"Prompt already exists: {prompt.name}")
26 |             return existing
27 |         self._prompts[prompt.name] = prompt
28 |         return prompt
29 | 
30 |     def get_prompt(self, name: str) -> Optional[Prompt]:
31 |         """Get prompt by name."""
32 |         return self._prompts.get(name)
33 | 
34 |     def list_prompts(self) -> list[Prompt]:
35 |         """List all registered prompts."""
36 |         return list(self._prompts.values())
37 | 


--------------------------------------------------------------------------------
/src/fastmcp/py.typed:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/jlowin/fastmcp/80c328b3dc0b949f010456ee0e85cc5c90e3305f/src/fastmcp/py.typed


--------------------------------------------------------------------------------
/src/fastmcp/resources/__init__.py:
--------------------------------------------------------------------------------
 1 | from .base import Resource
 2 | from .types import (
 3 |     TextResource,
 4 |     BinaryResource,
 5 |     FunctionResource,
 6 |     FileResource,
 7 |     HttpResource,
 8 |     DirectoryResource,
 9 | )
10 | from .templates import ResourceTemplate
11 | from .resource_manager import ResourceManager
12 | 
13 | __all__ = [
14 |     "Resource",
15 |     "TextResource",
16 |     "BinaryResource",
17 |     "FunctionResource",
18 |     "FileResource",
19 |     "HttpResource",
20 |     "DirectoryResource",
21 |     "ResourceTemplate",
22 |     "ResourceManager",
23 | ]
24 | 


--------------------------------------------------------------------------------
/src/fastmcp/resources/base.py:
--------------------------------------------------------------------------------
 1 | """Base classes and interfaces for FastMCP resources."""
 2 | 
 3 | import abc
 4 | from typing import Union, Annotated
 5 | 
 6 | from pydantic import (
 7 |     AnyUrl,
 8 |     BaseModel,
 9 |     ConfigDict,
10 |     Field,
11 |     UrlConstraints,
12 |     ValidationInfo,
13 |     field_validator,
14 | )
15 | 
16 | 
17 | class Resource(BaseModel, abc.ABC):
18 |     """Base class for all resources."""
19 | 
20 |     model_config = ConfigDict(validate_default=True)
21 | 
22 |     uri: Annotated[AnyUrl, UrlConstraints(host_required=False)] = Field(
23 |         default=..., description="URI of the resource"
24 |     )
25 |     name: str | None = Field(description="Name of the resource", default=None)
26 |     description: str | None = Field(
27 |         description="Description of the resource", default=None
28 |     )
29 |     mime_type: str = Field(
30 |         default="text/plain",
31 |         description="MIME type of the resource content",
32 |         pattern=r"^[a-zA-Z0-9]+/[a-zA-Z0-9\-+.]+$",
33 |     )
34 | 
35 |     @field_validator("name", mode="before")
36 |     @classmethod
37 |     def set_default_name(cls, name: str | None, info: ValidationInfo) -> str:
38 |         """Set default name from URI if not provided."""
39 |         if name:
40 |             return name
41 |         if uri := info.data.get("uri"):
42 |             return str(uri)
43 |         raise ValueError("Either name or uri must be provided")
44 | 
45 |     @abc.abstractmethod
46 |     async def read(self) -> Union[str, bytes]:
47 |         """Read the resource content."""
48 |         pass
49 | 


--------------------------------------------------------------------------------
/src/fastmcp/resources/resource_manager.py:
--------------------------------------------------------------------------------
 1 | """Resource manager functionality."""
 2 | 
 3 | from typing import Callable, Dict, Optional, Union
 4 | 
 5 | from pydantic import AnyUrl
 6 | 
 7 | from fastmcp.resources.base import Resource
 8 | from fastmcp.resources.templates import ResourceTemplate
 9 | from fastmcp.utilities.logging import get_logger
10 | 
11 | logger = get_logger(__name__)
12 | 
13 | 
14 | class ResourceManager:
15 |     """Manages FastMCP resources."""
16 | 
17 |     def __init__(self, warn_on_duplicate_resources: bool = True):
18 |         self._resources: Dict[str, Resource] = {}
19 |         self._templates: Dict[str, ResourceTemplate] = {}
20 |         self.warn_on_duplicate_resources = warn_on_duplicate_resources
21 | 
22 |     def add_resource(self, resource: Resource) -> Resource:
23 |         """Add a resource to the manager.
24 | 
25 |         Args:
26 |             resource: A Resource instance to add
27 | 
28 |         Returns:
29 |             The added resource. If a resource with the same URI already exists,
30 |             returns the existing resource.
31 |         """
32 |         logger.debug(
33 |             "Adding resource",
34 |             extra={
35 |                 "uri": resource.uri,
36 |                 "type": type(resource).__name__,
37 |                 "name": resource.name,
38 |             },
39 |         )
40 |         existing = self._resources.get(str(resource.uri))
41 |         if existing:
42 |             if self.warn_on_duplicate_resources:
43 |                 logger.warning(f"Resource already exists: {resource.uri}")
44 |             return existing
45 |         self._resources[str(resource.uri)] = resource
46 |         return resource
47 | 
48 |     def add_template(
49 |         self,
50 |         fn: Callable,
51 |         uri_template: str,
52 |         name: Optional[str] = None,
53 |         description: Optional[str] = None,
54 |         mime_type: Optional[str] = None,
55 |     ) -> ResourceTemplate:
56 |         """Add a template from a function."""
57 |         template = ResourceTemplate.from_function(
58 |             fn,
59 |             uri_template=uri_template,
60 |             name=name,
61 |             description=description,
62 |             mime_type=mime_type,
63 |         )
64 |         self._templates[template.uri_template] = template
65 |         return template
66 | 
67 |     async def get_resource(self, uri: Union[AnyUrl, str]) -> Optional[Resource]:
68 |         """Get resource by URI, checking concrete resources first, then templates."""
69 |         uri_str = str(uri)
70 |         logger.debug("Getting resource", extra={"uri": uri_str})
71 | 
72 |         # First check concrete resources
73 |         if resource := self._resources.get(uri_str):
74 |             return resource
75 | 
76 |         # Then check templates
77 |         for template in self._templates.values():
78 |             if params := template.matches(uri_str):
79 |                 try:
80 |                     return await template.create_resource(uri_str, params)
81 |                 except Exception as e:
82 |                     raise ValueError(f"Error creating resource from template: {e}")
83 | 
84 |         raise ValueError(f"Unknown resource: {uri}")
85 | 
86 |     def list_resources(self) -> list[Resource]:
87 |         """List all registered resources."""
88 |         logger.debug("Listing resources", extra={"count": len(self._resources)})
89 |         return list(self._resources.values())
90 | 
91 |     def list_templates(self) -> list[ResourceTemplate]:
92 |         """List all registered templates."""
93 |         logger.debug("Listing templates", extra={"count": len(self._templates)})
94 |         return list(self._templates.values())
95 | 


--------------------------------------------------------------------------------
/src/fastmcp/resources/templates.py:
--------------------------------------------------------------------------------
 1 | """Resource template functionality."""
 2 | 
 3 | import inspect
 4 | import re
 5 | from typing import Any, Callable, Dict, Optional
 6 | 
 7 | from pydantic import BaseModel, Field, TypeAdapter, validate_call
 8 | 
 9 | from fastmcp.resources.types import FunctionResource, Resource
10 | 
11 | 
12 | class ResourceTemplate(BaseModel):
13 |     """A template for dynamically creating resources."""
14 | 
15 |     uri_template: str = Field(
16 |         description="URI template with parameters (e.g. weather://{city}/current)"
17 |     )
18 |     name: str = Field(description="Name of the resource")
19 |     description: str | None = Field(description="Description of what the resource does")
20 |     mime_type: str = Field(
21 |         default="text/plain", description="MIME type of the resource content"
22 |     )
23 |     fn: Callable = Field(exclude=True)
24 |     parameters: dict = Field(description="JSON schema for function parameters")
25 | 
26 |     @classmethod
27 |     def from_function(
28 |         cls,
29 |         fn: Callable,
30 |         uri_template: str,
31 |         name: Optional[str] = None,
32 |         description: Optional[str] = None,
33 |         mime_type: Optional[str] = None,
34 |     ) -> "ResourceTemplate":
35 |         """Create a template from a function."""
36 |         func_name = name or fn.__name__
37 |         if func_name == "<lambda>":
38 |             raise ValueError("You must provide a name for lambda functions")
39 | 
40 |         # Get schema from TypeAdapter - will fail if function isn't properly typed
41 |         parameters = TypeAdapter(fn).json_schema()
42 | 
43 |         # ensure the arguments are properly cast
44 |         fn = validate_call(fn)
45 | 
46 |         return cls(
47 |             uri_template=uri_template,
48 |             name=func_name,
49 |             description=description or fn.__doc__ or "",
50 |             mime_type=mime_type or "text/plain",
51 |             fn=fn,
52 |             parameters=parameters,
53 |         )
54 | 
55 |     def matches(self, uri: str) -> Optional[Dict[str, Any]]:
56 |         """Check if URI matches template and extract parameters."""
57 |         # Convert template to regex pattern
58 |         pattern = self.uri_template.replace("{", "(?P<").replace("}", ">[^/]+)")
59 |         match = re.match(f"^{pattern}$", uri)
60 |         if match:
61 |             return match.groupdict()
62 |         return None
63 | 
64 |     async def create_resource(self, uri: str, params: Dict[str, Any]) -> Resource:
65 |         """Create a resource from the template with the given parameters."""
66 |         try:
67 |             # Call function and check if result is a coroutine
68 |             result = self.fn(**params)
69 |             if inspect.iscoroutine(result):
70 |                 result = await result
71 | 
72 |             return FunctionResource(
73 |                 uri=uri,  # type: ignore
74 |                 name=self.name,
75 |                 description=self.description,
76 |                 mime_type=self.mime_type,
77 |                 fn=lambda: result,  # Capture result in closure
78 |             )
79 |         except Exception as e:
80 |             raise ValueError(f"Error creating resource from template: {e}")
81 | 


--------------------------------------------------------------------------------
/src/fastmcp/resources/types.py:
--------------------------------------------------------------------------------
  1 | """Concrete resource implementations."""
  2 | 
  3 | import asyncio
  4 | import json
  5 | from pathlib import Path
  6 | from typing import Any, Callable, Union
  7 | 
  8 | import httpx
  9 | import pydantic.json
 10 | import pydantic_core
 11 | from pydantic import Field, ValidationInfo
 12 | 
 13 | from fastmcp.resources.base import Resource
 14 | 
 15 | 
 16 | class TextResource(Resource):
 17 |     """A resource that reads from a string."""
 18 | 
 19 |     text: str = Field(description="Text content of the resource")
 20 | 
 21 |     async def read(self) -> str:
 22 |         """Read the text content."""
 23 |         return self.text
 24 | 
 25 | 
 26 | class BinaryResource(Resource):
 27 |     """A resource that reads from bytes."""
 28 | 
 29 |     data: bytes = Field(description="Binary content of the resource")
 30 | 
 31 |     async def read(self) -> bytes:
 32 |         """Read the binary content."""
 33 |         return self.data
 34 | 
 35 | 
 36 | class FunctionResource(Resource):
 37 |     """A resource that defers data loading by wrapping a function.
 38 | 
 39 |     The function is only called when the resource is read, allowing for lazy loading
 40 |     of potentially expensive data. This is particularly useful when listing resources,
 41 |     as the function won't be called until the resource is actually accessed.
 42 | 
 43 |     The function can return:
 44 |     - str for text content (default)
 45 |     - bytes for binary content
 46 |     - other types will be converted to JSON
 47 |     """
 48 | 
 49 |     fn: Callable[[], Any] = Field(exclude=True)
 50 | 
 51 |     async def read(self) -> Union[str, bytes]:
 52 |         """Read the resource by calling the wrapped function."""
 53 |         try:
 54 |             result = self.fn()
 55 |             if isinstance(result, Resource):
 56 |                 return await result.read()
 57 |             if isinstance(result, bytes):
 58 |                 return result
 59 |             if isinstance(result, str):
 60 |                 return result
 61 |             try:
 62 |                 return json.dumps(pydantic_core.to_jsonable_python(result))
 63 |             except (TypeError, pydantic_core.PydanticSerializationError):
 64 |                 # If JSON serialization fails, try str()
 65 |                 return str(result)
 66 |         except Exception as e:
 67 |             raise ValueError(f"Error reading resource {self.uri}: {e}")
 68 | 
 69 | 
 70 | class FileResource(Resource):
 71 |     """A resource that reads from a file.
 72 | 
 73 |     Set is_binary=True to read file as binary data instead of text.
 74 |     """
 75 | 
 76 |     path: Path = Field(description="Path to the file")
 77 |     is_binary: bool = Field(
 78 |         default=False,
 79 |         description="Whether to read the file as binary data",
 80 |     )
 81 |     mime_type: str = Field(
 82 |         default="text/plain",
 83 |         description="MIME type of the resource content",
 84 |     )
 85 | 
 86 |     @pydantic.field_validator("path")
 87 |     @classmethod
 88 |     def validate_absolute_path(cls, path: Path) -> Path:
 89 |         """Ensure path is absolute."""
 90 |         if not path.is_absolute():
 91 |             raise ValueError("Path must be absolute")
 92 |         return path
 93 | 
 94 |     @pydantic.field_validator("is_binary")
 95 |     @classmethod
 96 |     def set_binary_from_mime_type(cls, is_binary: bool, info: ValidationInfo) -> bool:
 97 |         """Set is_binary based on mime_type if not explicitly set."""
 98 |         if is_binary:
 99 |             return True
100 |         mime_type = info.data.get("mime_type", "text/plain")
101 |         return not mime_type.startswith("text/")
102 | 
103 |     async def read(self) -> Union[str, bytes]:
104 |         """Read the file content."""
105 |         try:
106 |             if self.is_binary:
107 |                 return await asyncio.to_thread(self.path.read_bytes)
108 |             return await asyncio.to_thread(self.path.read_text)
109 |         except Exception as e:
110 |             raise ValueError(f"Error reading file {self.path}: {e}")
111 | 
112 | 
113 | class HttpResource(Resource):
114 |     """A resource that reads from an HTTP endpoint."""
115 | 
116 |     url: str = Field(description="URL to fetch content from")
117 |     mime_type: str | None = Field(
118 |         default="application/json", description="MIME type of the resource content"
119 |     )
120 | 
121 |     async def read(self) -> Union[str, bytes]:
122 |         """Read the HTTP content."""
123 |         async with httpx.AsyncClient() as client:
124 |             response = await client.get(self.url)
125 |             response.raise_for_status()
126 |             return response.text
127 | 
128 | 
129 | class DirectoryResource(Resource):
130 |     """A resource that lists files in a directory."""
131 | 
132 |     path: Path = Field(description="Path to the directory")
133 |     recursive: bool = Field(
134 |         default=False, description="Whether to list files recursively"
135 |     )
136 |     pattern: str | None = Field(
137 |         default=None, description="Optional glob pattern to filter files"
138 |     )
139 |     mime_type: str | None = Field(
140 |         default="application/json", description="MIME type of the resource content"
141 |     )
142 | 
143 |     @pydantic.field_validator("path")
144 |     @classmethod
145 |     def validate_absolute_path(cls, path: Path) -> Path:
146 |         """Ensure path is absolute."""
147 |         if not path.is_absolute():
148 |             raise ValueError("Path must be absolute")
149 |         return path
150 | 
151 |     def list_files(self) -> list[Path]:
152 |         """List files in the directory."""
153 |         if not self.path.exists():
154 |             raise FileNotFoundError(f"Directory not found: {self.path}")
155 |         if not self.path.is_dir():
156 |             raise NotADirectoryError(f"Not a directory: {self.path}")
157 | 
158 |         try:
159 |             if self.pattern:
160 |                 return (
161 |                     list(self.path.glob(self.pattern))
162 |                     if not self.recursive
163 |                     else list(self.path.rglob(self.pattern))
164 |                 )
165 |             return (
166 |                 list(self.path.glob("*"))
167 |                 if not self.recursive
168 |                 else list(self.path.rglob("*"))
169 |             )
170 |         except Exception as e:
171 |             raise ValueError(f"Error listing directory {self.path}: {e}")
172 | 
173 |     async def read(self) -> str:  # Always returns JSON string
174 |         """Read the directory listing."""
175 |         try:
176 |             files = await asyncio.to_thread(self.list_files)
177 |             file_list = [str(f.relative_to(self.path)) for f in files if f.is_file()]
178 |             return json.dumps({"files": file_list}, indent=2)
179 |         except Exception as e:
180 |             raise ValueError(f"Error reading directory {self.path}: {e}")
181 | 


--------------------------------------------------------------------------------
/src/fastmcp/server.py:
--------------------------------------------------------------------------------
  1 | """FastMCP - A more ergonomic interface for MCP servers."""
  2 | 
  3 | import asyncio
  4 | import functools
  5 | import inspect
  6 | import json
  7 | import re
  8 | from itertools import chain
  9 | from typing import Any, Callable, Dict, Literal, Sequence, TypeVar, ParamSpec
 10 | 
 11 | import pydantic_core
 12 | from pydantic import Field
 13 | import uvicorn
 14 | from mcp.server import Server as MCPServer
 15 | from mcp.server.sse import SseServerTransport
 16 | from mcp.server.stdio import stdio_server
 17 | from mcp.shared.context import RequestContext
 18 | from mcp.types import (
 19 |     EmbeddedResource,
 20 |     GetPromptResult,
 21 |     ImageContent,
 22 |     TextContent,
 23 | )
 24 | from mcp.types import (
 25 |     Prompt as MCPPrompt,
 26 |     PromptArgument as MCPPromptArgument,
 27 | )
 28 | from mcp.types import (
 29 |     Resource as MCPResource,
 30 | )
 31 | from mcp.types import (
 32 |     ResourceTemplate as MCPResourceTemplate,
 33 | )
 34 | from mcp.types import (
 35 |     Tool as MCPTool,
 36 | )
 37 | from pydantic import BaseModel
 38 | from pydantic.networks import AnyUrl
 39 | from pydantic_settings import BaseSettings, SettingsConfigDict
 40 | 
 41 | from fastmcp.exceptions import ResourceError
 42 | from fastmcp.prompts import Prompt, PromptManager
 43 | from fastmcp.prompts.base import PromptResult
 44 | from fastmcp.resources import FunctionResource, Resource, ResourceManager
 45 | from fastmcp.tools import ToolManager
 46 | from fastmcp.utilities.logging import configure_logging, get_logger
 47 | from fastmcp.utilities.types import Image
 48 | 
 49 | logger = get_logger(__name__)
 50 | 
 51 | P = ParamSpec("P")
 52 | R = TypeVar("R")
 53 | R_PromptResult = TypeVar("R_PromptResult", bound=PromptResult)
 54 | 
 55 | 
 56 | class Settings(BaseSettings):
 57 |     """FastMCP server settings.
 58 | 
 59 |     All settings can be configured via environment variables with the prefix FASTMCP_.
 60 |     For example, FASTMCP_DEBUG=true will set debug=True.
 61 |     """
 62 | 
 63 |     model_config: SettingsConfigDict = SettingsConfigDict(
 64 |         env_prefix="FASTMCP_",
 65 |         env_file=".env",
 66 |         extra="ignore",
 67 |     )
 68 | 
 69 |     # Server settings
 70 |     debug: bool = False
 71 |     log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
 72 | 
 73 |     # HTTP settings
 74 |     host: str = "0.0.0.0"
 75 |     port: int = 8000
 76 | 
 77 |     # resource settings
 78 |     warn_on_duplicate_resources: bool = True
 79 | 
 80 |     # tool settings
 81 |     warn_on_duplicate_tools: bool = True
 82 | 
 83 |     # prompt settings
 84 |     warn_on_duplicate_prompts: bool = True
 85 | 
 86 |     dependencies: list[str] = Field(
 87 |         default_factory=list,
 88 |         description="List of dependencies to install in the server environment",
 89 |     )
 90 | 
 91 | 
 92 | class FastMCP:
 93 |     def __init__(self, name: str | None = None, **settings: Any):
 94 |         self.settings = Settings(**settings)
 95 |         self._mcp_server = MCPServer(name=name or "FastMCP")
 96 |         self._tool_manager = ToolManager(
 97 |             warn_on_duplicate_tools=self.settings.warn_on_duplicate_tools
 98 |         )
 99 |         self._resource_manager = ResourceManager(
100 |             warn_on_duplicate_resources=self.settings.warn_on_duplicate_resources
101 |         )
102 |         self._prompt_manager = PromptManager(
103 |             warn_on_duplicate_prompts=self.settings.warn_on_duplicate_prompts
104 |         )
105 |         self.dependencies = self.settings.dependencies
106 | 
107 |         # Set up MCP protocol handlers
108 |         self._setup_handlers()
109 | 
110 |         # Configure logging
111 |         configure_logging(self.settings.log_level)
112 | 
113 |     @property
114 |     def name(self) -> str:
115 |         return self._mcp_server.name
116 | 
117 |     def run(self, transport: Literal["stdio", "sse"] = "stdio") -> None:
118 |         """Run the FastMCP server. Note this is a synchronous function.
119 | 
120 |         Args:
121 |             transport: Transport protocol to use ("stdio" or "sse")
122 |         """
123 |         TRANSPORTS = Literal["stdio", "sse"]
124 |         if transport not in TRANSPORTS.__args__:  # type: ignore
125 |             raise ValueError(f"Unknown transport: {transport}")
126 | 
127 |         if transport == "stdio":
128 |             asyncio.run(self.run_stdio_async())
129 |         else:  # transport == "sse"
130 |             asyncio.run(self.run_sse_async())
131 | 
132 |     def _setup_handlers(self) -> None:
133 |         """Set up core MCP protocol handlers."""
134 |         self._mcp_server.list_tools()(self.list_tools)
135 |         self._mcp_server.call_tool()(self.call_tool)
136 |         self._mcp_server.list_resources()(self.list_resources)
137 |         self._mcp_server.read_resource()(self.read_resource)
138 |         self._mcp_server.list_prompts()(self.list_prompts)
139 |         self._mcp_server.get_prompt()(self.get_prompt)
140 |         # TODO: This has not been added to MCP yet, see https://github.com/jlowin/fastmcp/issues/10
141 |         # self._mcp_server.list_resource_templates()(self.list_resource_templates)
142 | 
143 |     async def list_tools(self) -> list[MCPTool]:
144 |         """List all available tools."""
145 |         tools = self._tool_manager.list_tools()
146 |         return [
147 |             MCPTool(
148 |                 name=info.name,
149 |                 description=info.description,
150 |                 inputSchema=info.parameters,
151 |             )
152 |             for info in tools
153 |         ]
154 | 
155 |     def get_context(self) -> "Context":
156 |         """
157 |         Returns a Context object. Note that the context will only be valid
158 |         during a request; outside a request, most methods will error.
159 |         """
160 |         try:
161 |             request_context = self._mcp_server.request_context
162 |         except LookupError:
163 |             request_context = None
164 |         return Context(request_context=request_context, fastmcp=self)
165 | 
166 |     async def call_tool(
167 |         self, name: str, arguments: dict
168 |     ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
169 |         """Call a tool by name with arguments."""
170 |         context = self.get_context()
171 |         result = await self._tool_manager.call_tool(name, arguments, context=context)
172 |         converted_result = _convert_to_content(result)
173 |         return converted_result
174 | 
175 |     async def list_resources(self) -> list[MCPResource]:
176 |         """List all available resources."""
177 | 
178 |         resources = self._resource_manager.list_resources()
179 |         return [
180 |             MCPResource(
181 |                 uri=resource.uri,
182 |                 name=resource.name or "",
183 |                 description=resource.description,
184 |                 mimeType=resource.mime_type,
185 |             )
186 |             for resource in resources
187 |         ]
188 | 
189 |     async def list_resource_templates(self) -> list[MCPResourceTemplate]:
190 |         templates = self._resource_manager.list_templates()
191 |         return [
192 |             MCPResourceTemplate(
193 |                 uriTemplate=template.uri_template,
194 |                 name=template.name,
195 |                 description=template.description,
196 |             )
197 |             for template in templates
198 |         ]
199 | 
200 |     async def read_resource(self, uri: AnyUrl | str) -> str | bytes:
201 |         """Read a resource by URI."""
202 |         resource = await self._resource_manager.get_resource(uri)
203 |         if not resource:
204 |             raise ResourceError(f"Unknown resource: {uri}")
205 | 
206 |         try:
207 |             return await resource.read()
208 |         except Exception as e:
209 |             logger.error(f"Error reading resource {uri}: {e}")
210 |             raise ResourceError(str(e))
211 | 
212 |     def add_tool(
213 |         self,
214 |         fn: Callable,
215 |         name: str | None = None,
216 |         description: str | None = None,
217 |     ) -> None:
218 |         """Add a tool to the server.
219 | 
220 |         The tool function can optionally request a Context object by adding a parameter
221 |         with the Context type annotation. See the @tool decorator for examples.
222 | 
223 |         Args:
224 |             fn: The function to register as a tool
225 |             name: Optional name for the tool (defaults to function name)
226 |             description: Optional description of what the tool does
227 |         """
228 |         self._tool_manager.add_tool(fn, name=name, description=description)
229 | 
230 |     def tool(
231 |         self, name: str | None = None, description: str | None = None
232 |     ) -> Callable[[Callable[P, R]], Callable[P, R]]:
233 |         """Decorator to register a tool.
234 | 
235 |         Tools can optionally request a Context object by adding a parameter with the Context type annotation.
236 |         The context provides access to MCP capabilities like logging, progress reporting, and resource access.
237 | 
238 |         Args:
239 |             name: Optional name for the tool (defaults to function name)
240 |             description: Optional description of what the tool does
241 | 
242 |         Example:
243 |             @server.tool()
244 |             def my_tool(x: int) -> str:
245 |                 return str(x)
246 | 
247 |             @server.tool()
248 |             def tool_with_context(x: int, ctx: Context) -> str:
249 |                 ctx.info(f"Processing {x}")
250 |                 return str(x)
251 | 
252 |             @server.tool()
253 |             async def async_tool(x: int, context: Context) -> str:
254 |                 await context.report_progress(50, 100)
255 |                 return str(x)
256 |         """
257 |         # Check if user passed function directly instead of calling decorator
258 |         if callable(name):
259 |             raise TypeError(
260 |                 "The @tool decorator was used incorrectly. "
261 |                 "Did you forget to call it? Use @tool() instead of @tool"
262 |             )
263 | 
264 |         def decorator(fn: Callable[P, R]) -> Callable[P, R]:
265 |             self.add_tool(fn, name=name, description=description)
266 |             return fn
267 | 
268 |         return decorator
269 | 
270 |     def add_resource(self, resource: Resource) -> None:
271 |         """Add a resource to the server.
272 | 
273 |         Args:
274 |             resource: A Resource instance to add
275 |         """
276 |         self._resource_manager.add_resource(resource)
277 | 
278 |     def resource(
279 |         self,
280 |         uri: str,
281 |         *,
282 |         name: str | None = None,
283 |         description: str | None = None,
284 |         mime_type: str | None = None,
285 |     ) -> Callable[[Callable[P, R]], Callable[P, R]]:
286 |         """Decorator to register a function as a resource.
287 | 
288 |         The function will be called when the resource is read to generate its content.
289 |         The function can return:
290 |         - str for text content
291 |         - bytes for binary content
292 |         - other types will be converted to JSON
293 | 
294 |         If the URI contains parameters (e.g. "resource://{param}") or the function
295 |         has parameters, it will be registered as a template resource.
296 | 
297 |         Args:
298 |             uri: URI for the resource (e.g. "resource://my-resource" or "resource://{param}")
299 |             name: Optional name for the resource
300 |             description: Optional description of the resource
301 |             mime_type: Optional MIME type for the resource
302 | 
303 |         Example:
304 |             @server.resource("resource://my-resource")
305 |             def get_data() -> str:
306 |                 return "Hello, world!"
307 | 
308 |             @server.resource("resource://{city}/weather")
309 |             def get_weather(city: str) -> str:
310 |                 return f"Weather for {city}"
311 |         """
312 |         # Check if user passed function directly instead of calling decorator
313 |         if callable(uri):
314 |             raise TypeError(
315 |                 "The @resource decorator was used incorrectly. "
316 |                 "Did you forget to call it? Use @resource('uri') instead of @resource"
317 |             )
318 | 
319 |         def decorator(fn: Callable[P, R]) -> Callable[P, R]:
320 |             @functools.wraps(fn)
321 |             def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
322 |                 return fn(*args, **kwargs)
323 | 
324 |             # Check if this should be a template
325 |             has_uri_params = "{" in uri and "}" in uri
326 |             has_func_params = bool(inspect.signature(fn).parameters)
327 | 
328 |             if has_uri_params or has_func_params:
329 |                 # Validate that URI params match function params
330 |                 uri_params = set(re.findall(r"{(\w+)}", uri))
331 |                 func_params = set(inspect.signature(fn).parameters.keys())
332 | 
333 |                 if uri_params != func_params:
334 |                     raise ValueError(
335 |                         f"Mismatch between URI parameters {uri_params} "
336 |                         f"and function parameters {func_params}"
337 |                     )
338 | 
339 |                 # Register as template
340 |                 self._resource_manager.add_template(
341 |                     wrapper,
342 |                     uri_template=uri,
343 |                     name=name,
344 |                     description=description,
345 |                     mime_type=mime_type or "text/plain",
346 |                 )
347 |             else:
348 |                 # Register as regular resource
349 |                 resource = FunctionResource(
350 |                     uri=AnyUrl(uri),
351 |                     name=name,
352 |                     description=description,
353 |                     mime_type=mime_type or "text/plain",
354 |                     fn=wrapper,
355 |                 )
356 |                 self.add_resource(resource)
357 |             return wrapper
358 | 
359 |         return decorator
360 | 
361 |     def add_prompt(self, prompt: Prompt) -> None:
362 |         """Add a prompt to the server.
363 | 
364 |         Args:
365 |             prompt: A Prompt instance to add
366 |         """
367 |         self._prompt_manager.add_prompt(prompt)
368 | 
369 |     def prompt(
370 |         self, name: str | None = None, description: str | None = None
371 |     ) -> Callable[[Callable[P, R_PromptResult]], Callable[P, R_PromptResult]]:
372 |         """Decorator to register a prompt.
373 | 
374 |         Args:
375 |             name: Optional name for the prompt (defaults to function name)
376 |             description: Optional description of what the prompt does
377 | 
378 |         Example:
379 |             @server.prompt()
380 |             def analyze_table(table_name: str) -> list[Message]:
381 |                 schema = read_table_schema(table_name)
382 |                 return [
383 |                     {
384 |                         "role": "user",
385 |                         "content": f"Analyze this schema:\n{schema}"
386 |                     }
387 |                 ]
388 | 
389 |             @server.prompt()
390 |             async def analyze_file(path: str) -> list[Message]:
391 |                 content = await read_file(path)
392 |                 return [
393 |                     {
394 |                         "role": "user",
395 |                         "content": {
396 |                             "type": "resource",
397 |                             "resource": {
398 |                                 "uri": f"file://{path}",
399 |                                 "text": content
400 |                             }
401 |                         }
402 |                     }
403 |                 ]
404 |         """
405 |         # Check if user passed function directly instead of calling decorator
406 |         if callable(name):
407 |             raise TypeError(
408 |                 "The @prompt decorator was used incorrectly. "
409 |                 "Did you forget to call it? Use @prompt() instead of @prompt"
410 |             )
411 | 
412 |         def decorator(func: Callable[P, R_PromptResult]) -> Callable[P, R_PromptResult]:
413 |             prompt = Prompt.from_function(func, name=name, description=description)
414 |             self.add_prompt(prompt)
415 |             return func
416 | 
417 |         return decorator
418 | 
419 |     async def run_stdio_async(self) -> None:
420 |         """Run the server using stdio transport."""
421 |         async with stdio_server() as (read_stream, write_stream):
422 |             await self._mcp_server.run(
423 |                 read_stream,
424 |                 write_stream,
425 |                 self._mcp_server.create_initialization_options(),
426 |             )
427 | 
428 |     async def run_sse_async(self) -> None:
429 |         """Run the server using SSE transport."""
430 |         from starlette.applications import Starlette
431 |         from starlette.routing import Route
432 | 
433 |         sse = SseServerTransport("/messages")
434 | 
435 |         async def handle_sse(request):
436 |             async with sse.connect_sse(
437 |                 request.scope, request.receive, request._send
438 |             ) as streams:
439 |                 await self._mcp_server.run(
440 |                     streams[0],
441 |                     streams[1],
442 |                     self._mcp_server.create_initialization_options(),
443 |                 )
444 | 
445 |         async def handle_messages(request):
446 |             await sse.handle_post_message(request.scope, request.receive, request._send)
447 | 
448 |         starlette_app = Starlette(
449 |             debug=self.settings.debug,
450 |             routes=[
451 |                 Route("/sse", endpoint=handle_sse),
452 |                 Route("/messages", endpoint=handle_messages, methods=["POST"]),
453 |             ],
454 |         )
455 | 
456 |         config = uvicorn.Config(
457 |             starlette_app,
458 |             host=self.settings.host,
459 |             port=self.settings.port,
460 |             log_level=self.settings.log_level.lower(),
461 |         )
462 |         server = uvicorn.Server(config)
463 |         await server.serve()
464 | 
465 |     async def list_prompts(self) -> list[MCPPrompt]:
466 |         """List all available prompts."""
467 |         prompts = self._prompt_manager.list_prompts()
468 |         return [
469 |             MCPPrompt(
470 |                 name=prompt.name,
471 |                 description=prompt.description,
472 |                 arguments=[
473 |                     MCPPromptArgument(
474 |                         name=arg.name,
475 |                         description=arg.description,
476 |                         required=arg.required,
477 |                     )
478 |                     for arg in (prompt.arguments or [])
479 |                 ],
480 |             )
481 |             for prompt in prompts
482 |         ]
483 | 
484 |     async def get_prompt(
485 |         self, name: str, arguments: Dict[str, Any] | None = None
486 |     ) -> GetPromptResult:
487 |         """Get a prompt by name with arguments."""
488 |         try:
489 |             messages = await self._prompt_manager.render_prompt(name, arguments)
490 | 
491 |             return GetPromptResult(messages=pydantic_core.to_jsonable_python(messages))
492 |         except Exception as e:
493 |             logger.error(f"Error getting prompt {name}: {e}")
494 |             raise ValueError(str(e))
495 | 
496 | 
497 | def _convert_to_content(
498 |     result: Any,
499 | ) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
500 |     """Convert a result to a sequence of content objects."""
501 |     if result is None:
502 |         return []
503 | 
504 |     if isinstance(result, (TextContent, ImageContent, EmbeddedResource)):
505 |         return [result]
506 | 
507 |     if isinstance(result, Image):
508 |         return [result.to_image_content()]
509 | 
510 |     if isinstance(result, (list, tuple)):
511 |         return list(chain.from_iterable(_convert_to_content(item) for item in result))
512 | 
513 |     if not isinstance(result, str):
514 |         try:
515 |             result = json.dumps(pydantic_core.to_jsonable_python(result))
516 |         except Exception:
517 |             result = str(result)
518 | 
519 |     return [TextContent(type="text", text=result)]
520 | 
521 | 
522 | class Context(BaseModel):
523 |     """Context object providing access to MCP capabilities.
524 | 
525 |     This provides a cleaner interface to MCP's RequestContext functionality.
526 |     It gets injected into tool and resource functions that request it via type hints.
527 | 
528 |     To use context in a tool function, add a parameter with the Context type annotation:
529 | 
530 |     ```python
531 |     @server.tool()
532 |     def my_tool(x: int, ctx: Context) -> str:
533 |         # Log messages to the client
534 |         ctx.info(f"Processing {x}")
535 |         ctx.debug("Debug info")
536 |         ctx.warning("Warning message")
537 |         ctx.error("Error message")
538 | 
539 |         # Report progress
540 |         ctx.report_progress(50, 100)
541 | 
542 |         # Access resources
543 |         data = ctx.read_resource("resource://data")
544 | 
545 |         # Get request info
546 |         request_id = ctx.request_id
547 |         client_id = ctx.client_id
548 | 
549 |         return str(x)
550 |     ```
551 | 
552 |     The context parameter name can be anything as long as it's annotated with Context.
553 |     The context is optional - tools that don't need it can omit the parameter.
554 |     """
555 | 
556 |     _request_context: RequestContext | None
557 |     _fastmcp: FastMCP | None
558 | 
559 |     def __init__(
560 |         self,
561 |         *,
562 |         request_context: RequestContext | None = None,
563 |         fastmcp: FastMCP | None = None,
564 |         **kwargs: Any,
565 |     ):
566 |         super().__init__(**kwargs)
567 |         self._request_context = request_context
568 |         self._fastmcp = fastmcp
569 | 
570 |     @property
571 |     def fastmcp(self) -> FastMCP:
572 |         """Access to the FastMCP server."""
573 |         if self._fastmcp is None:
574 |             raise ValueError("Context is not available outside of a request")
575 |         return self._fastmcp
576 | 
577 |     @property
578 |     def request_context(self) -> RequestContext:
579 |         """Access to the underlying request context."""
580 |         if self._request_context is None:
581 |             raise ValueError("Context is not available outside of a request")
582 |         return self._request_context
583 | 
584 |     async def report_progress(
585 |         self, progress: float, total: float | None = None
586 |     ) -> None:
587 |         """Report progress for the current operation.
588 | 
589 |         Args:
590 |             progress: Current progress value e.g. 24
591 |             total: Optional total value e.g. 100
592 |         """
593 | 
594 |         progress_token = (
595 |             self.request_context.meta.progressToken
596 |             if self.request_context.meta
597 |             else None
598 |         )
599 | 
600 |         if not progress_token:
601 |             return
602 | 
603 |         await self.request_context.session.send_progress_notification(
604 |             progress_token=progress_token, progress=progress, total=total
605 |         )
606 | 
607 |     async def read_resource(self, uri: str | AnyUrl) -> str | bytes:
608 |         """Read a resource by URI.
609 | 
610 |         Args:
611 |             uri: Resource URI to read
612 | 
613 |         Returns:
614 |             The resource content as either text or bytes
615 |         """
616 |         assert (
617 |             self._fastmcp is not None
618 |         ), "Context is not available outside of a request"
619 |         return await self._fastmcp.read_resource(uri)
620 | 
621 |     def log(
622 |         self,
623 |         level: Literal["debug", "info", "warning", "error"],
624 |         message: str,
625 |         *,
626 |         logger_name: str | None = None,
627 |     ) -> None:
628 |         """Send a log message to the client.
629 | 
630 |         Args:
631 |             level: Log level (debug, info, warning, error)
632 |             message: Log message
633 |             logger_name: Optional logger name
634 |             **extra: Additional structured data to include
635 |         """
636 |         self.request_context.session.send_log_message(
637 |             level=level, data=message, logger=logger_name
638 |         )
639 | 
640 |     @property
641 |     def client_id(self) -> str | None:
642 |         """Get the client ID if available."""
643 |         return (
644 |             getattr(self.request_context.meta, "client_id", None)
645 |             if self.request_context.meta
646 |             else None
647 |         )
648 | 
649 |     @property
650 |     def request_id(self) -> str:
651 |         """Get the unique ID for this request."""
652 |         return str(self.request_context.request_id)
653 | 
654 |     @property
655 |     def session(self):
656 |         """Access to the underlying session for advanced usage."""
657 |         return self.request_context.session
658 | 
659 |     # Convenience methods for common log levels
660 |     def debug(self, message: str, **extra: Any) -> None:
661 |         """Send a debug log message."""
662 |         self.log("debug", message, **extra)
663 | 
664 |     def info(self, message: str, **extra: Any) -> None:
665 |         """Send an info log message."""
666 |         self.log("info", message, **extra)
667 | 
668 |     def warning(self, message: str, **extra: Any) -> None:
669 |         """Send a warning log message."""
670 |         self.log("warning", message, **extra)
671 | 
672 |     def error(self, message: str, **extra: Any) -> None:
673 |         """Send an error log message."""
674 |         self.log("error", message, **extra)
675 | 


--------------------------------------------------------------------------------
/src/fastmcp/tools/__init__.py:
--------------------------------------------------------------------------------
1 | from .base import Tool
2 | from .tool_manager import ToolManager
3 | 
4 | __all__ = ["Tool", "ToolManager"]
5 | 


--------------------------------------------------------------------------------
/src/fastmcp/tools/base.py:
--------------------------------------------------------------------------------
 1 | import fastmcp
 2 | from fastmcp.exceptions import ToolError
 3 | 
 4 | from fastmcp.utilities.func_metadata import func_metadata, FuncMetadata
 5 | from pydantic import BaseModel, Field
 6 | 
 7 | 
 8 | import inspect
 9 | from typing import TYPE_CHECKING, Any, Callable, Optional
10 | 
11 | if TYPE_CHECKING:
12 |     from fastmcp.server import Context
13 | 
14 | 
15 | class Tool(BaseModel):
16 |     """Internal tool registration info."""
17 | 
18 |     fn: Callable = Field(exclude=True)
19 |     name: str = Field(description="Name of the tool")
20 |     description: str = Field(description="Description of what the tool does")
21 |     parameters: dict = Field(description="JSON schema for tool parameters")
22 |     fn_metadata: FuncMetadata = Field(
23 |         description="Metadata about the function including a pydantic model for tool arguments"
24 |     )
25 |     is_async: bool = Field(description="Whether the tool is async")
26 |     context_kwarg: Optional[str] = Field(
27 |         None, description="Name of the kwarg that should receive context"
28 |     )
29 | 
30 |     @classmethod
31 |     def from_function(
32 |         cls,
33 |         fn: Callable,
34 |         name: Optional[str] = None,
35 |         description: Optional[str] = None,
36 |         context_kwarg: Optional[str] = None,
37 |     ) -> "Tool":
38 |         """Create a Tool from a function."""
39 |         func_name = name or fn.__name__
40 | 
41 |         if func_name == "<lambda>":
42 |             raise ValueError("You must provide a name for lambda functions")
43 | 
44 |         func_doc = description or fn.__doc__ or ""
45 |         is_async = inspect.iscoroutinefunction(fn)
46 | 
47 |         # Find context parameter if it exists
48 |         if context_kwarg is None:
49 |             sig = inspect.signature(fn)
50 |             for param_name, param in sig.parameters.items():
51 |                 if param.annotation is fastmcp.Context:
52 |                     context_kwarg = param_name
53 |                     break
54 | 
55 |         func_arg_metadata = func_metadata(
56 |             fn,
57 |             skip_names=[context_kwarg] if context_kwarg is not None else [],
58 |         )
59 |         parameters = func_arg_metadata.arg_model.model_json_schema()
60 | 
61 |         return cls(
62 |             fn=fn,
63 |             name=func_name,
64 |             description=func_doc,
65 |             parameters=parameters,
66 |             fn_metadata=func_arg_metadata,
67 |             is_async=is_async,
68 |             context_kwarg=context_kwarg,
69 |         )
70 | 
71 |     async def run(self, arguments: dict, context: Optional["Context"] = None) -> Any:
72 |         """Run the tool with arguments."""
73 |         try:
74 |             return await self.fn_metadata.call_fn_with_arg_validation(
75 |                 self.fn,
76 |                 self.is_async,
77 |                 arguments,
78 |                 {self.context_kwarg: context}
79 |                 if self.context_kwarg is not None
80 |                 else None,
81 |             )
82 |         except Exception as e:
83 |             raise ToolError(f"Error executing tool {self.name}: {e}") from e
84 | 


--------------------------------------------------------------------------------
/src/fastmcp/tools/tool_manager.py:
--------------------------------------------------------------------------------
 1 | from fastmcp.exceptions import ToolError
 2 | 
 3 | from fastmcp.tools.base import Tool
 4 | 
 5 | 
 6 | from typing import Any, Callable, Dict, Optional, TYPE_CHECKING
 7 | 
 8 | from fastmcp.utilities.logging import get_logger
 9 | 
10 | if TYPE_CHECKING:
11 |     from fastmcp.server import Context
12 | 
13 | logger = get_logger(__name__)
14 | 
15 | 
16 | class ToolManager:
17 |     """Manages FastMCP tools."""
18 | 
19 |     def __init__(self, warn_on_duplicate_tools: bool = True):
20 |         self._tools: Dict[str, Tool] = {}
21 |         self.warn_on_duplicate_tools = warn_on_duplicate_tools
22 | 
23 |     def get_tool(self, name: str) -> Optional[Tool]:
24 |         """Get tool by name."""
25 |         return self._tools.get(name)
26 | 
27 |     def list_tools(self) -> list[Tool]:
28 |         """List all registered tools."""
29 |         return list(self._tools.values())
30 | 
31 |     def add_tool(
32 |         self,
33 |         fn: Callable,
34 |         name: Optional[str] = None,
35 |         description: Optional[str] = None,
36 |     ) -> Tool:
37 |         """Add a tool to the server."""
38 |         tool = Tool.from_function(fn, name=name, description=description)
39 |         existing = self._tools.get(tool.name)
40 |         if existing:
41 |             if self.warn_on_duplicate_tools:
42 |                 logger.warning(f"Tool already exists: {tool.name}")
43 |             return existing
44 |         self._tools[tool.name] = tool
45 |         return tool
46 | 
47 |     async def call_tool(
48 |         self, name: str, arguments: dict, context: Optional["Context"] = None
49 |     ) -> Any:
50 |         """Call a tool by name with arguments."""
51 |         tool = self.get_tool(name)
52 |         if not tool:
53 |             raise ToolError(f"Unknown tool: {name}")
54 | 
55 |         return await tool.run(arguments, context=context)
56 | 


--------------------------------------------------------------------------------
/src/fastmcp/utilities/__init__.py:
--------------------------------------------------------------------------------
1 | """FastMCP utility modules."""
2 | 


--------------------------------------------------------------------------------
/src/fastmcp/utilities/func_metadata.py:
--------------------------------------------------------------------------------
  1 | import inspect
  2 | from collections.abc import Callable, Sequence, Awaitable
  3 | from typing import (
  4 |     Annotated,
  5 |     Any,
  6 |     Dict,
  7 |     ForwardRef,
  8 | )
  9 | from pydantic import Field
 10 | from fastmcp.exceptions import InvalidSignature
 11 | from pydantic._internal._typing_extra import eval_type_lenient
 12 | import json
 13 | from pydantic import BaseModel
 14 | from pydantic.fields import FieldInfo
 15 | from pydantic import ConfigDict, create_model
 16 | from pydantic import WithJsonSchema
 17 | from pydantic_core import PydanticUndefined
 18 | from fastmcp.utilities.logging import get_logger
 19 | 
 20 | 
 21 | logger = get_logger(__name__)
 22 | 
 23 | 
 24 | class ArgModelBase(BaseModel):
 25 |     """A model representing the arguments to a function."""
 26 | 
 27 |     def model_dump_one_level(self) -> dict[str, Any]:
 28 |         """Return a dict of the model's fields, one level deep.
 29 | 
 30 |         That is, sub-models etc are not dumped - they are kept as pydantic models.
 31 |         """
 32 |         kwargs: dict[str, Any] = {}
 33 |         for field_name in self.model_fields.keys():
 34 |             kwargs[field_name] = getattr(self, field_name)
 35 |         return kwargs
 36 | 
 37 |     model_config = ConfigDict(
 38 |         arbitrary_types_allowed=True,
 39 |     )
 40 | 
 41 | 
 42 | class FuncMetadata(BaseModel):
 43 |     arg_model: Annotated[type[ArgModelBase], WithJsonSchema(None)]
 44 |     # We can add things in the future like
 45 |     #  - Maybe some args are excluded from attempting to parse from JSON
 46 |     #  - Maybe some args are special (like context) for dependency injection
 47 | 
 48 |     async def call_fn_with_arg_validation(
 49 |         self,
 50 |         fn: Callable[..., Any] | Awaitable[Any],
 51 |         fn_is_async: bool,
 52 |         arguments_to_validate: dict[str, Any],
 53 |         arguments_to_pass_directly: dict[str, Any] | None,
 54 |     ) -> Any:
 55 |         """Call the given function with arguments validated and injected.
 56 | 
 57 |         Arguments are first attempted to be parsed from JSON, then validated against
 58 |         the argument model, before being passed to the function.
 59 |         """
 60 |         arguments_pre_parsed = self.pre_parse_json(arguments_to_validate)
 61 |         arguments_parsed_model = self.arg_model.model_validate(arguments_pre_parsed)
 62 |         arguments_parsed_dict = arguments_parsed_model.model_dump_one_level()
 63 | 
 64 |         arguments_parsed_dict |= arguments_to_pass_directly or {}
 65 | 
 66 |         if fn_is_async:
 67 |             if isinstance(fn, Awaitable):
 68 |                 return await fn
 69 |             return await fn(**arguments_parsed_dict)
 70 |         if isinstance(fn, Callable):
 71 |             return fn(**arguments_parsed_dict)
 72 |         raise TypeError("fn must be either Callable or Awaitable")
 73 | 
 74 |     def pre_parse_json(self, data: dict[str, Any]) -> dict[str, Any]:
 75 |         """Pre-parse data from JSON.
 76 | 
 77 |         Return a dict with same keys as input but with values parsed from JSON
 78 |         if appropriate.
 79 | 
 80 |         This is to handle cases like `["a", "b", "c"]` being passed in as JSON inside
 81 |         a string rather than an actual list. Claude desktop is prone to this - in fact
 82 |         it seems incapable of NOT doing this. For sub-models, it tends to pass
 83 |         dicts (JSON objects) as JSON strings, which can be pre-parsed here.
 84 |         """
 85 |         new_data = data.copy()  # Shallow copy
 86 |         for field_name, field_info in self.arg_model.model_fields.items():
 87 |             if field_name not in data.keys():
 88 |                 continue
 89 |             if isinstance(data[field_name], str):
 90 |                 try:
 91 |                     pre_parsed = json.loads(data[field_name])
 92 |                 except json.JSONDecodeError:
 93 |                     continue  # Not JSON - skip
 94 |                 if isinstance(pre_parsed, (str, int, float)):
 95 |                     # This is likely that the raw value is e.g. `"hello"` which we
 96 |                     # Should really be parsed as '"hello"' in Python - but if we parse
 97 |                     # it as JSON it'll turn into just 'hello'. So we skip it.
 98 |                     continue
 99 |                 new_data[field_name] = pre_parsed
100 |         assert new_data.keys() == data.keys()
101 |         return new_data
102 | 
103 |     model_config = ConfigDict(
104 |         arbitrary_types_allowed=True,
105 |     )
106 | 
107 | 
108 | def func_metadata(func: Callable, skip_names: Sequence[str] = ()) -> FuncMetadata:
109 |     """Given a function, return metadata including a pydantic model representing its signature.
110 | 
111 |     The use case for this is
112 |     ```
113 |     meta = func_to_pyd(func)
114 |     validated_args = meta.arg_model.model_validate(some_raw_data_dict)
115 |     return func(**validated_args.model_dump_one_level())
116 |     ```
117 | 
118 |     **critically** it also provides pre-parse helper to attempt to parse things from JSON.
119 | 
120 |     Args:
121 |         func: The function to convert to a pydantic model
122 |         skip_names: A list of parameter names to skip. These will not be included in
123 |             the model.
124 |     Returns:
125 |         A pydantic model representing the function's signature.
126 |     """
127 |     sig = _get_typed_signature(func)
128 |     params = sig.parameters
129 |     dynamic_pydantic_model_params: dict[str, Any] = {}
130 |     globalns = getattr(func, "__globals__", {})
131 |     for param in params.values():
132 |         if param.name.startswith("_"):
133 |             raise InvalidSignature(
134 |                 f"Parameter {param.name} of {func.__name__} may not start with an underscore"
135 |             )
136 |         if param.name in skip_names:
137 |             continue
138 |         annotation = param.annotation
139 | 
140 |         # `x: None` / `x: None = None`
141 |         if annotation is None:
142 |             annotation = Annotated[
143 |                 None,
144 |                 Field(
145 |                     default=param.default
146 |                     if param.default is not inspect.Parameter.empty
147 |                     else PydanticUndefined
148 |                 ),
149 |             ]
150 | 
151 |         # Untyped field
152 |         if annotation is inspect.Parameter.empty:
153 |             annotation = Annotated[
154 |                 Any,
155 |                 Field(),
156 |                 # 🤷
157 |                 WithJsonSchema({"title": param.name, "type": "string"}),
158 |             ]
159 | 
160 |         field_info = FieldInfo.from_annotated_attribute(
161 |             _get_typed_annotation(annotation, globalns),
162 |             param.default
163 |             if param.default is not inspect.Parameter.empty
164 |             else PydanticUndefined,
165 |         )
166 |         dynamic_pydantic_model_params[param.name] = (field_info.annotation, field_info)
167 |         continue
168 | 
169 |     arguments_model = create_model(
170 |         f"{func.__name__}Arguments",
171 |         **dynamic_pydantic_model_params,
172 |         __base__=ArgModelBase,
173 |     )
174 |     resp = FuncMetadata(arg_model=arguments_model)
175 |     return resp
176 | 
177 | 
178 | def _get_typed_annotation(annotation: Any, globalns: Dict[str, Any]) -> Any:
179 |     if isinstance(annotation, str):
180 |         annotation = ForwardRef(annotation)
181 |         annotation = eval_type_lenient(annotation, globalns, globalns)
182 | 
183 |     return annotation
184 | 
185 | 
186 | def _get_typed_signature(call: Callable[..., Any]) -> inspect.Signature:
187 |     """Get function signature while evaluating forward references"""
188 |     signature = inspect.signature(call)
189 |     globalns = getattr(call, "__globals__", {})
190 |     typed_params = [
191 |         inspect.Parameter(
192 |             name=param.name,
193 |             kind=param.kind,
194 |             default=param.default,
195 |             annotation=_get_typed_annotation(param.annotation, globalns),
196 |         )
197 |         for param in signature.parameters.values()
198 |     ]
199 |     typed_signature = inspect.Signature(typed_params)
200 |     return typed_signature
201 | 


--------------------------------------------------------------------------------
/src/fastmcp/utilities/logging.py:
--------------------------------------------------------------------------------
 1 | """Logging utilities for FastMCP."""
 2 | 
 3 | import logging
 4 | from typing import Literal
 5 | 
 6 | from rich.console import Console
 7 | from rich.logging import RichHandler
 8 | 
 9 | 
10 | def get_logger(name: str) -> logging.Logger:
11 |     """Get a logger nested under FastMCP namespace.
12 | 
13 |     Args:
14 |         name: the name of the logger, which will be prefixed with 'FastMCP.'
15 | 
16 |     Returns:
17 |         a configured logger instance
18 |     """
19 |     return logging.getLogger(f"FastMCP.{name}")
20 | 
21 | 
22 | def configure_logging(
23 |     level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
24 | ) -> None:
25 |     """Configure logging for FastMCP.
26 | 
27 |     Args:
28 |         level: the log level to use
29 |     """
30 |     logging.basicConfig(
31 |         level=level,
32 |         format="%(message)s",
33 |         handlers=[RichHandler(console=Console(stderr=True), rich_tracebacks=True)],
34 |     )
35 | 


--------------------------------------------------------------------------------
/src/fastmcp/utilities/types.py:
--------------------------------------------------------------------------------
 1 | """Common types used across FastMCP."""
 2 | 
 3 | import base64
 4 | from pathlib import Path
 5 | from typing import Optional, Union
 6 | 
 7 | from mcp.types import ImageContent
 8 | 
 9 | 
10 | class Image:
11 |     """Helper class for returning images from tools."""
12 | 
13 |     def __init__(
14 |         self,
15 |         path: Optional[Union[str, Path]] = None,
16 |         data: Optional[bytes] = None,
17 |         format: Optional[str] = None,
18 |     ):
19 |         if path is None and data is None:
20 |             raise ValueError("Either path or data must be provided")
21 |         if path is not None and data is not None:
22 |             raise ValueError("Only one of path or data can be provided")
23 | 
24 |         self.path = Path(path) if path else None
25 |         self.data = data
26 |         self._format = format
27 |         self._mime_type = self._get_mime_type()
28 | 
29 |     def _get_mime_type(self) -> str:
30 |         """Get MIME type from format or guess from file extension."""
31 |         if self._format:
32 |             return f"image/{self._format.lower()}"
33 | 
34 |         if self.path:
35 |             suffix = self.path.suffix.lower()
36 |             return {
37 |                 ".png": "image/png",
38 |                 ".jpg": "image/jpeg",
39 |                 ".jpeg": "image/jpeg",
40 |                 ".gif": "image/gif",
41 |                 ".webp": "image/webp",
42 |             }.get(suffix, "application/octet-stream")
43 |         return "image/png"  # default for raw binary data
44 | 
45 |     def to_image_content(self) -> ImageContent:
46 |         """Convert to MCP ImageContent."""
47 |         if self.path:
48 |             with open(self.path, "rb") as f:
49 |                 data = base64.b64encode(f.read()).decode()
50 |         elif self.data is not None:
51 |             data = base64.b64encode(self.data).decode()
52 |         else:
53 |             raise ValueError("No image data available")
54 | 
55 |         return ImageContent(type="image", data=data, mimeType=self._mime_type)
56 | 


--------------------------------------------------------------------------------
/tests/__init__.py:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/jlowin/fastmcp/80c328b3dc0b949f010456ee0e85cc5c90e3305f/tests/__init__.py


--------------------------------------------------------------------------------
/tests/prompts/__init__.py:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/jlowin/fastmcp/80c328b3dc0b949f010456ee0e85cc5c90e3305f/tests/prompts/__init__.py


--------------------------------------------------------------------------------
/tests/prompts/test_base.py:
--------------------------------------------------------------------------------
  1 | from pydantic import FileUrl
  2 | import pytest
  3 | from fastmcp.prompts.base import (
  4 |     Prompt,
  5 |     UserMessage,
  6 |     TextContent,
  7 |     AssistantMessage,
  8 |     Message,
  9 | )
 10 | from mcp.types import EmbeddedResource, TextResourceContents
 11 | 
 12 | 
 13 | class TestRenderPrompt:
 14 |     async def test_basic_fn(self):
 15 |         def fn() -> str:
 16 |             return "Hello, world!"
 17 | 
 18 |         prompt = Prompt.from_function(fn)
 19 |         assert await prompt.render() == [
 20 |             UserMessage(content=TextContent(type="text", text="Hello, world!"))
 21 |         ]
 22 | 
 23 |     async def test_async_fn(self):
 24 |         async def fn() -> str:
 25 |             return "Hello, world!"
 26 | 
 27 |         prompt = Prompt.from_function(fn)
 28 |         assert await prompt.render() == [
 29 |             UserMessage(content=TextContent(type="text", text="Hello, world!"))
 30 |         ]
 31 | 
 32 |     async def test_fn_with_args(self):
 33 |         async def fn(name: str, age: int = 30) -> str:
 34 |             return f"Hello, {name}! You're {age} years old."
 35 | 
 36 |         prompt = Prompt.from_function(fn)
 37 |         assert await prompt.render(arguments=dict(name="World")) == [
 38 |             UserMessage(
 39 |                 content=TextContent(
 40 |                     type="text", text="Hello, World! You're 30 years old."
 41 |                 )
 42 |             )
 43 |         ]
 44 | 
 45 |     async def test_fn_with_invalid_kwargs(self):
 46 |         async def fn(name: str, age: int = 30) -> str:
 47 |             return f"Hello, {name}! You're {age} years old."
 48 | 
 49 |         prompt = Prompt.from_function(fn)
 50 |         with pytest.raises(ValueError):
 51 |             await prompt.render(arguments=dict(age=40))
 52 | 
 53 |     async def test_fn_returns_message(self):
 54 |         async def fn() -> UserMessage:
 55 |             return UserMessage(content="Hello, world!")
 56 | 
 57 |         prompt = Prompt.from_function(fn)
 58 |         assert await prompt.render() == [
 59 |             UserMessage(content=TextContent(type="text", text="Hello, world!"))
 60 |         ]
 61 | 
 62 |     async def test_fn_returns_assistant_message(self):
 63 |         async def fn() -> AssistantMessage:
 64 |             return AssistantMessage(
 65 |                 content=TextContent(type="text", text="Hello, world!")
 66 |             )
 67 | 
 68 |         prompt = Prompt.from_function(fn)
 69 |         assert await prompt.render() == [
 70 |             AssistantMessage(content=TextContent(type="text", text="Hello, world!"))
 71 |         ]
 72 | 
 73 |     async def test_fn_returns_multiple_messages(self):
 74 |         expected = [
 75 |             UserMessage("Hello, world!"),
 76 |             AssistantMessage("How can I help you today?"),
 77 |             UserMessage("I'm looking for a restaurant in the center of town."),
 78 |         ]
 79 | 
 80 |         async def fn() -> list[Message]:
 81 |             return expected
 82 | 
 83 |         prompt = Prompt.from_function(fn)
 84 |         assert await prompt.render() == expected
 85 | 
 86 |     async def test_fn_returns_list_of_strings(self):
 87 |         expected = [
 88 |             "Hello, world!",
 89 |             "I'm looking for a restaurant in the center of town.",
 90 |         ]
 91 | 
 92 |         async def fn() -> list[str]:
 93 |             return expected
 94 | 
 95 |         prompt = Prompt.from_function(fn)
 96 |         assert await prompt.render() == [UserMessage(t) for t in expected]
 97 | 
 98 |     async def test_fn_returns_resource_content(self):
 99 |         """Test returning a message with resource content."""
100 | 
101 |         async def fn() -> UserMessage:
102 |             return UserMessage(
103 |                 content=EmbeddedResource(
104 |                     type="resource",
105 |                     resource=TextResourceContents(
106 |                         uri=FileUrl("file://file.txt"),
107 |                         text="File contents",
108 |                         mimeType="text/plain",
109 |                     ),
110 |                 )
111 |             )
112 | 
113 |         prompt = Prompt.from_function(fn)
114 |         assert await prompt.render() == [
115 |             UserMessage(
116 |                 content=EmbeddedResource(
117 |                     type="resource",
118 |                     resource=TextResourceContents(
119 |                         uri=FileUrl("file://file.txt"),
120 |                         text="File contents",
121 |                         mimeType="text/plain",
122 |                     ),
123 |                 )
124 |             )
125 |         ]
126 | 
127 |     async def test_fn_returns_mixed_content(self):
128 |         """Test returning messages with mixed content types."""
129 | 
130 |         async def fn() -> list[Message]:
131 |             return [
132 |                 UserMessage(content="Please analyze this file:"),
133 |                 UserMessage(
134 |                     content=EmbeddedResource(
135 |                         type="resource",
136 |                         resource=TextResourceContents(
137 |                             uri=FileUrl("file://file.txt"),
138 |                             text="File contents",
139 |                             mimeType="text/plain",
140 |                         ),
141 |                     )
142 |                 ),
143 |                 AssistantMessage(content="I'll help analyze that file."),
144 |             ]
145 | 
146 |         prompt = Prompt.from_function(fn)
147 |         assert await prompt.render() == [
148 |             UserMessage(
149 |                 content=TextContent(type="text", text="Please analyze this file:")
150 |             ),
151 |             UserMessage(
152 |                 content=EmbeddedResource(
153 |                     type="resource",
154 |                     resource=TextResourceContents(
155 |                         uri=FileUrl("file://file.txt"),
156 |                         text="File contents",
157 |                         mimeType="text/plain",
158 |                     ),
159 |                 )
160 |             ),
161 |             AssistantMessage(
162 |                 content=TextContent(type="text", text="I'll help analyze that file.")
163 |             ),
164 |         ]
165 | 
166 |     async def test_fn_returns_dict_with_resource(self):
167 |         """Test returning a dict with resource content."""
168 | 
169 |         async def fn() -> dict:
170 |             return {
171 |                 "role": "user",
172 |                 "content": {
173 |                     "type": "resource",
174 |                     "resource": {
175 |                         "uri": FileUrl("file://file.txt"),
176 |                         "text": "File contents",
177 |                         "mimeType": "text/plain",
178 |                     },
179 |                 },
180 |             }
181 | 
182 |         prompt = Prompt.from_function(fn)
183 |         assert await prompt.render() == [
184 |             UserMessage(
185 |                 content=EmbeddedResource(
186 |                     type="resource",
187 |                     resource=TextResourceContents(
188 |                         uri=FileUrl("file://file.txt"),
189 |                         text="File contents",
190 |                         mimeType="text/plain",
191 |                     ),
192 |                 )
193 |             )
194 |         ]
195 | 


--------------------------------------------------------------------------------
/tests/prompts/test_manager.py:
--------------------------------------------------------------------------------
  1 | import pytest
  2 | from fastmcp.prompts.base import UserMessage, TextContent, Prompt
  3 | from fastmcp.prompts.manager import PromptManager
  4 | 
  5 | 
  6 | class TestPromptManager:
  7 |     def test_add_prompt(self):
  8 |         """Test adding a prompt to the manager."""
  9 | 
 10 |         def fn() -> str:
 11 |             return "Hello, world!"
 12 | 
 13 |         manager = PromptManager()
 14 |         prompt = Prompt.from_function(fn)
 15 |         added = manager.add_prompt(prompt)
 16 |         assert added == prompt
 17 |         assert manager.get_prompt("fn") == prompt
 18 | 
 19 |     def test_add_duplicate_prompt(self, caplog):
 20 |         """Test adding the same prompt twice."""
 21 | 
 22 |         def fn() -> str:
 23 |             return "Hello, world!"
 24 | 
 25 |         manager = PromptManager()
 26 |         prompt = Prompt.from_function(fn)
 27 |         first = manager.add_prompt(prompt)
 28 |         second = manager.add_prompt(prompt)
 29 |         assert first == second
 30 |         assert "Prompt already exists" in caplog.text
 31 | 
 32 |     def test_disable_warn_on_duplicate_prompts(self, caplog):
 33 |         """Test disabling warning on duplicate prompts."""
 34 | 
 35 |         def fn() -> str:
 36 |             return "Hello, world!"
 37 | 
 38 |         manager = PromptManager(warn_on_duplicate_prompts=False)
 39 |         prompt = Prompt.from_function(fn)
 40 |         first = manager.add_prompt(prompt)
 41 |         second = manager.add_prompt(prompt)
 42 |         assert first == second
 43 |         assert "Prompt already exists" not in caplog.text
 44 | 
 45 |     def test_list_prompts(self):
 46 |         """Test listing all prompts."""
 47 | 
 48 |         def fn1() -> str:
 49 |             return "Hello, world!"
 50 | 
 51 |         def fn2() -> str:
 52 |             return "Goodbye, world!"
 53 | 
 54 |         manager = PromptManager()
 55 |         prompt1 = Prompt.from_function(fn1)
 56 |         prompt2 = Prompt.from_function(fn2)
 57 |         manager.add_prompt(prompt1)
 58 |         manager.add_prompt(prompt2)
 59 |         prompts = manager.list_prompts()
 60 |         assert len(prompts) == 2
 61 |         assert prompts == [prompt1, prompt2]
 62 | 
 63 |     async def test_render_prompt(self):
 64 |         """Test rendering a prompt."""
 65 | 
 66 |         def fn() -> str:
 67 |             return "Hello, world!"
 68 | 
 69 |         manager = PromptManager()
 70 |         prompt = Prompt.from_function(fn)
 71 |         manager.add_prompt(prompt)
 72 |         messages = await manager.render_prompt("fn")
 73 |         assert messages == [
 74 |             UserMessage(content=TextContent(type="text", text="Hello, world!"))
 75 |         ]
 76 | 
 77 |     async def test_render_prompt_with_args(self):
 78 |         """Test rendering a prompt with arguments."""
 79 | 
 80 |         def fn(name: str) -> str:
 81 |             return f"Hello, {name}!"
 82 | 
 83 |         manager = PromptManager()
 84 |         prompt = Prompt.from_function(fn)
 85 |         manager.add_prompt(prompt)
 86 |         messages = await manager.render_prompt("fn", arguments={"name": "World"})
 87 |         assert messages == [
 88 |             UserMessage(content=TextContent(type="text", text="Hello, World!"))
 89 |         ]
 90 | 
 91 |     async def test_render_unknown_prompt(self):
 92 |         """Test rendering a non-existent prompt."""
 93 |         manager = PromptManager()
 94 |         with pytest.raises(ValueError, match="Unknown prompt: unknown"):
 95 |             await manager.render_prompt("unknown")
 96 | 
 97 |     async def test_render_prompt_with_missing_args(self):
 98 |         """Test rendering a prompt with missing required arguments."""
 99 | 
100 |         def fn(name: str) -> str:
101 |             return f"Hello, {name}!"
102 | 
103 |         manager = PromptManager()
104 |         prompt = Prompt.from_function(fn)
105 |         manager.add_prompt(prompt)
106 |         with pytest.raises(ValueError, match="Missing required arguments"):
107 |             await manager.render_prompt("fn")
108 | 


--------------------------------------------------------------------------------
/tests/resources/__init__.py:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/jlowin/fastmcp/80c328b3dc0b949f010456ee0e85cc5c90e3305f/tests/resources/__init__.py


--------------------------------------------------------------------------------
/tests/resources/test_file_resources.py:
--------------------------------------------------------------------------------
  1 | import os
  2 | 
  3 | import pytest
  4 | from pathlib import Path
  5 | from tempfile import NamedTemporaryFile
  6 | from pydantic import FileUrl
  7 | 
  8 | from fastmcp.resources import FileResource
  9 | 
 10 | 
 11 | @pytest.fixture
 12 | def temp_file():
 13 |     """Create a temporary file for testing.
 14 | 
 15 |     File is automatically cleaned up after the test if it still exists.
 16 |     """
 17 |     content = "test content"
 18 |     with NamedTemporaryFile(mode="w", delete=False) as f:
 19 |         f.write(content)
 20 |         path = Path(f.name).resolve()
 21 |     yield path
 22 |     try:
 23 |         path.unlink()
 24 |     except FileNotFoundError:
 25 |         pass  # File was already deleted by the test
 26 | 
 27 | 
 28 | class TestFileResource:
 29 |     """Test FileResource functionality."""
 30 | 
 31 |     def test_file_resource_creation(self, temp_file: Path):
 32 |         """Test creating a FileResource."""
 33 |         resource = FileResource(
 34 |             uri=FileUrl(temp_file.as_uri()),
 35 |             name="test",
 36 |             description="test file",
 37 |             path=temp_file,
 38 |         )
 39 |         assert str(resource.uri) == temp_file.as_uri()
 40 |         assert resource.name == "test"
 41 |         assert resource.description == "test file"
 42 |         assert resource.mime_type == "text/plain"  # default
 43 |         assert resource.path == temp_file
 44 |         assert resource.is_binary is False  # default
 45 | 
 46 |     def test_file_resource_str_path_conversion(self, temp_file: Path):
 47 |         """Test FileResource handles string paths."""
 48 |         resource = FileResource(
 49 |             uri=FileUrl(f"file://{temp_file}"),
 50 |             name="test",
 51 |             path=Path(str(temp_file)),
 52 |         )
 53 |         assert isinstance(resource.path, Path)
 54 |         assert resource.path.is_absolute()
 55 | 
 56 |     async def test_read_text_file(self, temp_file: Path):
 57 |         """Test reading a text file."""
 58 |         resource = FileResource(
 59 |             uri=FileUrl(f"file://{temp_file}"),
 60 |             name="test",
 61 |             path=temp_file,
 62 |         )
 63 |         content = await resource.read()
 64 |         assert content == "test content"
 65 |         assert resource.mime_type == "text/plain"
 66 | 
 67 |     async def test_read_binary_file(self, temp_file: Path):
 68 |         """Test reading a file as binary."""
 69 |         resource = FileResource(
 70 |             uri=FileUrl(f"file://{temp_file}"),
 71 |             name="test",
 72 |             path=temp_file,
 73 |             is_binary=True,
 74 |         )
 75 |         content = await resource.read()
 76 |         assert isinstance(content, bytes)
 77 |         assert content == b"test content"
 78 | 
 79 |     def test_relative_path_error(self):
 80 |         """Test error on relative path."""
 81 |         with pytest.raises(ValueError, match="Path must be absolute"):
 82 |             FileResource(
 83 |                 uri=FileUrl("file:///test.txt"),
 84 |                 name="test",
 85 |                 path=Path("test.txt"),
 86 |             )
 87 | 
 88 |     async def test_missing_file_error(self, temp_file: Path):
 89 |         """Test error when file doesn't exist."""
 90 |         # Create path to non-existent file
 91 |         missing = temp_file.parent / "missing.txt"
 92 |         resource = FileResource(
 93 |             uri=FileUrl("file:///missing.txt"),
 94 |             name="test",
 95 |             path=missing,
 96 |         )
 97 |         with pytest.raises(ValueError, match="Error reading file"):
 98 |             await resource.read()
 99 | 
100 |     @pytest.mark.skipif(
101 |         os.name == "nt", reason="File permissions behave differently on Windows"
102 |     )
103 |     async def test_permission_error(self, temp_file: Path):
104 |         """Test reading a file without permissions."""
105 |         temp_file.chmod(0o000)  # Remove all permissions
106 |         try:
107 |             resource = FileResource(
108 |                 uri=FileUrl(temp_file.as_uri()),
109 |                 name="test",
110 |                 path=temp_file,
111 |             )
112 |             with pytest.raises(ValueError, match="Error reading file"):
113 |                 await resource.read()
114 |         finally:
115 |             temp_file.chmod(0o644)  # Restore permissions
116 | 


--------------------------------------------------------------------------------
/tests/resources/test_function_resources.py:
--------------------------------------------------------------------------------
  1 | from pydantic import BaseModel, AnyUrl
  2 | import pytest
  3 | from fastmcp.resources import FunctionResource
  4 | 
  5 | 
  6 | class TestFunctionResource:
  7 |     """Test FunctionResource functionality."""
  8 | 
  9 |     def test_function_resource_creation(self):
 10 |         """Test creating a FunctionResource."""
 11 | 
 12 |         def my_func() -> str:
 13 |             return "test content"
 14 | 
 15 |         resource = FunctionResource(
 16 |             uri=AnyUrl("fn://test"),
 17 |             name="test",
 18 |             description="test function",
 19 |             fn=my_func,
 20 |         )
 21 |         assert str(resource.uri) == "fn://test"
 22 |         assert resource.name == "test"
 23 |         assert resource.description == "test function"
 24 |         assert resource.mime_type == "text/plain"  # default
 25 |         assert resource.fn == my_func
 26 | 
 27 |     async def test_read_text(self):
 28 |         """Test reading text from a FunctionResource."""
 29 | 
 30 |         def get_data() -> str:
 31 |             return "Hello, world!"
 32 | 
 33 |         resource = FunctionResource(
 34 |             uri=AnyUrl("function://test"),
 35 |             name="test",
 36 |             fn=get_data,
 37 |         )
 38 |         content = await resource.read()
 39 |         assert content == "Hello, world!"
 40 |         assert resource.mime_type == "text/plain"
 41 | 
 42 |     async def test_read_binary(self):
 43 |         """Test reading binary data from a FunctionResource."""
 44 | 
 45 |         def get_data() -> bytes:
 46 |             return b"Hello, world!"
 47 | 
 48 |         resource = FunctionResource(
 49 |             uri=AnyUrl("function://test"),
 50 |             name="test",
 51 |             fn=get_data,
 52 |         )
 53 |         content = await resource.read()
 54 |         assert content == b"Hello, world!"
 55 | 
 56 |     async def test_json_conversion(self):
 57 |         """Test automatic JSON conversion of non-string results."""
 58 | 
 59 |         def get_data() -> dict:
 60 |             return {"key": "value"}
 61 | 
 62 |         resource = FunctionResource(
 63 |             uri=AnyUrl("function://test"),
 64 |             name="test",
 65 |             fn=get_data,
 66 |         )
 67 |         content = await resource.read()
 68 |         assert isinstance(content, str)
 69 |         assert '"key": "value"' in content
 70 | 
 71 |     async def test_error_handling(self):
 72 |         """Test error handling in FunctionResource."""
 73 | 
 74 |         def failing_func() -> str:
 75 |             raise ValueError("Test error")
 76 | 
 77 |         resource = FunctionResource(
 78 |             uri=AnyUrl("function://test"),
 79 |             name="test",
 80 |             fn=failing_func,
 81 |         )
 82 |         with pytest.raises(ValueError, match="Error reading resource function://test"):
 83 |             await resource.read()
 84 | 
 85 |     async def test_basemodel_conversion(self):
 86 |         """Test handling of BaseModel types."""
 87 | 
 88 |         class MyModel(BaseModel):
 89 |             name: str
 90 | 
 91 |         resource = FunctionResource(
 92 |             uri=AnyUrl("function://test"),
 93 |             name="test",
 94 |             fn=lambda: MyModel(name="test"),
 95 |         )
 96 |         content = await resource.read()
 97 |         assert content == '{"name": "test"}'
 98 | 
 99 |     async def test_custom_type_conversion(self):
100 |         """Test handling of custom types."""
101 | 
102 |         class CustomData:
103 |             def __str__(self) -> str:
104 |                 return "custom data"
105 | 
106 |         def get_data() -> CustomData:
107 |             return CustomData()
108 | 
109 |         resource = FunctionResource(
110 |             uri=AnyUrl("function://test"),
111 |             name="test",
112 |             fn=get_data,
113 |         )
114 |         content = await resource.read()
115 |         assert isinstance(content, str)
116 | 


--------------------------------------------------------------------------------
/tests/resources/test_resource_manager.py:
--------------------------------------------------------------------------------
  1 | import pytest
  2 | from pathlib import Path
  3 | from tempfile import NamedTemporaryFile
  4 | from pydantic import AnyUrl, FileUrl
  5 | 
  6 | from fastmcp.resources import (
  7 |     FileResource,
  8 |     FunctionResource,
  9 |     ResourceManager,
 10 |     ResourceTemplate,
 11 | )
 12 | 
 13 | 
 14 | @pytest.fixture
 15 | def temp_file():
 16 |     """Create a temporary file for testing.
 17 | 
 18 |     File is automatically cleaned up after the test if it still exists.
 19 |     """
 20 |     content = "test content"
 21 |     with NamedTemporaryFile(mode="w", delete=False) as f:
 22 |         f.write(content)
 23 |         path = Path(f.name).resolve()
 24 |     yield path
 25 |     try:
 26 |         path.unlink()
 27 |     except FileNotFoundError:
 28 |         pass  # File was already deleted by the test
 29 | 
 30 | 
 31 | class TestResourceManager:
 32 |     """Test ResourceManager functionality."""
 33 | 
 34 |     def test_add_resource(self, temp_file: Path):
 35 |         """Test adding a resource."""
 36 |         manager = ResourceManager()
 37 |         resource = FileResource(
 38 |             uri=FileUrl(f"file://{temp_file}"),
 39 |             name="test",
 40 |             path=temp_file,
 41 |         )
 42 |         added = manager.add_resource(resource)
 43 |         assert added == resource
 44 |         assert manager.list_resources() == [resource]
 45 | 
 46 |     def test_add_duplicate_resource(self, temp_file: Path):
 47 |         """Test adding the same resource twice."""
 48 |         manager = ResourceManager()
 49 |         resource = FileResource(
 50 |             uri=FileUrl(f"file://{temp_file}"),
 51 |             name="test",
 52 |             path=temp_file,
 53 |         )
 54 |         first = manager.add_resource(resource)
 55 |         second = manager.add_resource(resource)
 56 |         assert first == second
 57 |         assert manager.list_resources() == [resource]
 58 | 
 59 |     def test_warn_on_duplicate_resources(self, temp_file: Path, caplog):
 60 |         """Test warning on duplicate resources."""
 61 |         manager = ResourceManager()
 62 |         resource = FileResource(
 63 |             uri=FileUrl(f"file://{temp_file}"),
 64 |             name="test",
 65 |             path=temp_file,
 66 |         )
 67 |         manager.add_resource(resource)
 68 |         manager.add_resource(resource)
 69 |         assert "Resource already exists" in caplog.text
 70 | 
 71 |     def test_disable_warn_on_duplicate_resources(self, temp_file: Path, caplog):
 72 |         """Test disabling warning on duplicate resources."""
 73 |         manager = ResourceManager(warn_on_duplicate_resources=False)
 74 |         resource = FileResource(
 75 |             uri=FileUrl(f"file://{temp_file}"),
 76 |             name="test",
 77 |             path=temp_file,
 78 |         )
 79 |         manager.add_resource(resource)
 80 |         manager.add_resource(resource)
 81 |         assert "Resource already exists" not in caplog.text
 82 | 
 83 |     async def test_get_resource(self, temp_file: Path):
 84 |         """Test getting a resource by URI."""
 85 |         manager = ResourceManager()
 86 |         resource = FileResource(
 87 |             uri=FileUrl(f"file://{temp_file}"),
 88 |             name="test",
 89 |             path=temp_file,
 90 |         )
 91 |         manager.add_resource(resource)
 92 |         retrieved = await manager.get_resource(resource.uri)
 93 |         assert retrieved == resource
 94 | 
 95 |     async def test_get_resource_from_template(self):
 96 |         """Test getting a resource through a template."""
 97 |         manager = ResourceManager()
 98 | 
 99 |         def greet(name: str) -> str:
100 |             return f"Hello, {name}!"
101 | 
102 |         template = ResourceTemplate.from_function(
103 |             fn=greet,
104 |             uri_template="greet://{name}",
105 |             name="greeter",
106 |         )
107 |         manager._templates[template.uri_template] = template
108 | 
109 |         resource = await manager.get_resource(AnyUrl("greet://world"))
110 |         assert isinstance(resource, FunctionResource)
111 |         content = await resource.read()
112 |         assert content == "Hello, world!"
113 | 
114 |     async def test_get_unknown_resource(self):
115 |         """Test getting a non-existent resource."""
116 |         manager = ResourceManager()
117 |         with pytest.raises(ValueError, match="Unknown resource"):
118 |             await manager.get_resource(AnyUrl("unknown://test"))
119 | 
120 |     def test_list_resources(self, temp_file: Path):
121 |         """Test listing all resources."""
122 |         manager = ResourceManager()
123 |         resource1 = FileResource(
124 |             uri=FileUrl(f"file://{temp_file}"),
125 |             name="test1",
126 |             path=temp_file,
127 |         )
128 |         resource2 = FileResource(
129 |             uri=FileUrl(f"file://{temp_file}2"),
130 |             name="test2",
131 |             path=temp_file,
132 |         )
133 |         manager.add_resource(resource1)
134 |         manager.add_resource(resource2)
135 |         resources = manager.list_resources()
136 |         assert len(resources) == 2
137 |         assert resources == [resource1, resource2]
138 | 


--------------------------------------------------------------------------------
/tests/resources/test_resource_template.py:
--------------------------------------------------------------------------------
  1 | import json
  2 | import pytest
  3 | from pydantic import BaseModel
  4 | 
  5 | from fastmcp.resources import FunctionResource, ResourceTemplate
  6 | 
  7 | 
  8 | class TestResourceTemplate:
  9 |     """Test ResourceTemplate functionality."""
 10 | 
 11 |     def test_template_creation(self):
 12 |         """Test creating a template from a function."""
 13 | 
 14 |         def my_func(key: str, value: int) -> dict:
 15 |             return {"key": key, "value": value}
 16 | 
 17 |         template = ResourceTemplate.from_function(
 18 |             fn=my_func,
 19 |             uri_template="test://{key}/{value}",
 20 |             name="test",
 21 |         )
 22 |         assert template.uri_template == "test://{key}/{value}"
 23 |         assert template.name == "test"
 24 |         assert template.mime_type == "text/plain"  # default
 25 |         test_input = {"key": "test", "value": 42}
 26 |         assert template.fn(**test_input) == my_func(**test_input)
 27 | 
 28 |     def test_template_matches(self):
 29 |         """Test matching URIs against a template."""
 30 | 
 31 |         def my_func(key: str, value: int) -> dict:
 32 |             return {"key": key, "value": value}
 33 | 
 34 |         template = ResourceTemplate.from_function(
 35 |             fn=my_func,
 36 |             uri_template="test://{key}/{value}",
 37 |             name="test",
 38 |         )
 39 | 
 40 |         # Valid match
 41 |         params = template.matches("test://foo/123")
 42 |         assert params == {"key": "foo", "value": "123"}
 43 | 
 44 |         # No match
 45 |         assert template.matches("test://foo") is None
 46 |         assert template.matches("other://foo/123") is None
 47 | 
 48 |     async def test_create_resource(self):
 49 |         """Test creating a resource from a template."""
 50 | 
 51 |         def my_func(key: str, value: int) -> dict:
 52 |             return {"key": key, "value": value}
 53 | 
 54 |         template = ResourceTemplate.from_function(
 55 |             fn=my_func,
 56 |             uri_template="test://{key}/{value}",
 57 |             name="test",
 58 |         )
 59 | 
 60 |         resource = await template.create_resource(
 61 |             "test://foo/123",
 62 |             {"key": "foo", "value": 123},
 63 |         )
 64 | 
 65 |         assert isinstance(resource, FunctionResource)
 66 |         content = await resource.read()
 67 |         assert isinstance(content, str)
 68 |         data = json.loads(content)
 69 |         assert data == {"key": "foo", "value": 123}
 70 | 
 71 |     async def test_template_error(self):
 72 |         """Test error handling in template resource creation."""
 73 | 
 74 |         def failing_func(x: str) -> str:
 75 |             raise ValueError("Test error")
 76 | 
 77 |         template = ResourceTemplate.from_function(
 78 |             fn=failing_func,
 79 |             uri_template="fail://{x}",
 80 |             name="fail",
 81 |         )
 82 | 
 83 |         with pytest.raises(ValueError, match="Error creating resource from template"):
 84 |             await template.create_resource("fail://test", {"x": "test"})
 85 | 
 86 |     async def test_async_text_resource(self):
 87 |         """Test creating a text resource from async function."""
 88 | 
 89 |         async def greet(name: str) -> str:
 90 |             return f"Hello, {name}!"
 91 | 
 92 |         template = ResourceTemplate.from_function(
 93 |             fn=greet,
 94 |             uri_template="greet://{name}",
 95 |             name="greeter",
 96 |         )
 97 | 
 98 |         resource = await template.create_resource(
 99 |             "greet://world",
100 |             {"name": "world"},
101 |         )
102 | 
103 |         assert isinstance(resource, FunctionResource)
104 |         content = await resource.read()
105 |         assert content == "Hello, world!"
106 | 
107 |     async def test_async_binary_resource(self):
108 |         """Test creating a binary resource from async function."""
109 | 
110 |         async def get_bytes(value: str) -> bytes:
111 |             return value.encode()
112 | 
113 |         template = ResourceTemplate.from_function(
114 |             fn=get_bytes,
115 |             uri_template="bytes://{value}",
116 |             name="bytes",
117 |         )
118 | 
119 |         resource = await template.create_resource(
120 |             "bytes://test",
121 |             {"value": "test"},
122 |         )
123 | 
124 |         assert isinstance(resource, FunctionResource)
125 |         content = await resource.read()
126 |         assert content == b"test"
127 | 
128 |     async def test_basemodel_conversion(self):
129 |         """Test handling of BaseModel types."""
130 | 
131 |         class MyModel(BaseModel):
132 |             key: str
133 |             value: int
134 | 
135 |         def get_data(key: str, value: int) -> MyModel:
136 |             return MyModel(key=key, value=value)
137 | 
138 |         template = ResourceTemplate.from_function(
139 |             fn=get_data,
140 |             uri_template="test://{key}/{value}",
141 |             name="test",
142 |         )
143 | 
144 |         resource = await template.create_resource(
145 |             "test://foo/123",
146 |             {"key": "foo", "value": 123},
147 |         )
148 | 
149 |         assert isinstance(resource, FunctionResource)
150 |         content = await resource.read()
151 |         assert isinstance(content, str)
152 |         data = json.loads(content)
153 |         assert data == {"key": "foo", "value": 123}
154 | 
155 |     async def test_custom_type_conversion(self):
156 |         """Test handling of custom types."""
157 | 
158 |         class CustomData:
159 |             def __init__(self, value: str):
160 |                 self.value = value
161 | 
162 |             def __str__(self) -> str:
163 |                 return self.value
164 | 
165 |         def get_data(value: str) -> CustomData:
166 |             return CustomData(value)
167 | 
168 |         template = ResourceTemplate.from_function(
169 |             fn=get_data,
170 |             uri_template="test://{value}",
171 |             name="test",
172 |         )
173 | 
174 |         resource = await template.create_resource(
175 |             "test://hello",
176 |             {"value": "hello"},
177 |         )
178 | 
179 |         assert isinstance(resource, FunctionResource)
180 |         content = await resource.read()
181 |         assert content == "hello"
182 | 


--------------------------------------------------------------------------------
/tests/resources/test_resources.py:
--------------------------------------------------------------------------------
  1 | import pytest
  2 | from pydantic import AnyUrl
  3 | 
  4 | from fastmcp.resources import FunctionResource, Resource
  5 | 
  6 | 
  7 | class TestResourceValidation:
  8 |     """Test base Resource validation."""
  9 | 
 10 |     def test_resource_uri_validation(self):
 11 |         """Test URI validation."""
 12 | 
 13 |         def dummy_func() -> str:
 14 |             return "data"
 15 | 
 16 |         # Valid URI
 17 |         resource = FunctionResource(
 18 |             uri=AnyUrl("http://example.com/data"),
 19 |             name="test",
 20 |             fn=dummy_func,
 21 |         )
 22 |         assert str(resource.uri) == "http://example.com/data"
 23 | 
 24 |         # Missing protocol
 25 |         with pytest.raises(ValueError, match="Input should be a valid URL"):
 26 |             FunctionResource(
 27 |                 uri=AnyUrl("invalid"),
 28 |                 name="test",
 29 |                 fn=dummy_func,
 30 |             )
 31 | 
 32 |         # Missing host
 33 |         with pytest.raises(ValueError, match="Input should be a valid URL"):
 34 |             FunctionResource(
 35 |                 uri=AnyUrl("http://"),
 36 |                 name="test",
 37 |                 fn=dummy_func,
 38 |             )
 39 | 
 40 |     def test_resource_name_from_uri(self):
 41 |         """Test name is extracted from URI if not provided."""
 42 | 
 43 |         def dummy_func() -> str:
 44 |             return "data"
 45 | 
 46 |         resource = FunctionResource(
 47 |             uri=AnyUrl("resource://my-resource"),
 48 |             fn=dummy_func,
 49 |         )
 50 |         assert resource.name == "resource://my-resource"
 51 | 
 52 |     def test_resource_name_validation(self):
 53 |         """Test name validation."""
 54 | 
 55 |         def dummy_func() -> str:
 56 |             return "data"
 57 | 
 58 |         # Must provide either name or URI
 59 |         with pytest.raises(ValueError, match="Either name or uri must be provided"):
 60 |             FunctionResource(
 61 |                 fn=dummy_func,
 62 |             )
 63 | 
 64 |         # Explicit name takes precedence over URI
 65 |         resource = FunctionResource(
 66 |             uri=AnyUrl("resource://uri-name"),
 67 |             name="explicit-name",
 68 |             fn=dummy_func,
 69 |         )
 70 |         assert resource.name == "explicit-name"
 71 | 
 72 |     def test_resource_mime_type(self):
 73 |         """Test mime type handling."""
 74 | 
 75 |         def dummy_func() -> str:
 76 |             return "data"
 77 | 
 78 |         # Default mime type
 79 |         resource = FunctionResource(
 80 |             uri=AnyUrl("resource://test"),
 81 |             fn=dummy_func,
 82 |         )
 83 |         assert resource.mime_type == "text/plain"
 84 | 
 85 |         # Custom mime type
 86 |         resource = FunctionResource(
 87 |             uri=AnyUrl("resource://test"),
 88 |             fn=dummy_func,
 89 |             mime_type="application/json",
 90 |         )
 91 |         assert resource.mime_type == "application/json"
 92 | 
 93 |     async def test_resource_read_abstract(self):
 94 |         """Test that Resource.read() is abstract."""
 95 | 
 96 |         class ConcreteResource(Resource):
 97 |             pass
 98 | 
 99 |         with pytest.raises(TypeError, match="abstract method"):
100 |             ConcreteResource(uri=AnyUrl("test://test"), name="test")  # type: ignore
101 | 


--------------------------------------------------------------------------------
/tests/servers/__init__.py:
--------------------------------------------------------------------------------
https://raw.githubusercontent.com/jlowin/fastmcp/80c328b3dc0b949f010456ee0e85cc5c90e3305f/tests/servers/__init__.py


--------------------------------------------------------------------------------
/tests/servers/test_file_server.py:
--------------------------------------------------------------------------------
  1 | import json
  2 | from fastmcp import FastMCP
  3 | import pytest
  4 | from pathlib import Path
  5 | 
  6 | 
  7 | @pytest.fixture()
  8 | def test_dir(tmp_path_factory) -> Path:
  9 |     """Create a temporary directory with test files."""
 10 |     tmp = tmp_path_factory.mktemp("test_files")
 11 | 
 12 |     # Create test files
 13 |     (tmp / "example.py").write_text("print('hello world')")
 14 |     (tmp / "readme.md").write_text("# Test Directory\nThis is a test.")
 15 |     (tmp / "config.json").write_text('{"test": true}')
 16 | 
 17 |     return tmp
 18 | 
 19 | 
 20 | @pytest.fixture
 21 | def mcp() -> FastMCP:
 22 |     mcp = FastMCP()
 23 | 
 24 |     return mcp
 25 | 
 26 | 
 27 | @pytest.fixture(autouse=True)
 28 | def resources(mcp: FastMCP, test_dir: Path) -> FastMCP:
 29 |     @mcp.resource("dir://test_dir")
 30 |     def list_test_dir() -> list[str]:
 31 |         """List the files in the test directory"""
 32 |         return [str(f) for f in test_dir.iterdir()]
 33 | 
 34 |     @mcp.resource("file://test_dir/example.py")
 35 |     def read_example_py() -> str:
 36 |         """Read the example.py file"""
 37 |         try:
 38 |             return (test_dir / "example.py").read_text()
 39 |         except FileNotFoundError:
 40 |             return "File not found"
 41 | 
 42 |     @mcp.resource("file://test_dir/readme.md")
 43 |     def read_readme_md() -> str:
 44 |         """Read the readme.md file"""
 45 |         try:
 46 |             return (test_dir / "readme.md").read_text()
 47 |         except FileNotFoundError:
 48 |             return "File not found"
 49 | 
 50 |     @mcp.resource("file://test_dir/config.json")
 51 |     def read_config_json() -> str:
 52 |         """Read the config.json file"""
 53 |         try:
 54 |             return (test_dir / "config.json").read_text()
 55 |         except FileNotFoundError:
 56 |             return "File not found"
 57 | 
 58 |     return mcp
 59 | 
 60 | 
 61 | @pytest.fixture(autouse=True)
 62 | def tools(mcp: FastMCP, test_dir: Path) -> FastMCP:
 63 |     @mcp.tool()
 64 |     def delete_file(path: str) -> bool:
 65 |         # ensure path is in test_dir
 66 |         if Path(path).resolve().parent != test_dir:
 67 |             raise ValueError(f"Path must be in test_dir: {path}")
 68 |         Path(path).unlink()
 69 |         return True
 70 | 
 71 |     return mcp
 72 | 
 73 | 
 74 | async def test_list_resources(mcp: FastMCP):
 75 |     resources = await mcp.list_resources()
 76 |     assert len(resources) == 4
 77 | 
 78 |     assert [str(r.uri) for r in resources] == [
 79 |         "dir://test_dir",
 80 |         "file://test_dir/example.py",
 81 |         "file://test_dir/readme.md",
 82 |         "file://test_dir/config.json",
 83 |     ]
 84 | 
 85 | 
 86 | async def test_read_resource_dir(mcp: FastMCP):
 87 |     files = await mcp.read_resource("dir://test_dir")
 88 |     files = json.loads(files)
 89 | 
 90 |     assert sorted([Path(f).name for f in files]) == [
 91 |         "config.json",
 92 |         "example.py",
 93 |         "readme.md",
 94 |     ]
 95 | 
 96 | 
 97 | async def test_read_resource_file(mcp: FastMCP):
 98 |     result = await mcp.read_resource("file://test_dir/example.py")
 99 |     assert result == "print('hello world')"
100 | 
101 | 
102 | async def test_delete_file(mcp: FastMCP, test_dir: Path):
103 |     await mcp.call_tool(
104 |         "delete_file", arguments=dict(path=str(test_dir / "example.py"))
105 |     )
106 |     assert not (test_dir / "example.py").exists()
107 | 
108 | 
109 | async def test_delete_file_and_check_resources(mcp: FastMCP, test_dir: Path):
110 |     await mcp.call_tool(
111 |         "delete_file", arguments=dict(path=str(test_dir / "example.py"))
112 |     )
113 |     result = await mcp.read_resource("file://test_dir/example.py")
114 |     assert result == "File not found"
115 | 


--------------------------------------------------------------------------------
/tests/test_cli.py:
--------------------------------------------------------------------------------
  1 | """Tests for the FastMCP CLI."""
  2 | 
  3 | import json
  4 | import sys
  5 | from pathlib import Path
  6 | from unittest.mock import call, patch
  7 | 
  8 | import pytest
  9 | from typer.testing import CliRunner
 10 | 
 11 | from fastmcp.cli.cli import _parse_env_var, _parse_file_path, app
 12 | 
 13 | 
 14 | @pytest.fixture
 15 | def mock_config(tmp_path):
 16 |     """Create a mock Claude config file."""
 17 |     config = {"mcpServers": {}}
 18 |     config_file = tmp_path / "claude_desktop_config.json"
 19 |     config_file.write_text(json.dumps(config))
 20 |     return config_file
 21 | 
 22 | 
 23 | @pytest.fixture
 24 | def server_file(tmp_path):
 25 |     """Create a server file."""
 26 |     server_file = tmp_path / "server.py"
 27 |     server_file.write_text(
 28 |         """from fastmcp import FastMCP
 29 | mcp = FastMCP("test")
 30 | """
 31 |     )
 32 |     return server_file
 33 | 
 34 | 
 35 | @pytest.fixture
 36 | def mock_env_file(tmp_path):
 37 |     """Create a mock .env file."""
 38 |     env_file = tmp_path / ".env"
 39 |     env_file.write_text("FOO=bar\nBAZ=123")
 40 |     return env_file
 41 | 
 42 | 
 43 | def test_parse_env_var():
 44 |     """Test parsing environment variables."""
 45 |     assert _parse_env_var("FOO=bar") == ("FOO", "bar")
 46 |     assert _parse_env_var("FOO=") == ("FOO", "")
 47 |     assert _parse_env_var("FOO=bar baz") == ("FOO", "bar baz")
 48 |     assert _parse_env_var("FOO = bar ") == ("FOO", "bar")
 49 | 
 50 |     with pytest.raises(SystemExit):
 51 |         _parse_env_var("invalid")
 52 | 
 53 | 
 54 | @pytest.mark.parametrize(
 55 |     "args,expected_env",
 56 |     [
 57 |         # Basic env var
 58 |         (
 59 |             ["--env-var", "FOO=bar"],
 60 |             {"FOO": "bar"},
 61 |         ),
 62 |         # Multiple env vars
 63 |         (
 64 |             ["--env-var", "FOO=bar", "--env-var", "BAZ=123"],
 65 |             {"FOO": "bar", "BAZ": "123"},
 66 |         ),
 67 |         # Env var with spaces
 68 |         (
 69 |             ["--env-var", "FOO=bar baz"],
 70 |             {"FOO": "bar baz"},
 71 |         ),
 72 |     ],
 73 | )
 74 | def test_install_with_env_vars(mock_config, server_file, args, expected_env):
 75 |     """Test installing with environment variables."""
 76 |     runner = CliRunner()
 77 | 
 78 |     with patch("fastmcp.cli.claude.get_claude_config_path") as mock_config_path:
 79 |         mock_config_path.return_value = mock_config.parent
 80 | 
 81 |         result = runner.invoke(
 82 |             app,
 83 |             ["install", str(server_file)] + args,
 84 |         )
 85 | 
 86 |         assert result.exit_code == 0
 87 | 
 88 |         # Read the config file and check env vars
 89 |         config = json.loads(mock_config.read_text())
 90 |         assert "mcpServers" in config
 91 |         assert len(config["mcpServers"]) == 1
 92 |         server = next(iter(config["mcpServers"].values()))
 93 |         assert server["env"] == expected_env
 94 | 
 95 | 
 96 | def test_parse_file_path_windows_drive():
 97 |     """Test parsing a Windows file path with a drive letter."""
 98 |     file_spec = r"C:\path\to\file.txt"
 99 |     with (
100 |         patch("pathlib.Path.exists", return_value=True),
101 |         patch("pathlib.Path.is_file", return_value=True),
102 |     ):
103 |         file_path, server_object = _parse_file_path(file_spec)
104 |         assert file_path == Path(r"C:\path\to\file.txt").resolve()
105 |         assert server_object is None
106 | 
107 | 
108 | def test_parse_file_path_with_object():
109 |     """Test parsing a file path with an object specification."""
110 |     file_spec = "/path/to/file.txt:object"
111 |     with patch("sys.exit") as mock_exit:
112 |         _parse_file_path(file_spec)
113 | 
114 |         # Check that sys.exit was called twice with code 1
115 |         assert mock_exit.call_count == 2
116 |         mock_exit.assert_has_calls([call(1), call(1)])
117 | 
118 | 
119 | def test_parse_file_path_windows_with_object():
120 |     """Test parsing a Windows file path with an object specification."""
121 |     file_spec = r"C:\path\to\file.txt:object"
122 |     with (
123 |         patch("pathlib.Path.exists", return_value=True),
124 |         patch("pathlib.Path.is_file", return_value=True),
125 |     ):
126 |         file_path, server_object = _parse_file_path(file_spec)
127 |         assert file_path == Path(r"C:\path\to\file.txt").resolve()
128 |         assert server_object == "object"
129 | 
130 | 
131 | def test_install_with_env_file(mock_config, server_file, mock_env_file):
132 |     """Test installing with environment variables from a file."""
133 |     runner = CliRunner()
134 | 
135 |     with patch("fastmcp.cli.claude.get_claude_config_path") as mock_config_path:
136 |         mock_config_path.return_value = mock_config.parent
137 | 
138 |         result = runner.invoke(
139 |             app,
140 |             ["install", str(server_file), "--env-file", str(mock_env_file)],
141 |         )
142 | 
143 |         assert result.exit_code == 0
144 | 
145 |         # Read the config file and check env vars
146 |         config = json.loads(mock_config.read_text())
147 |         assert "mcpServers" in config
148 |         assert len(config["mcpServers"]) == 1
149 |         server = next(iter(config["mcpServers"].values()))
150 |         assert server["env"] == {"FOO": "bar", "BAZ": "123"}
151 | 
152 | 
153 | def test_install_preserves_existing_env_vars(mock_config, server_file):
154 |     """Test that installing preserves existing environment variables."""
155 |     # Set up initial config with env vars
156 |     config = {
157 |         "mcpServers": {
158 |             "test": {
159 |                 "command": "uv",
160 |                 "args": [
161 |                     "run",
162 |                     "--with",
163 |                     "fastmcp",
164 |                     "fastmcp",
165 |                     "run",
166 |                     str(server_file),
167 |                 ],
168 |                 "env": {"FOO": "bar", "BAZ": "123"},
169 |             }
170 |         }
171 |     }
172 |     mock_config.write_text(json.dumps(config))
173 | 
174 |     runner = CliRunner()
175 | 
176 |     with patch("fastmcp.cli.claude.get_claude_config_path") as mock_config_path:
177 |         mock_config_path.return_value = mock_config.parent
178 | 
179 |         # Install with a new env var
180 |         result = runner.invoke(
181 |             app,
182 |             ["install", str(server_file), "--env-var", "NEW=value"],
183 |         )
184 | 
185 |         assert result.exit_code == 0
186 | 
187 |         # Read the config file and check env vars are preserved
188 |         config = json.loads(mock_config.read_text())
189 |         server = next(iter(config["mcpServers"].values()))
190 |         assert server["env"] == {"FOO": "bar", "BAZ": "123", "NEW": "value"}
191 | 
192 | 
193 | def test_install_updates_existing_env_vars(mock_config, server_file):
194 |     """Test that installing updates existing environment variables."""
195 |     # Set up initial config with env vars
196 |     config = {
197 |         "mcpServers": {
198 |             "test": {
199 |                 "command": "uv",
200 |                 "args": [
201 |                     "run",
202 |                     "--with",
203 |                     "fastmcp",
204 |                     "fastmcp",
205 |                     "run",
206 |                     str(server_file),
207 |                 ],
208 |                 "env": {"FOO": "bar", "BAZ": "123"},
209 |             }
210 |         }
211 |     }
212 |     mock_config.write_text(json.dumps(config))
213 | 
214 |     runner = CliRunner()
215 | 
216 |     with patch("fastmcp.cli.claude.get_claude_config_path") as mock_config_path:
217 |         mock_config_path.return_value = mock_config.parent
218 | 
219 |         # Update an existing env var
220 |         result = runner.invoke(
221 |             app,
222 |             ["install", str(server_file), "--env-var", "FOO=newvalue"],
223 |         )
224 | 
225 |         assert result.exit_code == 0
226 | 
227 |         # Read the config file and check env var was updated
228 |         config = json.loads(mock_config.read_text())
229 |         server = next(iter(config["mcpServers"].values()))
230 |         assert server["env"] == {"FOO": "newvalue", "BAZ": "123"}
231 | 
232 | 
233 | def test_server_dependencies(mock_config, server_file):
234 |     """Test that server dependencies are correctly handled."""
235 |     # Create a server file with dependencies
236 |     server_file = server_file.parent / "server_with_deps.py"
237 |     server_file.write_text(
238 |         """from fastmcp import FastMCP
239 | mcp = FastMCP("test", dependencies=["pandas", "numpy"])
240 | """
241 |     )
242 | 
243 |     runner = CliRunner()
244 | 
245 |     with patch("fastmcp.cli.claude.get_claude_config_path") as mock_config_path:
246 |         mock_config_path.return_value = mock_config.parent
247 | 
248 |         result = runner.invoke(app, ["install", str(server_file)])
249 | 
250 |         assert result.exit_code == 0
251 | 
252 |         # Read the config file and check dependencies were added as --with args
253 |         config = json.loads(mock_config.read_text())
254 |         server = next(iter(config["mcpServers"].values()))
255 |         assert "--with" in server["args"]
256 |         assert "pandas" in server["args"]
257 |         assert "numpy" in server["args"]
258 | 
259 | 
260 | def test_server_dependencies_empty(mock_config, server_file):
261 |     """Test that server with no dependencies works correctly."""
262 |     runner = CliRunner()
263 | 
264 |     with patch("fastmcp.cli.claude.get_claude_config_path") as mock_config_path:
265 |         mock_config_path.return_value = mock_config.parent
266 | 
267 |         result = runner.invoke(app, ["install", str(server_file)])
268 | 
269 |         assert result.exit_code == 0
270 | 
271 |         # Read the config file and check only fastmcp is in --with args
272 |         config = json.loads(mock_config.read_text())
273 |         server = next(iter(config["mcpServers"].values()))
274 |         assert server["args"].count("--with") == 1
275 |         assert "fastmcp" in server["args"]
276 | 
277 | 
278 | def test_dev_with_dependencies(mock_config, server_file):
279 |     """Test that dev command handles dependencies correctly."""
280 |     server_file = server_file.parent / "server_with_deps.py"
281 |     server_file.write_text(
282 |         """from fastmcp import FastMCP
283 | mcp = FastMCP("test", dependencies=["pandas", "numpy"])
284 | """
285 |     )
286 | 
287 |     runner = CliRunner()
288 | 
289 |     with patch("subprocess.run") as mock_run:
290 |         mock_run.return_value.returncode = 0
291 |         result = runner.invoke(app, ["dev", str(server_file)])
292 |         assert result.exit_code == 0
293 | 
294 |         if sys.platform == "win32":
295 |             # On Windows, expect two calls
296 |             assert mock_run.call_count == 2
297 |             assert mock_run.call_args_list[0] == call(
298 |                 ["npx.cmd", "--version"], check=True, capture_output=True, shell=True
299 |             )
300 | 
301 |             # get the actual command and expected command without dependencies
302 |             actual_cmd = mock_run.call_args_list[1][0][0]
303 |             expected_start = [
304 |                 "npx.cmd",
305 |                 "@modelcontextprotocol/inspector",
306 |                 "uv",
307 |                 "run",
308 |                 "--with",
309 |                 "fastmcp",
310 |             ]
311 |             expected_end = ["fastmcp", "run", str(server_file)]
312 | 
313 |             # verify start and end of command
314 |             assert actual_cmd[: len(expected_start)] == expected_start
315 |             assert actual_cmd[-len(expected_end) :] == expected_end
316 | 
317 |             # verify dependencies are present (order-independent)
318 |             deps_section = actual_cmd[len(expected_start) : -len(expected_end)]
319 |             assert all(
320 |                 x in deps_section for x in ["--with", "numpy", "--with", "pandas"]
321 |             )
322 | 
323 |             # Verify subprocess call kwargs, allowing for environment variables
324 |             call_kwargs = mock_run.call_args_list[1][1]
325 |             assert call_kwargs["check"] is True
326 |             assert call_kwargs["shell"] is True
327 |             assert isinstance(call_kwargs["env"], dict)
328 |         else:
329 |             # same verification for unix, just with different command prefix
330 |             actual_cmd = mock_run.call_args_list[0][0][0]
331 |             expected_start = [
332 |                 "npx",
333 |                 "@modelcontextprotocol/inspector",
334 |                 "uv",
335 |                 "run",
336 |                 "--with",
337 |                 "fastmcp",
338 |             ]
339 |             expected_end = ["fastmcp", "run", str(server_file)]
340 | 
341 |             assert actual_cmd[: len(expected_start)] == expected_start
342 |             assert actual_cmd[-len(expected_end) :] == expected_end
343 | 
344 |             deps_section = actual_cmd[len(expected_start) : -len(expected_end)]
345 |             assert all(
346 |                 x in deps_section for x in ["--with", "numpy", "--with", "pandas"]
347 |             )
348 | 
349 |             # Verify subprocess call kwargs, allowing for environment variables
350 |             call_kwargs = mock_run.call_args_list[0][1]
351 |             assert call_kwargs["check"] is True
352 |             assert call_kwargs["shell"] is False
353 |             assert isinstance(call_kwargs["env"], dict)
354 | 
355 | 
356 | def test_run_with_dependencies(mock_config, server_file):
357 |     """Test that run command does not handle dependencies."""
358 |     # Create a server file with dependencies
359 |     server_file = server_file.parent / "server_with_deps.py"
360 |     server_file.write_text(
361 |         """from fastmcp import FastMCP
362 | mcp = FastMCP("test", dependencies=["pandas", "numpy"])
363 | 
364 | if __name__ == "__main__":
365 |     mcp.run()
366 | """
367 |     )
368 | 
369 |     runner = CliRunner()
370 | 
371 |     with patch("subprocess.run") as mock_run:
372 |         result = runner.invoke(app, ["run", str(server_file)])
373 |         assert result.exit_code == 0
374 | 
375 |         # Run command should not call subprocess.run
376 |         mock_run.assert_not_called()
377 | 


--------------------------------------------------------------------------------
/tests/test_func_metadata.py:
--------------------------------------------------------------------------------
  1 | from typing import Annotated
  2 | 
  3 | import annotated_types
  4 | import pytest
  5 | from pydantic import BaseModel, Field
  6 | 
  7 | from fastmcp.utilities.func_metadata import func_metadata
  8 | 
  9 | 
 10 | class SomeInputModelA(BaseModel):
 11 |     pass
 12 | 
 13 | 
 14 | class SomeInputModelB(BaseModel):
 15 |     class InnerModel(BaseModel):
 16 |         x: int
 17 | 
 18 |     how_many_shrimp: Annotated[int, Field(description="How many shrimp in the tank???")]
 19 |     ok: InnerModel
 20 |     y: None
 21 | 
 22 | 
 23 | def complex_arguments_fn(
 24 |     an_int: int,
 25 |     must_be_none: None,
 26 |     must_be_none_dumb_annotation: Annotated[None, "blah"],
 27 |     list_of_ints: list[int],
 28 |     # list[str] | str is an interesting case because if it comes in as JSON like
 29 |     # "[\"a\", \"b\"]" then it will be naively parsed as a string.
 30 |     list_str_or_str: list[str] | str,
 31 |     an_int_annotated_with_field: Annotated[
 32 |         int, Field(description="An int with a field")
 33 |     ],
 34 |     an_int_annotated_with_field_and_others: Annotated[
 35 |         int,
 36 |         str,  # Should be ignored, really
 37 |         Field(description="An int with a field"),
 38 |         annotated_types.Gt(1),
 39 |     ],
 40 |     an_int_annotated_with_junk: Annotated[
 41 |         int,
 42 |         "123",
 43 |         456,
 44 |     ],
 45 |     field_with_default_via_field_annotation_before_nondefault_arg: Annotated[
 46 |         int, Field(1)
 47 |     ],
 48 |     unannotated,
 49 |     my_model_a: SomeInputModelA,
 50 |     my_model_a_forward_ref: "SomeInputModelA",
 51 |     my_model_b: SomeInputModelB,
 52 |     an_int_annotated_with_field_default: Annotated[
 53 |         int,
 54 |         Field(1, description="An int with a field"),
 55 |     ],
 56 |     unannotated_with_default=5,
 57 |     my_model_a_with_default: SomeInputModelA = SomeInputModelA(),  # noqa: B008
 58 |     an_int_with_default: int = 1,
 59 |     must_be_none_with_default: None = None,
 60 |     an_int_with_equals_field: int = Field(1, ge=0),
 61 |     int_annotated_with_default: Annotated[int, Field(description="hey")] = 5,
 62 | ) -> str:
 63 |     _ = (
 64 |         an_int,
 65 |         must_be_none,
 66 |         must_be_none_dumb_annotation,
 67 |         list_of_ints,
 68 |         list_str_or_str,
 69 |         an_int_annotated_with_field,
 70 |         an_int_annotated_with_field_and_others,
 71 |         an_int_annotated_with_junk,
 72 |         field_with_default_via_field_annotation_before_nondefault_arg,
 73 |         unannotated,
 74 |         an_int_annotated_with_field_default,
 75 |         unannotated_with_default,
 76 |         my_model_a,
 77 |         my_model_a_forward_ref,
 78 |         my_model_b,
 79 |         my_model_a_with_default,
 80 |         an_int_with_default,
 81 |         must_be_none_with_default,
 82 |         an_int_with_equals_field,
 83 |         int_annotated_with_default,
 84 |     )
 85 |     return "ok!"
 86 | 
 87 | 
 88 | async def test_complex_function_runtime_arg_validation_non_json():
 89 |     """Test that basic non-JSON arguments are validated correctly"""
 90 |     meta = func_metadata(complex_arguments_fn)
 91 | 
 92 |     # Test with minimum required arguments
 93 |     result = await meta.call_fn_with_arg_validation(
 94 |         complex_arguments_fn,
 95 |         fn_is_async=False,
 96 |         arguments_to_validate={
 97 |             "an_int": 1,
 98 |             "must_be_none": None,
 99 |             "must_be_none_dumb_annotation": None,
100 |             "list_of_ints": [1, 2, 3],
101 |             "list_str_or_str": "hello",
102 |             "an_int_annotated_with_field": 42,
103 |             "an_int_annotated_with_field_and_others": 5,
104 |             "an_int_annotated_with_junk": 100,
105 |             "unannotated": "test",
106 |             "my_model_a": {},
107 |             "my_model_a_forward_ref": {},
108 |             "my_model_b": {"how_many_shrimp": 5, "ok": {"x": 1}, "y": None},
109 |         },
110 |         arguments_to_pass_directly=None,
111 |     )
112 |     assert result == "ok!"
113 | 
114 |     # Test with invalid types
115 |     with pytest.raises(ValueError):
116 |         await meta.call_fn_with_arg_validation(
117 |             complex_arguments_fn,
118 |             fn_is_async=False,
119 |             arguments_to_validate={"an_int": "not an int"},
120 |             arguments_to_pass_directly=None,
121 |         )
122 | 
123 | 
124 | async def test_complex_function_runtime_arg_validation_with_json():
125 |     """Test that JSON string arguments are parsed and validated correctly"""
126 |     meta = func_metadata(complex_arguments_fn)
127 | 
128 |     result = await meta.call_fn_with_arg_validation(
129 |         complex_arguments_fn,
130 |         fn_is_async=False,
131 |         arguments_to_validate={
132 |             "an_int": 1,
133 |             "must_be_none": None,
134 |             "must_be_none_dumb_annotation": None,
135 |             "list_of_ints": "[1, 2, 3]",  # JSON string
136 |             "list_str_or_str": '["a", "b", "c"]',  # JSON string
137 |             "an_int_annotated_with_field": 42,
138 |             "an_int_annotated_with_field_and_others": "5",  # JSON string
139 |             "an_int_annotated_with_junk": 100,
140 |             "unannotated": "test",
141 |             "my_model_a": "{}",  # JSON string
142 |             "my_model_a_forward_ref": "{}",  # JSON string
143 |             "my_model_b": '{"how_many_shrimp": 5, "ok": {"x": 1}, "y": null}',  # JSON string
144 |         },
145 |         arguments_to_pass_directly=None,
146 |     )
147 |     assert result == "ok!"
148 | 
149 | 
150 | def test_str_vs_list_str():
151 |     """Test handling of string vs list[str] type annotations.
152 | 
153 |     This is tricky as '"hello"' can be parsed as a JSON string or a Python string.
154 |     We want to make sure it's kept as a python string.
155 |     """
156 | 
157 |     def func_with_str_types(str_or_list: str | list[str]):
158 |         return str_or_list
159 | 
160 |     meta = func_metadata(func_with_str_types)
161 | 
162 |     # Test string input for union type
163 |     result = meta.pre_parse_json({"str_or_list": "hello"})
164 |     assert result["str_or_list"] == "hello"
165 | 
166 |     # Test string input that contains valid JSON for union type
167 |     # We want to see here that the JSON-vali string is NOT parsed as JSON, but rather
168 |     # kept as a raw string
169 |     result = meta.pre_parse_json({"str_or_list": '"hello"'})
170 |     assert result["str_or_list"] == '"hello"'
171 | 
172 |     # Test list input for union type
173 |     result = meta.pre_parse_json({"str_or_list": '["hello", "world"]'})
174 |     assert result["str_or_list"] == ["hello", "world"]
175 | 
176 | 
177 | def test_str_vs_int():
178 |     """
179 |     Test that string values are kept as strings even when they contain numbers,
180 |     while numbers are parsed correctly.
181 |     """
182 | 
183 |     def func_with_str_and_int(a: str, b: int):
184 |         return a
185 | 
186 |     meta = func_metadata(func_with_str_and_int)
187 |     result = meta.pre_parse_json({"a": "123", "b": 123})
188 |     assert result["a"] == "123"
189 |     assert result["b"] == 123
190 | 
191 | 
192 | def test_skip_names():
193 |     """Test that skipped parameters are not included in the model"""
194 | 
195 |     def func_with_many_params(
196 |         keep_this: int, skip_this: str, also_keep: float, also_skip: bool
197 |     ):
198 |         return keep_this, skip_this, also_keep, also_skip
199 | 
200 |     # Skip some parameters
201 |     meta = func_metadata(func_with_many_params, skip_names=["skip_this", "also_skip"])
202 | 
203 |     # Check model fields
204 |     assert "keep_this" in meta.arg_model.model_fields
205 |     assert "also_keep" in meta.arg_model.model_fields
206 |     assert "skip_this" not in meta.arg_model.model_fields
207 |     assert "also_skip" not in meta.arg_model.model_fields
208 | 
209 |     # Validate that we can call with only non-skipped parameters
210 |     model: BaseModel = meta.arg_model.model_validate({"keep_this": 1, "also_keep": 2.5})  # type: ignore
211 |     assert model.keep_this == 1  # type: ignore
212 |     assert model.also_keep == 2.5  # type: ignore
213 | 
214 | 
215 | async def test_lambda_function():
216 |     """Test lambda function schema and validation"""
217 |     fn = lambda x, y=5: x  # noqa: E731
218 |     meta = func_metadata(lambda x, y=5: x)
219 | 
220 |     # Test schema
221 |     assert meta.arg_model.model_json_schema() == {
222 |         "properties": {
223 |             "x": {"title": "x", "type": "string"},
224 |             "y": {"default": 5, "title": "y", "type": "string"},
225 |         },
226 |         "required": ["x"],
227 |         "title": "<lambda>Arguments",
228 |         "type": "object",
229 |     }
230 | 
231 |     async def check_call(args):
232 |         return await meta.call_fn_with_arg_validation(
233 |             fn,
234 |             fn_is_async=False,
235 |             arguments_to_validate=args,
236 |             arguments_to_pass_directly=None,
237 |         )
238 | 
239 |     # Basic calls
240 |     assert await check_call({"x": "hello"}) == "hello"
241 |     assert await check_call({"x": "hello", "y": "world"}) == "hello"
242 |     assert await check_call({"x": '"hello"'}) == '"hello"'
243 | 
244 |     # Missing required arg
245 |     with pytest.raises(ValueError):
246 |         await check_call({"y": "world"})
247 | 
248 | 
249 | def test_complex_function_json_schema():
250 |     meta = func_metadata(complex_arguments_fn)
251 |     assert meta.arg_model.model_json_schema() == {
252 |         "$defs": {
253 |             "InnerModel": {
254 |                 "properties": {"x": {"title": "X", "type": "integer"}},
255 |                 "required": ["x"],
256 |                 "title": "InnerModel",
257 |                 "type": "object",
258 |             },
259 |             "SomeInputModelA": {
260 |                 "properties": {},
261 |                 "title": "SomeInputModelA",
262 |                 "type": "object",
263 |             },
264 |             "SomeInputModelB": {
265 |                 "properties": {
266 |                     "how_many_shrimp": {
267 |                         "description": "How many shrimp in the tank???",
268 |                         "title": "How Many Shrimp",
269 |                         "type": "integer",
270 |                     },
271 |                     "ok": {"$ref": "#/$defs/InnerModel"},
272 |                     "y": {"title": "Y", "type": "null"},
273 |                 },
274 |                 "required": ["how_many_shrimp", "ok", "y"],
275 |                 "title": "SomeInputModelB",
276 |                 "type": "object",
277 |             },
278 |         },
279 |         "properties": {
280 |             "an_int": {"title": "An Int", "type": "integer"},
281 |             "must_be_none": {"title": "Must Be None", "type": "null"},
282 |             "must_be_none_dumb_annotation": {
283 |                 "title": "Must Be None Dumb Annotation",
284 |                 "type": "null",
285 |             },
286 |             "list_of_ints": {
287 |                 "items": {"type": "integer"},
288 |                 "title": "List Of Ints",
289 |                 "type": "array",
290 |             },
291 |             "list_str_or_str": {
292 |                 "anyOf": [
293 |                     {"items": {"type": "string"}, "type": "array"},
294 |                     {"type": "string"},
295 |                 ],
296 |                 "title": "List Str Or Str",
297 |             },
298 |             "an_int_annotated_with_field": {
299 |                 "description": "An int with a field",
300 |                 "title": "An Int Annotated With Field",
301 |                 "type": "integer",
302 |             },
303 |             "an_int_annotated_with_field_and_others": {
304 |                 "description": "An int with a field",
305 |                 "exclusiveMinimum": 1,
306 |                 "title": "An Int Annotated With Field And Others",
307 |                 "type": "integer",
308 |             },
309 |             "an_int_annotated_with_junk": {
310 |                 "title": "An Int Annotated With Junk",
311 |                 "type": "integer",
312 |             },
313 |             "field_with_default_via_field_annotation_before_nondefault_arg": {
314 |                 "default": 1,
315 |                 "title": "Field With Default Via Field Annotation Before Nondefault Arg",
316 |                 "type": "integer",
317 |             },
318 |             "unannotated": {"title": "unannotated", "type": "string"},
319 |             "my_model_a": {"$ref": "#/$defs/SomeInputModelA"},
320 |             "my_model_a_forward_ref": {"$ref": "#/$defs/SomeInputModelA"},
321 |             "my_model_b": {"$ref": "#/$defs/SomeInputModelB"},
322 |             "an_int_annotated_with_field_default": {
323 |                 "default": 1,
324 |                 "description": "An int with a field",
325 |                 "title": "An Int Annotated With Field Default",
326 |                 "type": "integer",
327 |             },
328 |             "unannotated_with_default": {
329 |                 "default": 5,
330 |                 "title": "unannotated_with_default",
331 |                 "type": "string",
332 |             },
333 |             "my_model_a_with_default": {
334 |                 "$ref": "#/$defs/SomeInputModelA",
335 |                 "default": {},
336 |             },
337 |             "an_int_with_default": {
338 |                 "default": 1,
339 |                 "title": "An Int With Default",
340 |                 "type": "integer",
341 |             },
342 |             "must_be_none_with_default": {
343 |                 "default": None,
344 |                 "title": "Must Be None With Default",
345 |                 "type": "null",
346 |             },
347 |             "an_int_with_equals_field": {
348 |                 "default": 1,
349 |                 "minimum": 0,
350 |                 "title": "An Int With Equals Field",
351 |                 "type": "integer",
352 |             },
353 |             "int_annotated_with_default": {
354 |                 "default": 5,
355 |                 "description": "hey",
356 |                 "title": "Int Annotated With Default",
357 |                 "type": "integer",
358 |             },
359 |         },
360 |         "required": [
361 |             "an_int",
362 |             "must_be_none",
363 |             "must_be_none_dumb_annotation",
364 |             "list_of_ints",
365 |             "list_str_or_str",
366 |             "an_int_annotated_with_field",
367 |             "an_int_annotated_with_field_and_others",
368 |             "an_int_annotated_with_junk",
369 |             "unannotated",
370 |             "my_model_a",
371 |             "my_model_a_forward_ref",
372 |             "my_model_b",
373 |         ],
374 |         "title": "complex_arguments_fnArguments",
375 |         "type": "object",
376 |     }
377 | 


--------------------------------------------------------------------------------
/tests/test_tool_manager.py:
--------------------------------------------------------------------------------
  1 | import logging
  2 | from typing import Optional
  3 | 
  4 | import pytest
  5 | from pydantic import BaseModel
  6 | import json
  7 | from fastmcp.exceptions import ToolError
  8 | from fastmcp.tools import ToolManager
  9 | 
 10 | 
 11 | class TestAddTools:
 12 |     def test_basic_function(self):
 13 |         """Test registering and running a basic function."""
 14 | 
 15 |         def add(a: int, b: int) -> int:
 16 |             """Add two numbers."""
 17 |             return a + b
 18 | 
 19 |         manager = ToolManager()
 20 |         manager.add_tool(add)
 21 | 
 22 |         tool = manager.get_tool("add")
 23 |         assert tool is not None
 24 |         assert tool.name == "add"
 25 |         assert tool.description == "Add two numbers."
 26 |         assert tool.is_async is False
 27 |         assert tool.parameters["properties"]["a"]["type"] == "integer"
 28 |         assert tool.parameters["properties"]["b"]["type"] == "integer"
 29 | 
 30 |     async def test_async_function(self):
 31 |         """Test registering and running an async function."""
 32 | 
 33 |         async def fetch_data(url: str) -> str:
 34 |             """Fetch data from URL."""
 35 |             return f"Data from {url}"
 36 | 
 37 |         manager = ToolManager()
 38 |         manager.add_tool(fetch_data)
 39 | 
 40 |         tool = manager.get_tool("fetch_data")
 41 |         assert tool is not None
 42 |         assert tool.name == "fetch_data"
 43 |         assert tool.description == "Fetch data from URL."
 44 |         assert tool.is_async is True
 45 |         assert tool.parameters["properties"]["url"]["type"] == "string"
 46 | 
 47 |     def test_pydantic_model_function(self):
 48 |         """Test registering a function that takes a Pydantic model."""
 49 | 
 50 |         class UserInput(BaseModel):
 51 |             name: str
 52 |             age: int
 53 | 
 54 |         def create_user(user: UserInput, flag: bool) -> dict:
 55 |             """Create a new user."""
 56 |             return {"id": 1, **user.model_dump()}
 57 | 
 58 |         manager = ToolManager()
 59 |         manager.add_tool(create_user)
 60 | 
 61 |         tool = manager.get_tool("create_user")
 62 |         assert tool is not None
 63 |         assert tool.name == "create_user"
 64 |         assert tool.description == "Create a new user."
 65 |         assert tool.is_async is False
 66 |         assert "name" in tool.parameters["$defs"]["UserInput"]["properties"]
 67 |         assert "age" in tool.parameters["$defs"]["UserInput"]["properties"]
 68 |         assert "flag" in tool.parameters["properties"]
 69 | 
 70 |     def test_add_invalid_tool(self):
 71 |         manager = ToolManager()
 72 |         with pytest.raises(AttributeError):
 73 |             manager.add_tool(1)  # type: ignore
 74 | 
 75 |     def test_add_lambda(self):
 76 |         manager = ToolManager()
 77 |         tool = manager.add_tool(lambda x: x, name="my_tool")
 78 |         assert tool.name == "my_tool"
 79 | 
 80 |     def test_add_lambda_with_no_name(self):
 81 |         manager = ToolManager()
 82 |         with pytest.raises(
 83 |             ValueError, match="You must provide a name for lambda functions"
 84 |         ):
 85 |             manager.add_tool(lambda x: x)
 86 | 
 87 |     def test_warn_on_duplicate_tools(self, caplog):
 88 |         """Test warning on duplicate tools."""
 89 | 
 90 |         def f(x: int) -> int:
 91 |             return x
 92 | 
 93 |         manager = ToolManager()
 94 |         manager.add_tool(f)
 95 |         with caplog.at_level(logging.WARNING):
 96 |             manager.add_tool(f)
 97 |             assert "Tool already exists: f" in caplog.text
 98 | 
 99 |     def test_disable_warn_on_duplicate_tools(self, caplog):
100 |         """Test disabling warning on duplicate tools."""
101 | 
102 |         def f(x: int) -> int:
103 |             return x
104 | 
105 |         manager = ToolManager()
106 |         manager.add_tool(f)
107 |         manager.warn_on_duplicate_tools = False
108 |         with caplog.at_level(logging.WARNING):
109 |             manager.add_tool(f)
110 |             assert "Tool already exists: f" not in caplog.text
111 | 
112 | 
113 | class TestCallTools:
114 |     async def test_call_tool(self):
115 |         def add(a: int, b: int) -> int:
116 |             """Add two numbers."""
117 |             return a + b
118 | 
119 |         manager = ToolManager()
120 |         manager.add_tool(add)
121 |         result = await manager.call_tool("add", {"a": 1, "b": 2})
122 |         assert result == 3
123 | 
124 |     async def test_call_async_tool(self):
125 |         async def double(n: int) -> int:
126 |             """Double a number."""
127 |             return n * 2
128 | 
129 |         manager = ToolManager()
130 |         manager.add_tool(double)
131 |         result = await manager.call_tool("double", {"n": 5})
132 |         assert result == 10
133 | 
134 |     async def test_call_tool_with_default_args(self):
135 |         def add(a: int, b: int = 1) -> int:
136 |             """Add two numbers."""
137 |             return a + b
138 | 
139 |         manager = ToolManager()
140 |         manager.add_tool(add)
141 |         result = await manager.call_tool("add", {"a": 1})
142 |         assert result == 2
143 | 
144 |     async def test_call_tool_with_missing_args(self):
145 |         def add(a: int, b: int) -> int:
146 |             """Add two numbers."""
147 |             return a + b
148 | 
149 |         manager = ToolManager()
150 |         manager.add_tool(add)
151 |         with pytest.raises(ToolError):
152 |             await manager.call_tool("add", {"a": 1})
153 | 
154 |     async def test_call_unknown_tool(self):
155 |         manager = ToolManager()
156 |         with pytest.raises(ToolError):
157 |             await manager.call_tool("unknown", {"a": 1})
158 | 
159 |     async def test_call_tool_with_list_int_input(self):
160 |         def sum_vals(vals: list[int]) -> int:
161 |             return sum(vals)
162 | 
163 |         manager = ToolManager()
164 |         manager.add_tool(sum_vals)
165 |         # Try both with plain list and with JSON list
166 |         result = await manager.call_tool("sum_vals", {"vals": "[1, 2, 3]"})
167 |         assert result == 6
168 |         result = await manager.call_tool("sum_vals", {"vals": [1, 2, 3]})
169 |         assert result == 6
170 | 
171 |     async def test_call_tool_with_list_str_or_str_input(self):
172 |         def concat_strs(vals: list[str] | str) -> str:
173 |             return vals if isinstance(vals, str) else "".join(vals)
174 | 
175 |         manager = ToolManager()
176 |         manager.add_tool(concat_strs)
177 |         # Try both with plain python object and with JSON list
178 |         result = await manager.call_tool("concat_strs", {"vals": ["a", "b", "c"]})
179 |         assert result == "abc"
180 |         result = await manager.call_tool("concat_strs", {"vals": '["a", "b", "c"]'})
181 |         assert result == "abc"
182 |         result = await manager.call_tool("concat_strs", {"vals": "a"})
183 |         assert result == "a"
184 |         result = await manager.call_tool("concat_strs", {"vals": '"a"'})
185 |         assert result == '"a"'
186 | 
187 |     async def test_call_tool_with_complex_model(self):
188 |         from fastmcp import Context
189 | 
190 |         class MyShrimpTank(BaseModel):
191 |             class Shrimp(BaseModel):
192 |                 name: str
193 | 
194 |             shrimp: list[Shrimp]
195 |             x: None
196 | 
197 |         def name_shrimp(tank: MyShrimpTank, ctx: Context) -> list[str]:
198 |             return [x.name for x in tank.shrimp]
199 | 
200 |         manager = ToolManager()
201 |         manager.add_tool(name_shrimp)
202 |         result = await manager.call_tool(
203 |             "name_shrimp",
204 |             {"tank": {"x": None, "shrimp": [{"name": "rex"}, {"name": "gertrude"}]}},
205 |         )
206 |         assert result == ["rex", "gertrude"]
207 |         result = await manager.call_tool(
208 |             "name_shrimp",
209 |             {"tank": '{"x": null, "shrimp": [{"name": "rex"}, {"name": "gertrude"}]}'},
210 |         )
211 |         assert result == ["rex", "gertrude"]
212 | 
213 | 
214 | class TestToolSchema:
215 |     async def test_context_arg_excluded_from_schema(self):
216 |         from fastmcp import Context
217 | 
218 |         def something(a: int, ctx: Context) -> int:
219 |             return a
220 | 
221 |         manager = ToolManager()
222 |         tool = manager.add_tool(something)
223 |         assert "ctx" not in json.dumps(tool.parameters)
224 |         assert "Context" not in json.dumps(tool.parameters)
225 |         assert "ctx" not in tool.fn_metadata.arg_model.model_fields
226 | 
227 | 
228 | class TestContextHandling:
229 |     """Test context handling in the tool manager."""
230 | 
231 |     def test_context_parameter_detection(self):
232 |         """Test that context parameters are properly detected in Tool.from_function()."""
233 |         from fastmcp import Context
234 | 
235 |         def tool_with_context(x: int, ctx: Context) -> str:
236 |             return str(x)
237 | 
238 |         manager = ToolManager()
239 |         tool = manager.add_tool(tool_with_context)
240 |         assert tool.context_kwarg == "ctx"
241 | 
242 |         def tool_without_context(x: int) -> str:
243 |             return str(x)
244 | 
245 |         tool = manager.add_tool(tool_without_context)
246 |         assert tool.context_kwarg is None
247 | 
248 |     async def test_context_injection(self):
249 |         """Test that context is properly injected during tool execution."""
250 |         from fastmcp import Context, FastMCP
251 | 
252 |         def tool_with_context(x: int, ctx: Context) -> str:
253 |             assert isinstance(ctx, Context)
254 |             return str(x)
255 | 
256 |         manager = ToolManager()
257 |         manager.add_tool(tool_with_context)
258 | 
259 |         mcp = FastMCP()
260 |         ctx = mcp.get_context()
261 |         result = await manager.call_tool("tool_with_context", {"x": 42}, context=ctx)
262 |         assert result == "42"
263 | 
264 |     async def test_context_injection_async(self):
265 |         """Test that context is properly injected in async tools."""
266 |         from fastmcp import Context, FastMCP
267 | 
268 |         async def async_tool(x: int, ctx: Context) -> str:
269 |             assert isinstance(ctx, Context)
270 |             return str(x)
271 | 
272 |         manager = ToolManager()
273 |         manager.add_tool(async_tool)
274 | 
275 |         mcp = FastMCP()
276 |         ctx = mcp.get_context()
277 |         result = await manager.call_tool("async_tool", {"x": 42}, context=ctx)
278 |         assert result == "42"
279 | 
280 |     async def test_context_optional(self):
281 |         """Test that context is optional when calling tools."""
282 |         from fastmcp import Context
283 | 
284 |         def tool_with_context(x: int, ctx: Optional[Context] = None) -> str:
285 |             return str(x)
286 | 
287 |         manager = ToolManager()
288 |         manager.add_tool(tool_with_context)
289 |         # Should not raise an error when context is not provided
290 |         result = await manager.call_tool("tool_with_context", {"x": 42})
291 |         assert result == "42"
292 | 
293 |     async def test_context_error_handling(self):
294 |         """Test error handling when context injection fails."""
295 |         from fastmcp import Context, FastMCP
296 | 
297 |         def tool_with_context(x: int, ctx: Context) -> str:
298 |             raise ValueError("Test error")
299 | 
300 |         manager = ToolManager()
301 |         manager.add_tool(tool_with_context)
302 | 
303 |         mcp = FastMCP()
304 |         ctx = mcp.get_context()
305 |         with pytest.raises(ToolError, match="Error executing tool tool_with_context"):
306 |             await manager.call_tool("tool_with_context", {"x": 42}, context=ctx)
307 | 


--------------------------------------------------------------------------------