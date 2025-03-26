import boto3
import json
import argparse
from datetime import datetime
from config import *
from jinja2 import Template

class ClaudeAnalyzer:
    def __init__(self):
        self.bedrock = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )

    def analyze_transcript(self, transcript, ideal_pitch):
        prompt = f"""You are an expert sales coach analyzing sales call transcripts.
        Your task is to analyze the transcript and ensure that the key points have been presented to the buyer and provide detailed feedback.
        Focus on identifying points that were covered, points that were missed, the effectiveness of the pitch based on the customer's response.
        Provide your analysis in a structured format with clear sections.
        First, let's understand the points to be covered in the pitch:
        {ideal_pitch}
        Now, let's analyze this call transcript:
        {transcript}
        Please provide your analysis in the following JSON format, including your thinking process:
        {{
            "analysis_steps": [
                {{
                    "step": "Initial Assessment",
                    "thinking": "Your thoughts on the overall call structure and flow",
                    "observations": ["Key observations about the call"]
                }},
                {{
                    "step": "Key Pitch Point Coverage",
                    "thinking": "How well did the sales rep cover the key points during the conversation",
                    "observations": ["Specific points about coverage of key points covered and missed"]
                }},
                {{
                    "step": "Effectiveness Analysis",
                    "thinking": "Analysis of the sales rep's effectiveness",
                    "observations": ["Observations about effectiveness"]
                }}
            ],
            "strengths": ["list of strengths with brief explanations"],
            "improvements": ["list of areas for improvement with specific examples"],
            "covered_points": ["list of key points that were covered with context"],
            "missing_points": ["list of key points that were missed with impact analysis"],
            "recommendations": ["list of specific recommendations with reasoning"]
        }}"""
        
        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 3000,
                "temperature": 0.7,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        response_body = json.loads(response['body'].read())
        return json.loads(response_body['content'][0]['text'])

class ReportGenerator:
    def __init__(self):
        self.email_template = Template(EMAIL_TEMPLATE)

    def generate_email(self, analysis_results, call_details):
        # Format analysis steps
        analysis_steps = ""
        for step in analysis_results['analysis_steps']:
            analysis_steps += f"\n{step['step']}:\n"
            analysis_steps += f"Thinking: {step['thinking']}\n"
            analysis_steps += "Observations:\n" + "\n".join(f"- {obs}" for obs in step['observations']) + "\n"

        # Create template variables
        template_vars = {
            'call_date': call_details['date'],
            'sales_rep_name': call_details['sales_rep'],
            'customer_name': call_details['customer'],
            'call_duration': call_details['duration'],
            'analysis_steps': analysis_steps,
            'strengths': '\n'.join(f"- {s}" for s in analysis_results['strengths']),
            'improvements': '\n'.join(f"- {i}" for i in analysis_results['improvements']),
            'covered_points': '\n'.join(f"- {p}" for p in analysis_results['covered_points']),
            'missing_points': '\n'.join(f"- {p}" for p in analysis_results['missing_points']),
            'recommendations': '\n'.join(f"- {r}" for r in analysis_results['recommendations'])
        }

        # Render the template
        return self.email_template.render(**template_vars)

def read_transcript(file_path):
    """Read transcript from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading transcript file: {e}")
        return None

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Analyze sales call transcript using AWS Bedrock Claude')
    parser.add_argument('--transcript', type=str, required=True, help='Path to the transcript file')
    parser.add_argument('--sales-rep', type=str, required=True, help='Name of the sales representative')
    parser.add_argument('--customer', type=str, required=True, help='Name of the customer')
    parser.add_argument('--duration', type=str, default='45 minutes', help='Duration of the call')
    parser.add_argument('--output', type=str, default='analysis_report.txt', help='Output file path for the report')
    
    args = parser.parse_args()

    # Read transcript
    transcript = read_transcript(args.transcript)
    if not transcript:
        print("Failed to read transcript. Exiting...")
        return

    # Initialize analyzer and report generator
    claude_analyzer = ClaudeAnalyzer()
    report_generator = ReportGenerator()

    # Call details
    call_details = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'sales_rep': args.sales_rep,
        'customer': args.customer,
        'duration': args.duration
    }

    print("Analyzing transcript...")
    # Analyze transcript with Claude
    analysis_results = claude_analyzer.analyze_transcript(
        transcript,
        IDEAL_PITCH_TEMPLATE
    )

    print("Generating report...")
    # Generate email report
    email_content = report_generator.generate_email(
        analysis_results,
        call_details
    )

    # Save the report
    with open(args.output, 'w') as f:
        f.write(email_content)
    
    print(f"Analysis complete! Report saved to {args.output}")

if __name__ == "__main__":
    main()