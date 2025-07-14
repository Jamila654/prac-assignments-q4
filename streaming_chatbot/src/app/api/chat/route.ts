// import { type NextRequest, NextResponse } from "next/server"

// export async function POST(request: NextRequest) {
//   try {
//     const body = await request.json()

//     const response = await fetch("https://streaming1.vercel.app/chat/", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify(body),
//     })

//     if (!response.ok) {
//       throw new Error(`HTTP error! status: ${response.status}`)
//     }

//     const data = await response.json()
//     return NextResponse.json(data)
//   } catch (error) {
//     console.error("Proxy error:", error)
//     return NextResponse.json({ error: "Failed to fetch from FastAPI" }, { status: 500 })
//   }
// }

import type { NextRequest } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    // Ensure the request matches the FastAPI Message model structure
    const requestBody = {
      text: body.text || body.message || "",
      user_id: body.user_id || "anonymous_user", // Add required user_id field
    }

    console.log("Sending to FastAPI:", requestBody)

    const response = await fetch("https://streaming1.vercel.app/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify(requestBody),
    })

    console.log("FastAPI response status:", response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error("FastAPI error response:", errorText)
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`)
    }

    // Return the streaming response directly
    return new Response(response.body, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        "Access-Control-Allow-Origin": "*",
      },
    })
  } catch (error) {
    console.error("Proxy error:", error)
    return new Response(
      JSON.stringify({
        error: "Failed to fetch from FastAPI",
        details: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      },
    )
  }
}
