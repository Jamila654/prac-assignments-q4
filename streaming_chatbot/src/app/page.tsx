"use client"

import type React from "react"

import { useState, useEffect, useRef } from "react"

interface Message {
  id: string
  text: string
  reply: string
  isUser: boolean
  isStreaming: boolean
  timestamp: Date
}

export default function ClimateChatbot() {
  const [userName, setUserName] = useState<string>("")
  const [tempName, setTempName] = useState<string>("")
  const [showNameModal, setShowNameModal] = useState(true)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const streamingTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  // Initialize chat after name is set
  useEffect(() => {
    if (userName && messages.length === 0) {
      setMessages([
        {
          id: "1",
          text: "",
          reply: `Hello ${userName}! 👋 I'm EcoBot, your climate and environment assistant. I can help you learn about sustainability, climate change, renewable energy, and search the web for the latest environmental news. What would you like to know?`,
          isUser: false,
          isStreaming: false,
          timestamp: new Date(),
        },
      ])
    }
  }, [userName, messages.length])

  const handleNameSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (tempName.trim()) {
      setUserName(tempName.trim())
      setShowNameModal(false)
    }
  }

  // Function to simulate streaming response word by word
  const streamResponse = (fullResponse: string, messageIndex: number) => {
    const words = fullResponse.split(" ")
    let currentWordIndex = 0

    const streamNextWord = () => {
      if (currentWordIndex < words.length) {
        const currentText = words.slice(0, currentWordIndex + 1).join(" ")
        setMessages((prev) =>
          prev.map((msg, index) => (index === messageIndex ? { ...msg, reply: currentText, isStreaming: true } : msg)),
        )
        currentWordIndex++
        streamingTimeoutRef.current = setTimeout(streamNextWord, 50)
      } else {
        // Streaming complete
        setMessages((prev) => prev.map((msg, index) => (index === messageIndex ? { ...msg, isStreaming: false } : msg)))
      }
    }
    streamNextWord()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      reply: "",
      isUser: true,
      isStreaming: false,
      timestamp: new Date(),
    }

    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      text: "",
      reply: "",
      isUser: false,
      isStreaming: true,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage, botMessage])
    const currentInput = input
    setInput("")
    setIsLoading(true)

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: currentInput,
          user_id: userName, // Use the user's name as user_id
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(`API Error: ${response.status} - ${errorData.error || "Unknown error"}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let fullResponse = ""

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split("\n")

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6))
                if (data.chunk) {
                  fullResponse += data.chunk
                } else if (data.message_output) {
                  fullResponse = data.message_output
                } else if (data.tool_called) {
                  fullResponse += `🔍 Searching: ${data.tool_called}\n`
                } else if (data.tool_output) {
                  fullResponse += `📊 Found: ${data.tool_output}\n`
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      }

      const messageIndex = messages.length + 1
      streamResponse(
        fullResponse || "I apologize, but I couldn't process your request. Please try again.",
        messageIndex,
      )
    } catch (error) {
      const messageIndex = messages.length + 1
      streamResponse(`I'm having trouble connecting right now. Please try again in a moment.`, messageIndex)
    } finally {
      setIsLoading(false)
    }
  }

  const formatTimestamp = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  const quickPrompts = [
    "What are renewable energy trends?",
    "How to reduce carbon footprint?",
    "Climate change effects?",
    "Sustainable living tips?",
  ]

  // Name Modal
  if (showNameModal) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md border border-gray-100">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-3xl">🤖</span>
            </div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">Welcome to EcoBot</h1>
            <p className="text-gray-600">Your AI assistant for climate and environmental insights</p>
          </div>

          <form onSubmit={handleNameSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                What's your name?
              </label>
              <input
                type="text"
                id="name"
                value={tempName}
                onChange={(e) => setTempName(e.target.value)}
                placeholder="Enter your name"
                className="w-full px-4 py-3 border text-black border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white py-3 px-6 rounded-xl font-medium hover:from-blue-600 hover:to-indigo-700 transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              Start Chatting
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-xl">🤖</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">EcoBot</h1>
                <p className="text-sm text-gray-600">Climate & Environment AI</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-sm text-gray-600">
                Hello, <span className="font-medium text-blue-600">{userName.charAt(0).toUpperCase() + userName.slice(1)}</span>
              </div>
              <button
                onClick={() => setShowNameModal(true)}
                className="text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 px-3 py-1 rounded-full transition-colors"
              >
                Change Name
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto p-6 h-[calc(100vh-100px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 mb-6">
          {messages.map((message, index) => (
            <div key={message.id} className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[75%] ${message.isUser ? "order-2" : "order-1"}`}>
                <div
                  className={`rounded-2xl px-4 py-3 shadow-sm ${
                    message.isUser
                      ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white ml-4"
                      : "bg-white border border-gray-200 mr-4"
                  }`}
                >
                  {message.isUser ? (
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium opacity-90">{userName.charAt(0).toUpperCase() + userName.slice(1)}</span>
                      </div>
                      <p className="leading-relaxed">{message.text}</p>
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-sm font-medium text-blue-600">EcoBot</span>
                        {message.isStreaming && (
                          <div className="flex gap-1">
                            <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                            <div
                              className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                              style={{ animationDelay: "0.1s" }}
                            ></div>
                            <div
                              className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                              style={{ animationDelay: "0.2s" }}
                            ></div>
                          </div>
                        )}
                      </div>
                      <p className="whitespace-pre-wrap leading-relaxed text-gray-700">{message.reply}</p>
                    </div>
                  )}
                </div>
                <div className={`text-xs text-gray-500 mt-1 ${message.isUser ? "text-right mr-4" : "ml-4"}`}>
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-lg p-4">
          <form onSubmit={handleSubmit} className="flex gap-3 mb-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me about climate change, sustainability, renewable energy..."
              className="flex-1 px-4 py-3 text-black border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-medium transition-all duration-200 shadow-md hover:shadow-lg"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <span>Send</span>
              )}
            </button>
          </form>

          {/* Quick Prompts */}
          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt, index) => (
              <button
                key={index}
                onClick={() => setInput(prompt)}
                className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg transition-all duration-200 border border-gray-200 hover:border-gray-300"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
