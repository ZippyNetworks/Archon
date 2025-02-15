# plugins/tool_example.py

class EchoTool:
    name = "echo_tool"
    description = "Echoes the text back to the user."

    def run(self, text: str) -> str:
        return f"Echo: {text}"
