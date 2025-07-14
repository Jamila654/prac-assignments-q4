# 🤖 EcoBot - Climate & Environment AI Chatbot

A modern, streaming AI chatbot focused on climate change, environmental sustainability, and renewable energy topics. Built with Next.js frontend and FastAPI backend with real-time streaming responses.

## ✨ Features

- **🌍 Climate-Focused AI**: Specialized chatbot for environmental and climate topics
- **⚡ Real-time Streaming**: Word-by-word streaming responses for better user experience
- **🔍 Web Search Integration**: Can search the web for latest environmental news and data
- **👤 Personalized Experience**: User name collection and personalized interactions
- **📱 Responsive Design**: Clean, modern UI that works on all devices
- **🛠️ Tool Integration**: Supports various environmental data tools and APIs
- **💬 Interactive Chat**: Quick prompt buttons for common environmental questions

## 🚀 Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Server-Sent Events (SSE)** - Real-time streaming communication

### Backend
- **FastAPI** - Modern Python web framework
- **Streaming Response** - Real-time data streaming
- **CORS Middleware** - Cross-origin resource sharing
- **Pydantic** - Data validation and serialization

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- npm or yarn

### Frontend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecobot-chatbot.git
cd ecobot-chatbot
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Backend Setup

The backend is hosted at `https://streaming1.vercel.app/` but you can run it locally:

1. Navigate to the backend directory (if available)
2. Install Python dependencies:
```bash
pip install fastapi uvicorn python-multipart
```

3. Run the FastAPI server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```env
# FastAPI Backend URL
NEXT_PUBLIC_API_URL=https://streaming1.vercel.app

# Optional: Custom API endpoints
FASTAPI_CHAT_ENDPOINT=/chat/
```

### API Configuration

The frontend communicates with the FastAPI backend through:
- **Endpoint**: `/api/chat`
- **Method**: POST
- **Content-Type**: application/json
- **Response**: text/event-stream (Server-Sent Events)

## 📡 API Reference

### Chat Endpoint

**POST** `/api/chat`

Request body:
```json
{
  "text": "What are renewable energy trends?",
  "user_id": "john_doe"
}
```

Response (Server-Sent Events):
```
data: {"chunk": "Renewable"}
data: {"chunk": " energy"}
data: {"tool_called": "web_search"}
data: {"message_output": "Complete response here"}
```

### FastAPI Backend Endpoints

- **GET** `/` - Health check
- **GET** `/users/{user_id}` - Get user information
- **POST** `/chat/` - Main chat endpoint with streaming response

## 🏗️ Project Structure

```
ecobot-chatbot/
├── app/
│   ├── api/
│   │   └── chat/
│   │       └── route.ts          # API proxy to FastAPI
│   ├── globals.css               # Global styles
│   ├── layout.tsx               # Root layout
│   └── page.tsx                 # Main chat interface
├── public/                      # Static assets
├── README.md
├── next.config.js
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

## 🎯 Usage

1. **Start a Conversation**: Enter your name when prompted
2. **Ask Questions**: Type questions about climate, environment, or sustainability
3. **Use Quick Prompts**: Click on suggested topics for quick access
4. **Real-time Responses**: Watch as responses stream in word-by-word
5. **Web Search**: The bot can search for latest environmental news and data

### Example Questions

- "What are the latest developments in renewable energy?"
- "How can I reduce my carbon footprint?"
- "What are the effects of climate change on agriculture?"
- "Tell me about sustainable living practices"

## 🔄 Streaming Implementation

The chatbot uses Server-Sent Events (SSE) for real-time streaming:

1. **Frontend**: Sends POST request to `/api/chat`
2. **API Route**: Proxies request to FastAPI backend
3. **FastAPI**: Returns streaming response with various event types
4. **Frontend**: Processes stream and displays word-by-word

### Event Types

- `chunk`: Individual text pieces
- `tool_called`: When AI uses a tool (e.g., web search)
- `tool_output`: Results from tool usage
- `message_output`: Complete response message

## 🛠️ Development

### Adding New Features

1. **Frontend Components**: Add to `app/` directory
2. **API Routes**: Create in `app/api/` directory
3. **Styling**: Use Tailwind CSS classes
4. **Types**: Define in TypeScript interfaces

### Code Style

- Use TypeScript for type safety
- Follow Next.js App Router conventions
- Use Tailwind CSS for styling
- Implement proper error handling

## 🚀 Deployment

### Frontend (Vercel)

1. Push to GitHub repository
2. Connect to Vercel
3. Deploy automatically on push

### Backend (FastAPI)

The backend is already deployed at `https://streaming1.vercel.app/`


### Development Guidelines

- Write clean, documented code
- Add TypeScript types for new features
- Test streaming functionality thoroughly
- Follow existing code patterns
- Update README for new features


## 🙏 Acknowledgments

- **FastAPI** for the excellent Python web framework
- **Next.js** for the React framework
- **Tailwind CSS** for the utility-first CSS framework
- **OpenAI** for AI capabilities (if using OpenAI models)
- **Vercel** for hosting and deployment

## 🔗 Links

- [Live Demo](https://streamingchatbot.vercel.app/)
- [FastAPI Backend](https://streaming1.vercel.app)
- [GitHub Repository](https://github.com/Jamila654/prac-assignments-q4/tree/main/streaming_chatbot)

---

**Made with 💚 for a sustainable future**


