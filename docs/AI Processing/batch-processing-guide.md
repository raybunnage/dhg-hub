# Comprehensive Guide to Message Batching with PDFService

## Introduction for Beginners

When you're working with lots of PDFs, processing them one at a time can be slow and expensive. Message batching is like having a team of workers process multiple PDFs at once, instead of having one person do them one after another. This guide will show you how to use message batching effectively, even if you're new to programming.

## Why Use Message Batching?

1. **Save Money**: It costs 50% less than processing PDFs one at a time
2. **Process More**: You can handle up to 100,000 PDFs in one batch
3. **Work Smarter**: The system works on multiple PDFs at the same time
4. **Flexible Use**: Works with all kinds of PDF tasks (reading, analyzing, extracting text)

## Important Numbers to Remember

- You can process up to 100,000 PDFs in one batch
- Your batch data must be smaller than 256 MB (megabytes)
- The system will work on your batch for up to 24 hours
- You can access your results for 29 days after creating the batch
- Each batch only works within your specific workspace (like your own private room)

## Pricing Guide (Cost per Million Tokens)

Different models have different costs. Here's what you'll pay:

| Model               | Input Cost | Output Cost |
|--------------------|------------|-------------|
| Claude 3.5 Sonnet  | $1.50      | $7.50      |
| Claude 3 Opus      | $7.50      | $37.50     |
| Claude 3 Haiku     | $0.125     | $0.625     |

## Step-by-Step Implementation Guide

### Step 1: Setting Up Your Project

First, you'll need to import the necessary libraries and set up your basic structure. Here's how:

```python
# Import required libraries
import anthropic
import asyncio
from datetime import datetime
from typing import List, Dict, Any

# You'll need these specific imports for message batching
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request
```

### Step 2: Creating a Basic PDFProcessor Class

Let's create a class that will handle our PDF processing:

```python
class PDFProcessor:
    def __init__(self, api_key: str):
        """
        Initialize the PDF processor with your API key
        
        Args:
            api_key (str): Your Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        self.batch_tracking = {}  # Store information about our batches
        
    def _generate_custom_id(self, pdf_name: str) -> str:
        """
        Create a unique ID for each PDF request
        
        Args:
            pdf_name (str): Name of the PDF file
            
        Returns:
            str: A unique identifier for this PDF request
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"pdf_{pdf_name}_{timestamp}"
```

### Step 3: Creating a Batch

Here's how to create a batch of PDF processing requests:

```python
def create_pdf_batch(self, pdf_list: List[Dict[str, Any]]) -> str:
    """
    Create a batch of PDF processing requests
    
    Args:
        pdf_list: List of dictionaries containing PDF information
                 Each dictionary should have 'name' and 'content' keys
    
    Returns:
        str: The batch ID for tracking
    
    Example:
        pdf_list = [
            {
                'name': 'document1.pdf',
                'content': 'What is the main topic of this PDF?'
            },
            {
                'name': 'document2.pdf',
                'content': 'Summarize this PDF.'
            }
        ]
    """
    try:
        # Create a list of requests for each PDF
        batch_requests = []
        
        for pdf_info in pdf_list:
            # Generate a unique ID for this request
            custom_id = self._generate_custom_id(pdf_info['name'])
            
            # Create the request object
            request = Request(
                custom_id=custom_id,
                params=MessageCreateParamsNonStreaming(
                    model="claude-3-5-sonnet-20241022",  # You can change the model
                    max_tokens=1024,  # Adjust based on your needs
                    messages=[{
                        "role": "user",
                        "content": pdf_info['content']
                    }]
                )
            )
            
            batch_requests.append(request)
        
        # Create the batch with all requests
        batch = self.client.messages.batches.create(requests=batch_requests)
        
        # Store batch information for tracking
        self.batch_tracking[batch.id] = {
            "created_at": datetime.now(),
            "status": "in_progress",
            "total_requests": len(pdf_list)
        }
        
        return batch.id
        
    except Exception as e:
        print(f"Error creating batch: {str(e)}")
        raise
```

### Step 4: Tracking Batch Progress

You'll want to know how your batch is progressing. Here's how to check:

```python
def check_batch_status(self, batch_id: str) -> Dict[str, Any]:
    """
    Check the current status of a batch
    
    Args:
        batch_id (str): The ID of the batch to check
        
    Returns:
        Dict containing status information
        
    Example output:
        {
            'status': 'in_progress',
            'processed': 45,
            'total': 100,
            'errors': 2,
            'created_at': '2024-01-11T10:00:00Z'
        }
    """
    try:
        # Get the batch information from the API
        batch = self.client.messages.batches.retrieve(batch_id)
        
        # Create a friendly status report
        status_report = {
            'status': batch.processing_status,
            'processed': batch.request_counts.succeeded,
            'total': self.batch_tracking[batch_id]['total_requests'],
            'errors': batch.request_counts.errored,
            'created_at': self.batch_tracking[batch_id]['created_at'].isoformat()
        }
        
        return status_report
        
    except Exception as e:
        print(f"Error checking batch status: {str(e)}")
        raise
```

### Step 5: Getting Batch Results

Once your batch is complete, here's how to get the results:

