import boto3
import json
import argparse
import requests
import time
from datetime import datetime
from config import *
from jinja2 import Template
from docx import Document
import hmac
import hashlib
import base64

class ClaudeAnalyzer:
    def __init__(self):
        self.bedrock = boto3.client(
            'bedrock-runtime',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
            verify=False
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
            "objections": ["list of objections that were raised by the customer"],
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
            'objections': '\n'.join(f"- {p}" for p in analysis_results['objections']),
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

def read_word_document(file_path):
    """Read content from a Word document, including both paragraphs and tables."""
    try:
        doc = Document(file_path)
        full_text = []
        
        # Read paragraphs
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                full_text.append(paragraph.text)
        
        # Read tables
        for table in doc.tables:
            for row in table.rows:
                row_text = []
                for cell in row.cells:
                    if cell.text.strip():
                        row_text.append(cell.text.strip())
                if row_text:  # Only add non-empty rows
                    full_text.append(" | ".join(row_text))
        
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading Word document: {e}")
        return None

def get_gong_signature(access_key, secret_key, timestamp, request_id, method, path, body=""):
    """Generate signature for Gong API request."""
    string_to_sign = f"{timestamp}\n{request_id}\n{method}\n{path}\n{body}"
    signature = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

def fetch_gong_transcript(conversation_id):
    """Fetch transcript from Gong API."""
    try:
        timestamp = str(int(time.time() * 1000))
        request_id = str(int(time.time() * 1000))
        path = "/v2/calls/transcript"  # Correct endpoint
        method = "POST"
        
        # Request body
        body = {
            "filter": {
                "callIds": [conversation_id]
            }
        }
        body_json = json.dumps(body)
        
        # Generate signature
        signature = get_gong_signature(
            GONG_ACCESS_KEY,
            GONG_SECRET_KEY,
            timestamp,
            request_id,
            method,
            path,
            body_json
        )
        
        # Make request
        headers = {
            "Authorization": f"Basic {base64.b64encode(f'{GONG_ACCESS_KEY}:{GONG_SECRET_KEY}'.encode()).decode()}",
            "X-Gong-Timestamp": timestamp,
            "X-Gong-Request-Id": request_id,
            "X-Gong-Signature": signature,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{GONG_BASE_URL}{path}",
            headers=headers,
            json=body,  # This will automatically handle JSON encoding
            verify=False  # Disable SSL verification
        )
        
        # Print response details for debugging
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Raw response content: {response.text[:500]}...")  # Print first 500 chars of response
        
        if response.status_code == 200:
            try:
                data = response.json()
                # Extract transcript text from Gong response
                transcript = []
                
                # Get the first call transcript (since we're querying for a specific call ID)
                if data.get('callTranscripts') and len(data['callTranscripts']) > 0:
                    call_transcript = data['callTranscripts'][0]
                    
                    # Process each transcript section
                    for section in call_transcript.get('transcript', []):
                        topic = section.get('topic', '')
                        for sentence in section.get('sentences', []):
                            text = sentence.get('text', '')
                            if text:
                                # Format: [Topic] Speaker: Text
                                transcript.append(f"[{topic}] {text}")
                
                return '\n'.join(transcript)
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response: {e}")
                print(f"Full response content: {response.text}")
                return None
        else:
            print(f"Error fetching Gong transcript: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Error fetching Gong transcript: {e}")
        return None

def process_transcript(transcript, ideal_pitch, sales_rep, customer, duration, output_file):
    """Process a single transcript and generate a report."""
    if not transcript:
        print("Failed to read transcript. Skipping...")
        return False

    # Initialize analyzer and report generator
    claude_analyzer = ClaudeAnalyzer()
    report_generator = ReportGenerator()

    # Call details
    call_details = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'sales_rep': sales_rep,
        'customer': customer,
        'duration': duration
    }

    print("Analyzing transcript...")
    # Analyze transcript with Claude
    analysis_results = claude_analyzer.analyze_transcript(
        transcript,
        ideal_pitch
    )

    print("Generating report...")
    # Generate email report
    email_content = report_generator.generate_email(
        analysis_results,
        call_details
    )

    # Save the report
    with open(output_file, 'w') as f:
        f.write(email_content)
    
    print(f"Analysis complete! Report saved to {output_file}")
    return True

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Analyze sales call transcript using AWS Bedrock Claude')
    parser.add_argument('--transcript', type=str, help='Path to the transcript file (required if not using --gong-ids)')
    parser.add_argument('--ideal-pitch', type=str, required=True, help='Path to the Word document containing the ideal pitch')
    parser.add_argument('--sales-rep', type=str, required=True, help='Name of the sales representative')
    parser.add_argument('--customer', type=str, required=True, help='Name of the customer')
    parser.add_argument('--duration', type=str, default='45 minutes', help='Duration of the call')
    parser.add_argument('--output', type=str, default='analysis_report.txt', help='Output file path for the report')
    parser.add_argument('--gong-ids', type=str, help='Comma-separated list of Gong conversation IDs to analyze')
    
    args = parser.parse_args()

    # Validate arguments
    if not args.gong_ids and not args.transcript:
        print("Error: Either --transcript or --gong-ids must be provided")
        return

    # Read ideal pitch from Word document
    ideal_pitch = read_word_document(args.ideal_pitch)
    if not ideal_pitch:
        print("Failed to read ideal pitch document. Exiting...")
        return

    if args.gong_ids:
        # Process Gong transcripts
        gong_ids = [id.strip() for id in args.gong_ids.split(',')]
        for i, conversation_id in enumerate(gong_ids):
            print(f"\nProcessing Gong transcript {i+1}/{len(gong_ids)} (ID: {conversation_id})...")
            transcript = fetch_gong_transcript(conversation_id)
            output_file = f"analysis_report_{conversation_id}.txt"
            process_transcript(
                transcript,
                ideal_pitch,
                args.sales_rep,
                args.customer,
                args.duration,
                output_file
            )
    else:
        # Process local transcript
        transcript = read_transcript(args.transcript)
        process_transcript(
            transcript,
            ideal_pitch,
            args.sales_rep,
            args.customer,
            args.duration,
            args.output
        )

if __name__ == "__main__":
    main()