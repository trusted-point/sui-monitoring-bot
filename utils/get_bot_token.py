def get_bot_token(file_path='bot_token.txt'):
    try:
        with open(file_path, 'r') as file:
            token = file.read().strip()
            return str(token)
    except FileNotFoundError:
        print(f"Error: Bot token file '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error: Unable to read bot token. {e}")
        return None
    