class CopilotCLILogger:
    @staticmethod
    def log_success(message: str):
        print(f"✔️  {message}")

    @staticmethod
    def log_error(message: str):
        print(f"❌ {message}")
