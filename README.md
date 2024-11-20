# QueryLens - Data Analytics Chatbot

QueryLens is a Streamlit-based interactive chatbot for data analytics. Designed to process SQL and Python queries, it provides users with insightful responses, visualizations, and interactive prompts for data-related questions. Users can ask questions, view responses, and generate plots in real-time.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Example Prompts](#example-prompts)
- [Technical Details](#technical-details)
- [License](#license)

## Overview

QueryLens is a powerful data chatbot that interacts with an SQL database and a Python interpreter to respond to user queries. It supports:
- SQL queries for extracting data insights.
- Python-based visualizations using Plotly for data analysis and reporting.
- Enhanced UI for ease of use, including preset examples and plot customization.

## Features

- **Data Exploration**: Perform SQL queries on your database and retrieve information in natural language.
- **Data Visualization**: Generate Python-based plots on the fly with Plotly.
- **Enhanced UI**: Streamlit-based UI with interactive elements, customizable layout, and reset functionality.
- **System & Initial Prompts**: Start your exploration with preset prompts for ease of use.
- **State Management**: Maintain conversation history for context-aware querying and plotting.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/QueryLens.git
   cd QueryLens

2. Set up a virtual environment and install dependencies:
   ```bash
   python3 -m venv env
   source env/bin/activate
   pip install -r requirements.txt

3. Launch the Streamlit app:
   ```bash
   streamlit run chat.py


## Usage

1. Access the Interface: Open the Streamlit URL provided in your terminal.
2. Ask Questions: Use natural language queries like “What is the total sales by year?”.
3. Generate Plots: Request visualizations directly, e.g., “Plot the number of users by country.”
4. Use the Reset Button: Clear your session and start a fresh conversation anytime.

## Configuration

- **OpenAI API Key**: Your API key is required to enable natural language processing. Add it to your .env file.
- **SQL Database**: Define your SQL database connection details in .env for secure and effective database access.

## Example Prompts

- "Show the total sales by year."
- "List the top 10 products sold."
- "Number of users in each country who came via Facebook."
- "Plot the sales trend over the years."
- "Show geographical distribution of distribution centers on the map."


## Technical Details

### Architecture

QueryLens uses a combination of the following:

- **Streamlit**: For the UI, allowing interactive querying, reset functionality, and custom layouts.
- **OpenAI’s Language Models**: For natural language understanding and query interpretation.
- **SQLAlchemy and LangChain SQL Agent**: For managing database queries.
- **Plotly**: For dynamic data visualizations.
- **Python Session State**: To manage conversation context and preserve session history.


### Error Handling

QueryLens incorporates mechanisms to manage:
- **Rate Limiting**: Retry logic to handle OpenAI API limits.
- **Output Formatting**: Ensures correct display of responses and plots.

### Customizability

- **UI Improvements**: Add custom layouts or colors in the Streamlit app.
- **Expand Prompts**: Add more system prompts or sample questions for a better user experience.


## License
This project is licensed under the MIT License.
