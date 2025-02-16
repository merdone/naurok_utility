Here's a sample `README.md` file for the project:

---

# Naurok Test Answer Bot

This project is a Telegram bot that automates the process of answering tests from the Naurok platform. The bot uses Selenium for browser automation, BeautifulSoup for parsing HTML content, and a task queue to handle multiple user requests.

---

## Features

- **Automated Test Processing:** Handles Naurok tests by logging in, selecting random options, and submitting answers.
- **Queue System:** Processes multiple test requests in order and notifies users of their position in the queue.
- **Caching:** Caches answers to avoid reprocessing tests and provides quick responses for previously processed tests.
- **Thread Management:** Uses threading to monitor idle time and clear outdated tests.
- **Error Handling:** Handles various errors during test processing and provides feedback to users.

---

## Prerequisites

1. Python 3.8+
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download the ChromeDriver that matches your version of Google Chrome:
   - [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
4. Add the `chromedriver` executable to your system's PATH or place it in the project directory.

---

## Environment Variables

Create a file named `config.env` in the project root directory and add the following environment variables:

```env
EMAIL=your_email
PASSWORD=your_password
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

---

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone https://github.com:merdone/naurok_utility.git
   cd naurok_utility
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your environment variables in `config.env`.

4. Start the bot:
   ```bash
   python main.py
   ```

---

## Usage

1. Start a conversation with your Telegram bot by sending `/start`.
2. Send a link to a Naurok test (e.g., `https://naurok.com.ua/test/...`).
3. The bot will add your request to the queue and notify you when the test results are ready.
4. Use a dot (`.`) followed by a search query to attempt to find a test link via Google (e.g., `.math test naurok`).

---

## Commands

- `/start` - Start the conversation with the bot.
- Sending a test link - The bot will process the test and provide answers.
- `.` followed by a query - Searches for a Naurok test link using Google (captcha may interfere).

---

## Known Issues and Limitations

- **Captcha:** The bot cannot handle captchas. If a captcha appears, the test may fail.
- **Headless Mode:** The bot operates in headless mode, which may encounter rendering issues with certain tests.
- **Error Handling:** The bot provides basic error messages but may not specify the exact cause of the error.

---

## Contributing

If you'd like to contribute to this project, feel free to create a pull request or open an issue with suggestions for improvement.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

## Disclaimer

This bot is for educational purposes only. Use it responsibly and ensure you comply with the Naurok platform's terms of service.

---

