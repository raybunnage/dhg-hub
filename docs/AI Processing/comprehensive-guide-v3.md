# Comprehensive Claude Prompt Engineering Guide

## Table of Contents
1. [Core Principles](#core-principles)
2. [Long Context Best Practices](#long-context-best-practices)
3. [Using XML Tags](#using-xml-tags)
4. [Role Prompting](#role-prompting)
5. [Chain of Thought & Prompt Chaining](#chain-of-thought--prompt-chaining)
6. [Multishot Prompting](#multishot-prompting)
7. [Prefilling Responses](#prefilling-responses)
8. [Text Generation Capabilities](#text-generation-capabilities)
9. [Advanced Features](#advanced-features)
10. [Evaluation Guidelines](#evaluation-guidelines)
11. [Best Practices for Production](#best-practices-for-production)

## Long Context Best Practices

Claude's extended context window (200K tokens for Claude 3 models) enables handling complex, data-rich tasks. Here are essential tips for optimizing long context prompts:

### Document Organization
- Place long documents and inputs (~20K+ tokens) near the top of your prompt
- Put queries and instructions after the documents
- Structure content with XML tags for clarity

Example of organizing multiple documents:
```xml
<documents>
  <document index="1">
    <source>annual_report_2023.pdf</source>
    <document_content>
      [Annual Report Content]
    </document_content>
  </document>
  <document index="2">
    <source>competitor_analysis_q2.xlsx</source>
    <document_content>
      [Competitor Analysis Content]
    </document_content>
  </document>
</documents>

Analyze these documents to identify our competitive positioning. Focus on:
1. Market share trends
2. Product differentiation
3. Growth opportunities
```

### Grounding and Citation
- Ask Claude to quote relevant parts before analysis
- Use XML tags to structure quotes and analysis
- Reference specific sections of documents

Example of grounded analysis:
```xml
<task>
Review the financial reports and extract key performance metrics.
</task>

<quotes>
From annual_report_2023.pdf: "Revenue grew 32% YoY to $156M"
From competitor_analysis_q2.xlsx: "Market leader revenue: $412M (+18% YoY)"
</quotes>

<analysis>
Based on these figures, we can conclude:
1. Our growth rate (32%) outpaces the market leader (18%)
2. Current market share is approximately 27.5% ($156M/$568M total)
3. Growth trajectory suggests potential to reach 35% share by EOY
</analysis>
```

## Advanced Features

### Embeddings
Text embeddings enable semantic search and similarity analysis. Here are the key considerations and capabilities:

#### Available Models
```plaintext
Model          | Context Length | Dimensions  | Best For
---------------|---------------|-------------|----------
voyage-3-large | 32,000        | 1024/2048   | General purpose
voyage-3       | 32,000        | 1024        | Multilingual
voyage-3-lite  | 32,000        | 512         | Performance
voyage-code-3  | 32,000        | 1024        | Code retrieval
```

Example of using embeddings with Python:
```python
import voyageai

vo = voyageai.Client()

# Example documents
documents = [
    "The Mediterranean diet emphasizes fish and vegetables",
    "Photosynthesis converts light energy into glucose",
    "20th-century innovations centered on electronics"
]

# Create embeddings
doc_embeddings = vo.embed(
    documents, 
    model="voyage-3", 
    input_type="document"
).embeddings

# Example query
query = "What foods are part of healthy diets?"
query_embedding = vo.embed(
    [query], 
    model="voyage-3", 
    input_type="query"
).embeddings[0]

# Find most similar document
similarities = np.dot(doc_embeddings, query_embedding)
best_match = np.argmax(similarities)
print(documents[best_match])
```

### Vision Capabilities (Claude 3)

Claude 3 can analyze images with sophisticated understanding. Here are key features and best practices:

#### Image Requirements
- Supported formats: JPEG, PNG, GIF, WebP
- Maximum size: 8000x8000 pixels
- Optimal size: Up to 1568 pixels on longest edge
- Token usage: (width * height) / 750 tokens approximately

Example of vision API usage:
```python
import base64
import anthropic

# Prepare image
with open("image.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Describe this image in detail."
                }
            ],
        }
    ],
)
```

### Computer Use (Beta)

Claude can interact with computer interfaces through specialized tools. Here are the key components:

#### Available Tools
1. Computer Tool (`computer_20241022`)
   - Mouse and keyboard control
   - Screen reading and interaction
   
2. Text Editor Tool (`text_editor_20241022`)
   - Document editing
   - Text manipulation
   
3. Bash Tool (`bash_20241022`)
   - Command execution
   - File system operations

Example of computer use API:
```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {
            "type": "computer_20241022",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768
        },
        {
            "type": "text_editor_20241022",
            "name": "str_replace_editor"
        },
        {
            "type": "bash_20241022",
            "name": "bash"
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "Open a text editor and create a Python script that prints 'Hello World'"
        }
    ]
)
```

[Previous content from Evaluation Guidelines and Best Practices remains unchanged]

## Resources and Tools
- [Anthropic Documentation](https://docs.anthropic.com/)
- [Claude API Reference](https://docs.anthropic.com/claude/reference)
- [Embeddings Documentation](https://docs.anthropic.com/claude/docs/embeddings)
- [Vision Guide](https://docs.anthropic.com/claude/docs/vision)
- [Computer Use Guide](https://docs.anthropic.com/claude/docs/computer-use)

*Note: This guide is based on Anthropic's documentation and best practices. For the most up-to-date information, always refer to the official documentation.*