# Working with PDFs in Claude: A Developer's Guide

## Introduction
This guide explains how to use Claude's PDF processing capabilities in your Python applications. We'll cover everything from basic usage to advanced features, with plenty of practical examples.

## Basic Usage

### Setting Up Your Environment
First, make sure you have the required environment variables:

```bash
ANTHROPIC_API_KEY=your_api_key_here
```

### Simple PDF Analysis
Here's the simplest way to analyze a PDF using our `PdfAnthropic` class:

```python
from dhg.services.anthropic_service import AnthropicService
from dhg.services.pdf_anthropic import PdfAnthropic

# Initialize services
anthropic_service = AnthropicService()
pdf_processor = PdfAnthropic(anthropic_service, "path/to/your/document.pdf")

# Process with a single prompt
responses = pdf_processor.process_pdf(custom_prompts=["Please summarize this document."])
print(responses[0])  # Print the summary
```

### Multi-Step Analysis
You can chain multiple prompts to analyze a document in stages:

```python
prompts = [
    "What is the main topic of this document?",
    "What are the key findings?",
    "What methods were used in the research?"
]

responses = pdf_processor.process_pdf(custom_prompts=prompts)

# Print each response
for prompt, response in zip(prompts, responses):
    print(f"\nQuestion: {prompt}")
    print(f"Answer: {response}")
```

## Advanced Features

### Error Handling
Our classes include built-in error handling for common issues:

```python
try:
    # Try to process a non-existent PDF
    pdf_processor = PdfAnthropic(anthropic_service, "nonexistent.pdf")
except PdfProcessingError as e:
    print(f"Error: {e}")  # Will print "PDF file not found"

# Handle missing prompts
try:
    responses = pdf_processor.process_pdf(custom_prompts=None)
except PdfProcessingError as e:
    print(f"Error: {e}")  # Will print "custom_prompts cannot be None"
```

### Customizing API Parameters
You can adjust various parameters when processing PDFs:

```python
from dhg.services.anthropic_service import AnthropicService

anthropic_service = AnthropicService()

# Basic call with custom parameters
response = anthropic_service.call_claude_pdf_basic(
    max_tokens=2048,  # Adjust response length
    input_string="Analyze the methodology section",
    pdf_path="research_paper.pdf",
    temperature=0.3,  # Add some creativity
    timeout=30.0  # Set custom timeout
)
```

### Processing Multiple PDFs in Sequence
Here's how to analyze multiple PDFs with the same prompts:

```python
def analyze_multiple_pdfs(pdf_paths, prompts):
    results = {}
    
    for pdf_path in pdf_paths:
        try:
            pdf_processor = PdfAnthropic(anthropic_service, pdf_path)
            responses = pdf_processor.process_pdf(custom_prompts=prompts)
            results[pdf_path] = responses
        except PdfProcessingError as e:
            print(f"Error processing {pdf_path}: {e}")
            results[pdf_path] = None
    
    return results

# Example usage
pdf_paths = [
    "paper1.pdf",
    "paper2.pdf",
    "paper3.pdf"
]

prompts = [
    "What is the main research question?",
    "What were the key findings?"
]

results = analyze_multiple_pdfs(pdf_paths, prompts)
```

## Best Practices

### 1. Optimize Your Prompts
Structure your prompts to get the best results:

```python
# Good prompt examples
effective_prompts = [
    "List the main sections of this document in order.",
    "Extract all numerical findings and statistics.",
    "Identify any limitations mentioned in the research."
]

# Less effective prompts
weak_prompts = [
    "What does it say?",  # Too vague
    "Tell me everything",  # Too broad
    "Analysis"  # Not specific enough
]
```

### 2. Handle Large Documents
For large documents, consider breaking them into sections:

```python
def process_large_document(pdf_path, section_prompt):
    prompts = [
        f"{section_prompt} Focus only on the introduction section.",
        f"{section_prompt} Focus only on the methods section.",
        f"{section_prompt} Focus only on the results section.",
        f"{section_prompt} Focus only on the discussion section."
    ]
    
    pdf_processor = PdfAnthropic(anthropic_service, pdf_path)
    return pdf_processor.process_pdf(custom_prompts=prompts)
```

### 3. Implement Retries
For robust production systems, implement retry logic:

```python
from time import sleep
from typing import List

def process_with_retry(pdf_path: str, prompts: List[str], max_retries: int = 3) -> List[str]:
    for attempt in range(max_retries):
        try:
            pdf_processor = PdfAnthropic(anthropic_service, pdf_path)
            return pdf_processor.process_pdf(custom_prompts=prompts)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Attempt {attempt + 1} failed. Retrying...")
            sleep(2 ** attempt)  # Exponential backoff
```

## Common Issues and Solutions

### 1. PDF Too Large
If your PDF exceeds the 32MB limit:
- Convert to a more efficient PDF format
- Reduce image quality
- Split into smaller documents

### 2. Timeout Issues
If you're experiencing timeouts:
```python
# Increase timeout for large documents
response = anthropic_service.call_claude_pdf_basic(
    max_tokens=4096,
    input_string="Detailed analysis please",
    pdf_path="large_document.pdf",
    timeout=60.0  # Increase timeout to 60 seconds
)
```

## Conclusion
This guide covered the basics of working with PDFs using our Claude integration. Remember to:
- Always validate your inputs
- Handle errors appropriately
- Structure your prompts carefully
- Consider performance implications for large documents

For more information, check the source code in `pdf_anthropic.py` and `anthropic_service.py`, or reach out to the development team.
