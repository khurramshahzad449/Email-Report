# Sales Call Analysis Agent

This agent analyzes sales call transcripts using AWS Bedrock's Claude model to evaluate sales representatives' performance against an ideal pitch template. It provides detailed feedback on strengths, areas for improvement, and specific recommendations.

## Features

- Analyzes sales call transcripts using AWS Bedrock's Claude 3 Sonnet model
- Evaluates performance against a customizable ideal pitch template
- Provides detailed analysis including:
  - Step-by-step analysis process with reasoning
  - Strengths and areas for improvement
  - Key points covered and missed
  - Specific recommendations with context
- Generates formatted email reports
- Supports custom transcript input

## Prerequisites

- Python 3.7 or higher
- AWS Account with Bedrock access
- AWS credentials with appropriate permissions

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd sales-call-analyzer
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your AWS credentials:

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
```

4. (Optional) Customize the ideal pitch template in `config.py`:

```python
IDEAL_PITCH_TEMPLATE = """
Your custom pitch template here...
"""
```

## Usage

### Basic Usage

Run the script with a transcript file:

```bash
python main.py --transcript sample_transcript.txt --sales-rep "John" --customer "Bob" --duration "30 minutes" --output "analysis_report.txt"
```

### Command Line Arguments

- `--transcript`: Path to the transcript file (required)
- `--sales-rep`: Name of the sales representative (required)
- `--customer`: Name of the customer (required)
- `--duration`: Duration of the call (optional, defaults to "45 minutes")
- `--output`: Output file path for the report (optional, defaults to "analysis_report.txt")

### Example Transcript Format

Create a text file with your transcript in the following format:

```
Sales Rep: Hello, I'm John from TechCorp...
Customer: Hi John, thanks for coming in...
Sales Rep: I'd like to show you how our solution can help...
```

## Output

The script generates a detailed report in the specified output file containing:

- Call details
- Analysis process with reasoning
- Strengths
- Areas for improvement
- Key points covered
- Missing key points
- Specific recommendations

## Customization

### Ideal Pitch Template

Edit the `IDEAL_PITCH_TEMPLATE` in `config.py` to match your company's sales pitch requirements.

### Analysis Parameters

Adjust the `ANALYSIS_PARAMETERS` in `config.py` to modify:

- Confidence thresholds
- Maximum allowed missing points
- Required sections for analysis

### Email Template

Modify the `EMAIL_TEMPLATE` in `config.py` to customize the report format.

## Troubleshooting

1. **AWS Credentials Error**

   - Verify your AWS credentials in the `.env` file
   - Ensure you have Bedrock access enabled in your AWS account

2. **Transcript File Error**

   - Check if the transcript file exists and is readable
   - Ensure the file is properly formatted

3. **Analysis Issues**
   - Verify the transcript is clear and readable
   - Check if the ideal pitch template is properly configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
