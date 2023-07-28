# HubermanLab QA CLI Tool
The HubermanLab QA command line tool allows you to ask a health-related question and get actionable insights along with references to relevant resources. The resources are based on the content of the Huberman Lab Podcast, which is hosted by Andrew Huberman, a neuroscientist and tenured Professor at the Department of Neurobiology at Stanford University School of Medicine.

## Features
The CLI tool allows you to:

- **Setup** paths to which the outputs will be saved. If the paths are not setup, the default paths will be taken.
- **Perform** Question Answering: This mode will return the answer and relevant segments.
- **Search** for resources: This mode will return only the relevant resources, without checking if they are relevant nor providing a final answer.

## Installation
There are two ways to install the CLI tool: directly from PyPi using pip, or by cloning the repository and installing the requirements.

#### Method 1: PyPi
```bash
pip install hubermanlabqa
```

#### Method 2: From Repository
First, clone the repository to your local machine:
```bash
git clone https://github.com/<username>/HubermanLabQA.git
cd HubermanLabQA
```

Then install the necessary dependencies:
```bash
pip install -r requirements.txt
```

## Environment Variables
Before you begin, you should set up your environment variables.

1. Create a .env file in your project root directory.
2. You can set environment variables through the CLI tool using the --set-env command. This command takes two arguments: the variable name and the variable value. For example, to set the OPENAI_KEY, run the following command:
```bash
python main.py --set-env OPENAI_API_KEY your_openai_key
```

**Note:** Replace `your_openai_key` with your actual OpenAI API key.

## Usage
#### Setting up output directories

You can setup the directories to which the outputs will be saved. If the paths are not setup, the default paths will be taken.

```bash
python main.py --set-output-paths path/to/qa_output path/to/images
```

#### Question Answering Mode

In this mode, the CLI tool returns the answer and relevant segments for a given question.
```bash
python main.py --question "What is the impact of sleep on cognitive function?"
```

You can also customize the parameters of the QA engine:
```bash
python main.py --question "What is the impact of sleep on cognitive function?" --embedding_model sbert --n_search 20 --n_relevant_segments 3 --llm_model gpt-3.5-turbo --temperature 0
```

#### Resource Searching Mode

In this mode, the CLI tool returns only the relevant resources, without checking if they are relevant nor providing a final answer.
```bash
python main.py --resources "What is the impact of sleep on cognitive function?"
```

## Notes
- In the resource searching mode, the tool will not require calling the OpenAI API, thus it won't incur any costs and won't require providing the OPENAI_API_KEY.
- The question answering mode requires calls to the OpenAI API to check the relevance of the segments and construct a final answer.