import os
import random
import asyncio
import logging
import resend
from fastmcp import FastMCP

mcp = FastMCP(name="HelloMCPServer")

logging.basicConfig(level=logging.INFO)
resend.api_key = os.getenv("RESEND_API_KEY")
sender = os.getenv("RESEND_FROM_EMAIL")

@mcp.tool()
def greet(name: str) -> str:
    """Greets a user by name."""
    logging.info(f"greet() called with name={name}")
    return f"Ahoy, {name}! Welcome aboard, ye scallywag! 🏴‍☠️"

@mcp.tool()
def roll_dice(n_dice: int) -> list[int]:
    """Rolls n_dice 6-sided dice and returns the results."""
    logging.info(f"roll_dice() called with n_dice={n_dice}")
    return [random.randint(1, 6) for _ in range(n_dice)]

@mcp.tool()
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email using Resend."""
    logging.info(f"send_email() called recipient={recipient}")
    try:
        email = resend.Emails.send({
            "from": sender,
            "to": [recipient],
            "subject": subject,
            "html": f"<strong>{body}</strong>",
            "text": body
        })
        return f"Email sent successfully. ID: {email['id']}"
    except Exception as e:
        return f"Error sending email: {e}"

async def main():
    await mcp.run_async(transport="streamable-http", path="/mcp", host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
