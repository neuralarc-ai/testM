# 🤖 Manus AI Clone - Complete Implementation

A fully functional clone of Manus AI with autonomous AI agents, multi-modal content generation, web automation, and real-time task orchestration.

## 🌟 Features

### 🧠 **11 Specialized AI Agents**
- **Executor Agent**: Task execution and coordination
- **Planning Agent**: Strategic planning and workflow design
- **Knowledge Agent**: Information retrieval and synthesis
- **Content Creator**: Text, articles, and creative writing
- **Visual Designer**: Image generation and visual content
- **Code Developer**: Software development and debugging
- **Data Analyst**: Data processing and insights
- **Research Specialist**: Web research and analysis
- **Communication Expert**: Email and social media content
- **Presentation Specialist**: Slides and presentation creation
- **Automation Expert**: Web automation and task automation

### 🎨 **Content Generation**
- **Text Generation**: Articles, blogs, emails, social media posts
- **Image Generation**: DALL-E 3 and Stability AI integration
- **Presentation Creation**: AI-powered slide generation with themes
- **Document Generation**: PDF, HTML, Markdown with custom styling
- **Audio Processing**: Speech synthesis and transcription
- **Infographic Creation**: Data-driven visual content

### 🌐 **Web Automation**
- **Browser Control**: Selenium-based automation with Chrome/ChromeDriver
- **AI-Powered Navigation**: GPT-4 analyzes pages and creates automation plans
- **Form Filling**: Intelligent form completion and submission
- **Data Extraction**: Web scraping with AI-guided selection
- **Session Management**: Multiple concurrent browser sessions

### ⚡ **Task Orchestration**
- **Multi-Agent Coordination**: Intelligent task distribution
- **Real-time Processing**: Async execution with progress tracking
- **Dependency Management**: Smart step execution based on prerequisites
- **Task Templates**: Predefined workflows for common use cases
- **Priority Queue**: Task prioritization and resource management

### 📱 **Multi-Platform Support**
- **Web Application**: Professional React frontend
- **Mobile App**: React Native for iOS/Android
- **REST API**: Comprehensive backend with 50+ endpoints
- **Real-time Updates**: Live progress monitoring and notifications

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │   Mobile App    │    │   API Clients   │
│     (React)     │    │ (React Native)  │    │   (External)    │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │      Backend API          │
                    │    (Flask + Python)       │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
    ┌─────┴─────┐         ┌───────┴───────┐       ┌───────┴───────┐
    │    AI     │         │ Orchestration │       │   Computer    │
    │ Services  │         │   Service     │       │   Service     │
    └───────────┘         └───────────────┘       └───────────────┘
          │                       │                       │
    ┌─────┴─────┐         ┌───────┴───────┐       ┌───────┴───────┐
    │  OpenAI   │         │  Task Queue   │       │   Selenium    │
    │ Anthropic │         │  Multi-Agent  │       │ ChromeDriver  │
    │Stability  │         │  Coordination │       │   Browser     │
    │ElevenLabs │         └───────────────┘       │  Automation   │
    │  Google   │                                 └───────────────┘
    │Perplexity │
    └───────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.11+ and pip
- **Chrome/Chromium** browser (for automation)
- **Git** for version control

### 1. Clone the Repository
```bash
git clone https://github.com/neuralarc-ai/testM.git
cd testM
```

### 2. Environment Setup
```bash
# Copy environment variables
cp manus-backend/.env.example manus-backend/.env
cp manus-frontend/.env.example manus-frontend/.env

# Edit .env files with your API keys
nano manus-backend/.env
```

### 3. One-Command Deployment
```bash
# Deploy everything automatically
./deploy.sh

# Or deploy components separately:
./deploy.sh stop     # Stop all services
./deploy.sh restart  # Restart all services
./deploy.sh status   # Check service status
./deploy.sh logs     # View logs
```

### 4. Manual Setup (Alternative)

#### Backend Setup
```bash
cd manus-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

#### Frontend Setup
```bash
cd manus-frontend
npm install
npm run dev
```

#### Mobile App Setup
```bash
cd manus-mobile
npm install
npx expo start
```

## 📋 API Documentation

### Authentication Endpoints
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/profile` - Get user profile
- `POST /api/auth/logout` - User logout

