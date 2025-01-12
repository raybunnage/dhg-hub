# Comprehensive Prompt Engineering Guide

## Core Principles

### Clear and Direct Communication
- Treat interactions with Claude like working with a brilliant but new employee who needs explicit context
- Provide contextual information about:
  - Task purpose and end goals
  - Target audience
  - Workflow context
  - Success criteria
- Use sequential steps and specific instructions

#### Example: Unclear vs Clear Prompting

❌ Unclear Prompt:
```
Write marketing copy for our product.
```

✅ Clear Prompt:
```
Write marketing copy for our enterprise SaaS product with these specifications:
- Target audience: IT managers at Fortune 500 companies
- Key features to highlight: AI-powered security, real-time collaboration, compliance tools
- Tone: Professional but approachable
- Length: 200-250 words
- Include: One customer quote and a clear call-to-action
- Purpose: For use in email campaigns targeting existing leads
```

### Using Examples (Multishot Prompting)
- Include 3-5 diverse examples to demonstrate patterns
- Examples should be:
  - Relevant to your use case
  - Cover edge cases and variations
  - Use clear structure (e.g., XML tags)
- More examples generally lead to better performance

#### Customer Service Response Examples
```
<examples>
<example>
Input: My account was charged twice this month. Please help!
Response: I understand how frustrating unexpected charges can be. I've looked into your account and confirmed there was a duplicate charge on [DATE]. I've initiated a refund for the extra charge, which should appear in 3-5 business days. I'm also adding a $10 credit to your account for the inconvenience.
Category: Billing
Priority: High
Follow-up: Monitor refund status
</example>

<example>
Input: How do I export my data to Excel?
Response: I'll guide you through exporting your data to Excel:
1. Go to Dashboard > Reports
2. Click the "Export" button in the top right
3. Select "Excel Format (.xlsx)"
4. Choose your date range
5. Click "Generate Export"
The file will download automatically. Let me know if you need any clarification!
Category: Technical Support
Priority: Low
Follow-up: None needed
</example>

<example>
Input: Your competitor offers this feature for free. Why should I pay?
Response: I appreciate you bringing this to my attention. While [Competitor] does offer a basic version of this feature, our implementation includes:
- Advanced encryption
- Custom workflows
- 24/7 premium support
- Enterprise compliance features
I'd be happy to set up a demo to show you these additional capabilities in action.
Category: Sales Support
Priority: Medium
Follow-up: Schedule demo
</example>
</examples>
```

### Chain of Thought (CoT) Prompting

CoT is particularly effective for:
- Complex mathematical calculations
- Multi-step analysis
- Decision-making with multiple factors
- Logic puzzles and reasoning tasks
- Document analysis and summarization

#### Three Levels of CoT Implementation:

1. **Basic CoT**
```
Think through this step-by-step:
What would be the total cost of a project that requires:
- 3 developers at $100/hour for 4 weeks
- 1 designer at $80/hour for 2 weeks
- Software licenses costing $2000/month
Assume a 40-hour work week.
```

2. **Guided CoT**
```
To calculate the project cost:
1. First, calculate developer costs:
   - Hours per week × Number of weeks × Hourly rate × Number of developers
2. Then, calculate designer costs:
   - Hours per week × Number of weeks × Hourly rate
3. Add software license costs:
   - Monthly cost × Number of months
4. Sum all costs
5. Add 10% contingency buffer
Please show your work for each step.
```

3. **Structured CoT with XML Tags**
```
<task>
Calculate optimal investment allocation for retirement portfolio with:
- Investment amount: $100,000
- Time horizon: 25 years
- Risk tolerance: Moderate
- Required annual return: 7%
</task>

<thinking>
1. Analyze risk profile:
   - Moderate risk suggests 60/40 stock/bond split
   - Need to consider inflation (historical avg 2-3%)
   
2. Calculate required growth:
   - Target: $100,000 * (1.07)^25 = $542,743
   - Need to outpace inflation, so real return of 4-5%

3. Assess allocation options:
   - Stock allocation (60%): $60,000
     * 70% US stocks ($42,000)
     * 30% International stocks ($18,000)
   - Bond allocation (40%): $40,000
     * 80% Government bonds ($32,000)
     * 20% Corporate bonds ($8,000)

4. Consider rebalancing:
   - Annual rebalancing to maintain ratios
   - Dividend reinvestment plan
</thinking>

<answer>
Recommended allocation:
- US Stocks: 42% ($42,000)
- International Stocks: 18% ($18,000)
- Government Bonds: 32% ($32,000)
- Corporate Bonds: 8% ($8,000)

Additional recommendations:
1. Set up automatic annual rebalancing
2. Enable dividend reinvestment
3. Review allocation every 5 years or upon major life events
</answer>
```

