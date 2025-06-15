# # #type: ignore
# import os
# from agents import AsyncOpenAI, Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel, function_tool
# from dotenv import load_dotenv
# import asyncio
# import webbrowser
# import urllib.parse
# import chainlit as cl

# set_tracing_disabled(True)
# load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
# model = OpenAIChatCompletionsModel(openai_client=client, model="gemini-2.0-flash")

# @cl.on_chat_start
# async def start():
#     await cl.Message(content="Hello there, I am a shopping assistant!").send()

# @cl.on_message
# async def main(message: cl.Message):
#     msg = cl.Message(content="Processing...")
#     await msg.send()
#     try:
#         @function_tool
#         async def search_daraz(item: str):
#             base_url = "https://www.daraz.pk/catalog/?q="
#             search_query = urllib.parse.quote(item)
#             search_url = f"{base_url}{search_query}"
            
#             print(f"Opening browser for search URL: {search_url}") 
#             webbrowser.open(search_url)
#             return f"Opened Daraz.pk search results for '{item}'"
        
        
#         shopping_agent = Agent(
#         name="Shopping Assistant",
#         instructions="You assist users in finding products by redirecting to Daraz.pk (https://www.daraz.pk) search results using the search_daraz tool. For non-shopping queries, delegate appropriately.",
#         model=model,
#         tools=[search_daraz]
#         )

#         support_agent = Agent(
#             name="Support Agent",
#             instructions="You help users with post-purchase support and returns.",
#             model=model
#         )

#         shopping_tool = shopping_agent.as_tool(tool_name="ShoppingTool", tool_description="Redirect to Daraz.pk to search for products.")
#         support_tool = support_agent.as_tool(tool_name="SupportTool", tool_description="Provide post-purchase support and returns.")

#         triage_agent = Agent(
#             name="Triage Agent",
#             instructions="You route user queries to the appropriate department. For queries about buying products, use the ShoppingTool to redirect to Daraz.pk search results. For post-purchase issues, use the SupportTool.",
#             model=model,
#             tools=[shopping_tool, support_tool]
#         )
        
#         result = await Runner.run(triage_agent, message.content)
#         msg.content = result.final_output
#         await msg.update()
        
#     except Exception as e:
#         msg.content = f"Error: {e}"
#         await msg.update()
#         return

# # @function_tool
# # async def search_daraz(item: str):
# #     base_url = "https://www.daraz.pk/catalog/?q="
# #     search_query = urllib.parse.quote(item)
# #     search_url = f"{base_url}{search_query}"
    
# #     print(f"Opening browser for search URL: {search_url}") 
# #     webbrowser.open(search_url)
# #     return f"Opened Daraz.pk search results for '{item}'"

# # async def main():
# #     # shopping_agent = Agent(
# #     #     name="Shopping Assistant",
# #     #     instructions="You assist users in finding products by redirecting to Daraz.pk (https://www.daraz.pk) search results using the search_daraz tool. For non-shopping queries, delegate appropriately.",
# #     #     model=model,
# #     #     tools=[search_daraz]
# #     # )

# #     # support_agent = Agent(
# #     #     name="Support Agent",
# #     #     instructions="You help users with post-purchase support and returns.",
# #     #     model=model
# #     # )

# #     # shopping_tool = shopping_agent.as_tool(tool_name="ShoppingTool", tool_description="Redirect to Daraz.pk to search for products.")
# #     # support_tool = support_agent.as_tool(tool_name="SupportTool", tool_description="Provide post-purchase support and returns.")

# #     # triage_agent = Agent(
# #     #     name="Triage Agent",
# #     #     instructions="You route user queries to the appropriate department. For queries about buying products, use the ShoppingTool to redirect to Daraz.pk search results. For post-purchase issues, use the SupportTool.",
# #     #     model=model,
# #     #     tools=[shopping_tool, support_tool]
# #     # )
    
# #     # result = await Runner.run(triage_agent, "I want to buy men shirt")
# #     # print("Final Output:", result.final_output)

# # if __name__ == "__main__":
# #     asyncio.run(main())

import os
from agents import AsyncOpenAI, Agent, Runner, set_tracing_disabled, OpenAIChatCompletionsModel, function_tool
from dotenv import load_dotenv
import asyncio
import webbrowser
import urllib.parse
import chainlit as cl

set_tracing_disabled(True)
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = AsyncOpenAI(api_key=GEMINI_API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
model = OpenAIChatCompletionsModel(openai_client=client, model="gemini-2.0-flash")

@cl.on_chat_start
async def start():
    await cl.Message(content="Hello there, I am a shopping assistant!").send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Processing...")
    await msg.send()
    try:
        @function_tool
        async def search_daraz(item: str):
            base_url = "https://www.daraz.pk/catalog/?q="
            search_query = urllib.parse.quote(item)
            search_url = f"{base_url}{search_query}"
            
            print(f"Opening browser for search URL: {search_url}") 
            webbrowser.open(search_url)
            return f"Opened Daraz.pk search results for '{item}'"
        
        @function_tool
        async def redirect_to_login():
            login_url = "https://www.daraz.pk"
            print(f"Redirecting to login URL: {login_url}")
            webbrowser.open(login_url)
            return "Redirected to Daraz.pk login page. Please log in to access your account."
        
        shopping_agent = Agent(
            name="Shopping Assistant",
            instructions="You assist users in finding products by redirecting to Daraz.pk (https://www.daraz.pk) search results using the search_daraz tool. For non-shopping queries, delegate appropriately.",
            model=model,
            tools=[search_daraz]
        )

        support_agent = Agent(
            name="Support Agent",
            instructions="You help users with post-purchase support and returns. For queries about recent purchases, use the redirect_to_login tool to redirect to the Daraz.pk login page.",
            model=model,
            tools=[redirect_to_login]
        )

        shopping_tool = shopping_agent.as_tool(tool_name="ShoppingTool", tool_description="Redirect to Daraz.pk to search for products.")
        support_tool = support_agent.as_tool(tool_name="SupportTool", tool_description="Redirect to Daraz.pk login page for post-purchase support.")

        triage_agent = Agent(
            name="Triage Agent",
            instructions="You route user queries to the appropriate department. For queries about buying products, use the ShoppingTool to redirect to Daraz.pk search results. For post-purchase issues, use the SupportTool to redirect to the Daraz.pk login page.If any other query is not about buying products or post-purchase issues, delegate appropriately.If the user says anything other than 'buying products' or 'post-purchase issues', delegate appropriately.",
            model=model,
            tools=[shopping_tool, support_tool]
        )
        
        result = await Runner.run(triage_agent, message.content)
        msg.content = result.final_output
        await msg.update()
        
    except Exception as e:
        msg.content = f"Error: {e}"
        await msg.update()
        return
