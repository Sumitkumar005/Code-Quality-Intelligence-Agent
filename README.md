# Code Quality Intelligence Agent (CQIA)

🤖 **AI-Powered Code Analysis & Quality Intelligence**

An advanced code quality analysis tool that combines AST parsing, machine learning, and conversational AI to provide comprehensive insights into your codebase.

## ✨ Features

### Core Capabilities
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, Go, Rust, C#
- **AST-Based Analysis**: Deep structural code analysis using Abstract Syntax Trees
- **AI-Powered Insights**: LangChain-based agent with conversational Q&A
- **RAG Integration**: Retrieval-Augmented Generation for large codebases
- **CLI Interface**: Simple command-line tool for quick analysis
- **Web Interface**: Modern React-based dashboard

### Analysis Categories
- 🔒 **Security Vulnerabilities**: Hardcoded credentials, unsafe functions, injection risks
- ⚡ **Performance Issues**: Inefficient loops, memory leaks, optimization opportunities  
- 🧹 **Code Quality**: Complexity, duplication, maintainability issues
- 📚 **Documentation**: Missing docstrings, inadequate comments
- 🧪 **Testing Gaps**: Coverage analysis and test recommendations

### Advanced Features
- **Severity Scoring**: Intelligent prioritization of issues
- **Technical Debt Estimation**: Time-based estimates for fixes
- **Dependency Analysis**: Code relationship mapping
- **Interactive Q&A**: Natural language queries about your code
- **GitHub Integration**: Direct repository analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for web interface)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd code-quality-agent
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
npm install
```

4. **Optional: Install Ollama for Local LLM**
```bash
# Visit https://ollama.ai for installation
ollama pull llama3:8b
```

## 📋 Usage

### CLI Interface (Primary)

**Analyze local code:**
```bash
python backend/cli.py analyze ./src
```

**Analyze with different output formats:**
```bash
python backend/cli.py analyze ./src --format json --output report.json
python backend/cli.py analyze ./src --format markdown --output report.md
```

**Interactive Q&A mode:**
```bash
python backend/cli.py interactive
```

### Web Interface

1. **Start the backend:**
```bash
cd backend
python main.py
```

2. **Start the frontend:**
```bash
npm run dev
```

3. **Open browser:** http://localhost:3000

## 🏗️ Architecture

### System Design
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Web Interface   │    │  REST API       │
│                 │    │  (Next.js)       │    │  (FastAPI)      │
└─────────┬───────┘    └────────┬─────────┘    └─────────┬───────┘
          │                     │                        │
          └─────────────────────┼────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │   Analysis Service     │
                    │                        │
                    │  ┌─────────────────┐   │
                    │  │  AST Analyzer   │   │
                    │  └─────────────────┘   │
                    │  ┌─────────────────┐   │
                    │  │ LangChain Agent │   │
                    │  └─────────────────┘   │
                    │  ┌─────────────────┐   │
                    │  │   RAG System    │   │
                    │  └─────────────────┘   │
                    └────────────────────────┘
```##
# Key Components

**AST Analyzer** (`backend/app/services/ast_analyzer.py`)
- Multi-language AST parsing
- Security vulnerability detection
- Performance bottleneck identification
- Code quality metrics calculation

**Agent Service** (`backend/app/services/agent_service.py`)
- LangChain-based conversational AI
- RAG implementation for large codebases
- Intelligent question answering
- Context-aware recommendations

**Analysis Service** (`backend/app/services/analysis_service.py`)
- Orchestrates analysis workflow
- Background task processing
- Results enhancement and prioritization
- Technical debt estimation

## 🔧 Configuration

### Environment Variables
```bash
# Backend Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3:8b
DATABASE_URL=sqlite:///./cqia_tool.db

# Analysis Settings
MAX_REPO_SIZE_MB=100
MAX_FILE_SIZE_KB=1000
CHUNK_SIZE=1000

# RAG Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_DB_PATH=./vector_db
TOP_K_RETRIEVAL=5
```

### Supported File Types
- **Python**: `.py`
- **JavaScript**: `.js`, `.jsx`
- **TypeScript**: `.ts`, `.tsx`
- **Java**: `.java`
- **Go**: `.go`
- **Rust**: `.rs`
- **C#**: `.cs`

## 📊 Example Output

### CLI Analysis Report
```
📊 Analysis Summary
┌─────────────────┬─────────┐
│ Metric          │ Value   │
├─────────────────┼─────────┤
│ Total Files     │ 23      │
│ Lines of Code   │ 4,567   │
│ Languages       │ Python, │
│                 │ JS, TS  │
│ Quality Score   │ 78/100  │
└─────────────────┴─────────┘

🔍 Detected Issues
┌─────────────────┬──────────┬──────────┬─────────────────────┐
│ File            │ Type     │ Severity │ Message             │
├─────────────────┼──────────┼──────────┼─────────────────────┤
│ auth.py         │ Security │ High     │ Hardcoded password  │
│ utils.js        │ Perf     │ Medium   │ Inefficient loop    │
└─────────────────┴──────────┴──────────┴─────────────────────┘

💡 Recommendations
• 🚨 URGENT: Fix security vulnerabilities immediately
• ⚡ Optimize performance bottlenecks
• 📚 Add documentation to key functions
```

### Interactive Q&A
```
❓ Your question: What are the most critical security issues?

🤖 Based on your analysis, I found 2 high-severity security issues:
   1. Hardcoded API keys in config.py (line 15)
   2. SQL injection vulnerability in user_service.py (line 42)
   
   I recommend:
   - Move credentials to environment variables immediately
   - Implement parameterized queries for database operations
   - Consider adding input validation middleware
```

## 🧪 Testing

### Run Tests
```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests  
npm test
```

### Test Coverage
```bash
# Generate coverage report
python -m pytest --cov=app tests/
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
```bash
# Production backend
cd backend
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# Production frontend
npm run build
npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain** for agent framework
- **FastAPI** for high-performance API
- **Next.js** for modern web interface
- **Ollama** for local LLM inference
- **ChromaDB** for vector storage

---

**Built with ❤️ for developers who care about code quality**