### Task Management
- `GET /api/tasks` - List user tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/{id}/execute` - Execute task

### AI Agents
- `GET /api/agents` - List available agents
- `GET /api/agents/{id}` - Get agent details
- `GET /api/agents/recommendations` - Get agent recommendations
- `POST /api/agents/{id}/execute` - Execute agent task

### Content Generation
- `POST /api/media/presentations` - Generate presentation
- `POST /api/media/presentations/ai-generate` - AI-generated presentation
- `POST /api/media/documents` - Generate document
- `POST /api/media/documents/ai-generate` - AI-generated document
- `POST /api/media/images/generate` - Generate image
- `POST /api/media/audio/generate-speech` - Generate speech

### Task Orchestration
- `GET /api/orchestration/tasks/templates` - Get task templates
- `POST /api/orchestration/tasks/create-from-template` - Create from template
- `POST /api/orchestration/tasks/create-custom` - Create custom task
- `GET /api/orchestration/tasks` - List orchestration tasks
- `POST /api/orchestration/tasks/{id}/cancel` - Cancel task
- `POST /api/orchestration/tasks/{id}/pause` - Pause task
- `POST /api/orchestration/tasks/{id}/resume` - Resume task

### Computer Automation
- `POST /api/computer/sessions` - Create browser session
- `GET /api/computer/sessions` - List sessions
- `POST /api/computer/sessions/{id}/automate` - Automate task
- `GET /api/computer/sessions/{id}/status` - Get session status

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
# AI Service API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
STABILITY_API_KEY=your_stability_key
ELEVENLABS_API_KEY=your_elevenlabs_key
GOOGLE_API_KEY=your_google_key
PERPLEXITY_API_KEY=your_perplexity_key

# Database
DATABASE_URL=sqlite:///manus.db

# Security
JWT_SECRET_KEY=your_jwt_secret
FLASK_SECRET_KEY=your_flask_secret

# Server
FLASK_ENV=production
FLASK_DEBUG=False
```

#### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Manus AI Clone
```

## 📱 Mobile App

The React Native mobile app provides full access to all Manus AI features:

### Features
- **Cross-platform**: iOS and Android support
- **Authentication**: Secure login and registration
- **Task Management**: Create and monitor tasks
- **Agent Interaction**: Access all AI agents
- **Content Library**: View generated content
- **Real-time Updates**: Live task progress

### Development
```bash
cd manus-mobile
npm install
npx expo start

# For iOS
npx expo start --ios

# For Android
npx expo start --android
```

## 🧪 Testing

### Backend Tests
```bash
cd manus-backend
source venv/bin/activate
python -m pytest tests/
```

### Frontend Tests
```bash
cd manus-frontend
npm test
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# API info
curl http://localhost:8000/api

# Test authentication
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@example.com","password":"password123"}'
```

## 🚀 Production Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d --build

# Scale services
docker-compose up -d --scale backend=3
```

### AWS Deployment
```bash
# Deploy backend to AWS Lambda
cd manus-backend
serverless deploy

# Deploy frontend to AWS S3 + CloudFront
cd manus-frontend
npm run build
aws s3 sync dist/ s3://your-bucket-name
```

### Systemd Services
```bash
# Create systemd services for production
./deploy.sh systemd

# Start services
sudo systemctl start manus-backend
sudo systemctl start manus-frontend
```

## 📊 Monitoring

### Health Checks
- Backend: `http://localhost:8000/health`
- Frontend: `http://localhost:3000`
- API Status: `http://localhost:8000/api`

### Logs
```bash
# View logs
./deploy.sh logs

# Real-time monitoring
tail -f backend.log
tail -f frontend.log
```

## 🔒 Security

- **JWT Authentication**: Secure token-based authentication
- **API Rate Limiting**: Protection against abuse
- **Input Validation**: Comprehensive request validation
- **CORS Configuration**: Secure cross-origin requests
- **Environment Variables**: Secure API key management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 and DALL-E 3
- **Anthropic** for Claude AI
- **Stability AI** for image generation
- **ElevenLabs** for speech synthesis
- **Google** for various AI services
- **Perplexity** for web search capabilities

## 📞 Support

For support and questions:
- **Email**: support@neuralarc.ai
- **Website**: https://neuralarc.ai
- **Documentation**: [Full API Documentation](docs/api.md)

---

**Built with ❤️ by Neural Arc Inc**

*Manus AI Clone - The complete autonomous AI agent platform*

