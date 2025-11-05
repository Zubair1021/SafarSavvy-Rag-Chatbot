


# 🚀 SafarSavvy AI - University Transport Assistant

**Transform your university transport documents into an intelligent, searchable knowledge base powered by AI.**

## ✨ **What is SafarSavvy AI?**

SafarSavvy AI is a professional-grade **Retrieval-Augmented Generation (RAG)** system designed for university transportation systems. It transforms transport documents into an intelligent knowledge base, allowing students to ask questions in natural language and get instant, accurate answers about bus routes, timings, stops, registration, and service updates.

## 🎯 **Perfect For:**

- **University Students** - Bus routes, timings, stops, and schedules
- **Transport Office** - Service updates, policies, and procedures
- **Student Services** - Registration, bus passes, and transport information
- **Campus Administration** - Transport documentation and knowledge base

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   FastAPI       │    │   Vector Store  │
│   (React/HTML)  │◄──►│   Backend       │◄──►│   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   DeepSeek AI   │
                       │   (OpenRouter)  │
                       └─────────────────┘
```

## 🚀 **Key Features**


### 🤖 **AI-Powered Chat**
- **Natural Language Queries** - Ask questions in plain English
- **Context-Aware Responses** - AI understands document context
- **Conversation Memory** - Maintains chat history
- **Multilingual Support** - Works with English and Urdu text
- **Real-time Processing** - Instant responses

### 🎨 **Professional Interface**
- **Modern UI/UX** - Clean, professional design
- **Responsive Design** - Works on all devices
- **Real-time Updates** - Live progress indicators
- **Professional Branding** - Ready for company use

### 🔒 **Enterprise Features**
- **Secure Processing** - Local document processing
- **Memory Management** - Optimized for large files
- **Error Handling** - Robust error management
- **Logging & Monitoring** - Comprehensive system logs
- **Scalable Architecture** - Ready for production use

## 🛠️ **Technology Stack**

- **Backend**: FastAPI (Python)
- **AI Model**: DeepSeek AI via OpenRouter
- **Vector Database**: ChromaDB
- **Embeddings**: Sentence Transformers (all-mpnet-base-v2)
- **Frontend**: HTML5, CSS3, JavaScript


## 📋 **Requirements**

### System Requirements
- **OS**: Windows 10/11, macOS, Linux
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Python**: 3.8 or higher

### Software Dependencies
- Python 3.8+
- pip package manager
- Modern web browser

## 🚀 **Quick Start**

### 1. **Clone & Setup**
```bash
git clone <your-repo-url>
cd safarsavvy-rag
```

### 2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Configure Environment**
```bash
# Copy environment template
cp env_template.txt .env

# Edit .env file with your API keys
DEEPSEEK_API_KEY=your_openrouter_api_key_here
DATABASE_URL=sqlite:///safarsavvy.db
CHROMA_DB_PATH=./chroma_db
LOG_LEVEL=INFO
```

### 4. **Start the System**
```bash
python start.py
```

### 5. **Access the Interface**
Open your browser and go to: `http://localhost:8000`



## 🚀 **Deployment Options**

### **Development**
```bash
python start.py
```

### **Production**
```bash
# Using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t safarsavvy-ai .
docker run -p 8000:8000 safarsavvy-ai
```

### **Cloud Deployment**
- **AWS**: EC2 with RDS and S3
- **Azure**: App Service with Cosmos DB
- **Google Cloud**: Compute Engine with Cloud SQL
- **Heroku**: Simple deployment with add-ons

## 🧪 **Testing**

### **System Health Check**
```bash
python test_system.py
```
## 🔮 **Future Enhancements**

### **Planned Features**
- **Multi-User Support**: User authentication and roles
- **Document Versioning**: Track document changes
- **Advanced Analytics**: Usage insights and reports
- **API Integration**: Connect with other business systems
- **Mobile App**: Native mobile applications

### **AI Improvements**
- **Custom Training**: Train on company-specific data
- **Multi-Modal**: Support images and diagrams
- **Voice Interface**: Speech-to-text capabilities
- **Smart Summaries**: Automatic document summarization

## 📞 **Support & Community**

### **Getting Help**
- **Documentation**: Check this README first
- **Issues**: Report bugs via GitHub issues
- **Discussions**: Join community discussions
- **Email**: Contact support team

### **Contributing**
1. Fork the repository
2. Create feature branch
3. Make your changes
4. Submit pull request
5. Join the team!

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Grok AI**: Advanced language model capabilities
- **OpenRouter**: API access and management
- **ChromaDB**: Vector database technology
- **FastAPI**: Modern Python web framework
- **Open Source Community**: All contributors and maintainers

---

**Built with ❤️ for modern businesses**

*Transform your university transport knowledge into intelligent insights with SafarSavvy AI*