```python
async def get_batch_results(self, batch_id: str) -> List[Dict[str, Any]]:
    """
    Get the results from a completed batch
    
    Args:
        batch_id (str): The ID of the batch to get results from
        
    Returns:
        List of dictionaries containing results for each PDF
        
    Example output:
        [
            {
                'pdf_name': 'document1.pdf',
                'status': 'success',
                'result': 'The main topic is artificial intelligence...'
            },
            {
                'pdf_name': 'document2.pdf',
                'status': 'error',
                'error': 'Failed to process PDF'
            }
        ]
    """
    results = []
    
    try:
        # Stream the results to handle large batches efficiently
        for result in self.client.messages.batches.results(batch_id):
            # Extract the PDF name from the custom_id
            pdf_name = result.custom_id.split('_')[1]  # Based on our custom_id format
            
            # Handle different result types
            if result.result.type == "succeeded":
                # Success case
                results.append({
                    'pdf_name': pdf_name,
                    'status': 'success',
                    'result': result.result.message.content[0].text
                })
            elif result.result.type == "errored":
                # Error case
                results.append({
                    'pdf_name': pdf_name,
                    'status': 'error',
                    'error': str(result.result.error)
                })
            elif result.result.type == "expired":
                # Expired case
                results.append({
                    'pdf_name': pdf_name,
                    'status': 'expired',
                    'error': 'Request expired before processing'
                })
                
        return results
        
    except Exception as e:
        print(f"Error getting batch results: {str(e)}")
        raise
```

### Step 6: Putting It All Together

Here's how to use all these pieces together:

```python
async def process_pdf_batch(self, pdf_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process a batch of PDFs from start to finish
    
    Args:
        pdf_list: List of dictionaries containing PDF information
        
    Returns:
        List of dictionaries containing results
    """
    try:
        # Step 1: Create the batch
        batch_id = self.create_pdf_batch(pdf_list)
        print(f"Created batch with ID: {batch_id}")
        
        # Step 2: Wait for processing to complete
        while True:
            status = self.check_batch_status(batch_id)
            print(f"Batch status: {status['status']}")
            
            if status['status'] == "ended":
                break
                
            # Wait 30 seconds before checking again
            await asyncio.sleep(30)
        
        # Step 3: Get the results
        results = await self.get_batch_results(batch_id)
        return results
        
    except Exception as e:
        print(f"Error in batch processing: {str(e)}")
        raise
```

## Using the Code: A Complete Example

Here's how to use the PDFProcessor class we created:

```python
async def main():
    # Initialize the processor
    processor = PDFProcessor("your-api-key-here")
    
    # Prepare your PDF list
    pdf_list = [
        {
            'name': 'business_report.pdf',
            'content': 'Please summarize the key findings in this report.'
        },
        {
            'name': 'technical_specs.pdf',
            'content': 'What are the main technical requirements listed?'
        }
    ]
    
    try:
        # Process the batch
        results = await processor.process_pdf_batch(pdf_list)
        
        # Print results
        for result in results:
            print(f"\nResults for {result['pdf_name']}:")
            if result['status'] == 'success':
                print(f"Analysis: {result['result']}")
            else:
                print(f"Error: {result['error']}")
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the program
if __name__ == "__main__":
    asyncio.run(main())
```

## Common Problems and Solutions

### 1. Batch Too Large
```python
# Bad: Trying to process too many PDFs at once
pdf_list = [generate_pdfs() for _ in range(200000)]  # Too many!

# Good: Break into smaller batches
def process_large_dataset(pdf_list):
    batch_size = 50000
    for i in range(0, len(pdf_list), batch_size):
        batch = pdf_list[i:i + batch_size]
        # Process this batch
```

### 2. Handling Timeouts
```python
# Bad: No timeout handling
while True:
    status = check_batch_status(batch_id)
    if status['status'] == "ended":
        break

# Good: Add timeout handling
async def check_with_timeout(batch_id, max_hours=24):
    start_time = datetime.now()
    while True:
        if (datetime.now() - start_time).total_hours() > max_hours:
            raise TimeoutError("Batch processing exceeded 24 hours")
        # Check status...
        await asyncio.sleep(30)
```

## Tips for Success

1. **Start Small**: Begin with a small batch (5-10 PDFs) to test your setup
2. **Monitor Progress**: Regularly check batch status and log progress
3. **Handle Errors**: Always implement error handling and retries
4. **Save Results**: Store results as you get them, don't wait for everything to finish
5. **Test First**: Try processing one PDF before attempting a batch

## Security Best Practices

1. **API Keys**: Never share your API key or commit it to code
2. **Data Privacy**: Be careful with sensitive PDF content
3. **Error Logs**: Don't log sensitive information from PDFs
4. **Access Control**: Limit who can access batch results

## Performance Tips

1. **Batch Size**: Start with smaller batches (1000-5000) and increase as needed
2. **Memory Usage**: Stream results instead of loading everything at once
3. **Error Handling**: Implement exponential backoff for retries
4. **Monitoring**: Keep track of processing times and success rates

Remember: Processing speed depends on many factors including PDF size, complexity, and system load. Start conservatively and adjust based on your needs.

## Conclusion

Message batching is a powerful way to process many PDFs efficiently and at lower cost. Start with the basic implementation above and customize it for your specific needs. Remember to handle errors appropriately and monitor your batches for best results.

Need help? You can always:
- Check the Anthropic documentation
- Look at your batch status in the console
- Monitor your API usage
- Implement proper logging for debugging

Good luck with your PDF processing!