## Evaluation Guidelines

### Success Criteria
Success criteria should be SMART (Specific, Measurable, Achievable, Relevant, Time-bound)

#### Example Criteria Framework:
```
Task: Customer Service Chatbot

1. Response Accuracy
   - 95% correct information in responses
   - < 1% false information
   - 100% compliance with company policies

2. Response Time
   - 90% of responses within 2 seconds
   - No response over 5 seconds

3. User Satisfaction
   - CSAT score > 4.5/5
   - < 5% escalation rate
   - > 80% first-contact resolution

4. Language Quality
   - Grammar score > 95%
   - Tone alignment > 90%
   - Brand voice compliance > 95%

5. Safety & Ethics
   - Zero PII exposures
   - 100% compliance with ethical guidelines
   - < 0.1% toxic/harmful responses
```

### Testing Approach

#### Code-Based Grading Example
```python
def evaluate_response(response, golden_answer):
    # Basic exact match
    if response.strip().lower() == golden_answer.strip().lower():
        return 1.0
    
    # Partial matching
    score = 0.0
    required_elements = [
        "pricing",
        "features",
        "timeline"
    ]
    
    for element in required_elements:
        if element in response.lower():
            score += 0.33
            
    # Check for prohibited elements
    prohibited = ["confidential", "internal"]
    for word in prohibited:
        if word in response.lower():
            score = 0.0
            break
            
    return round(score, 2)
```

#### LLM-Based Grading Example
```
<grading_rubric>
Evaluate the following customer service response on a scale of 1-5:

Criteria:
1. Accuracy (1-5):
   - 5: All information correct and verified
   - 3: Mostly correct with minor inaccuracies
   - 1: Contains major errors

2. Tone (1-5):
   - 5: Perfect professional, empathetic tone
   - 3: Acceptable but could be improved
   - 1: Inappropriate or unprofessional

3. Completeness (1-5):
   - 5: Addresses all aspects of the query
   - 3: Addresses main points but misses details
   - 1: Fails to address key aspects

4. Policy Compliance (1-5):
   - 5: Fully compliant with all policies
   - 3: Minor policy deviations
   - 1: Major policy violations

Provide a score for each criterion and an overall average.
Include brief justification for each score.
</grading_rubric>
```

### Advanced Testing Strategies

#### A/B Testing Format
```
<test_case>
Version A: [Original prompt]
Version B: [Modified prompt with one change]

Test metrics:
1. Response accuracy
2. Response time
3. Token usage
4. User satisfaction

Sample size: 1000 queries per version
Duration: 1 week
Success criteria: 95% confidence interval
</test_case>
```

#### Edge Case Testing
```
<edge_cases>
1. Empty inputs
2. Extremely long inputs (>10k tokens)
3. Non-English characters
4. Special characters and symbols
5. Technical jargon
6. Multiple questions in one prompt
7. Ambiguous requests
8. Boundary conditions
9. Invalid formats
10. Rate limiting scenarios
</edge_cases>
```

## Best Practices for Production

### Error Handling
- Implement retry logic with exponential backoff
- Set up monitoring for response quality
- Create fallback responses for common failure modes
- Log and analyze error patterns

### Performance Optimization
- Cache common responses
- Batch similar requests
- Implement response streaming for long outputs
- Use efficient token management

### Monitoring and Maintenance
- Track key metrics:
  - Response accuracy
  - Latency
  - Token usage
  - Error rates
  - User satisfaction
- Regular prompt refinement based on data
- A/B testing for major changes
- Continuous evaluation against success criteria

## Resources and Tools
- [Anthropic Documentation](https://docs.anthropic.com/)
- Claude API Reference
- Evaluation frameworks
- Prompt templates and examples

_This guide is based on Anthropic's documentation and best practices for working with Claude and other LLMs. For the most up-to-date information, always refer to the official documentation._