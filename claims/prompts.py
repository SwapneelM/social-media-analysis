"""
Prompts for factual claims extraction using GPT-4o.

Contains the system prompt, few-shot examples, and prompt construction
functions for extracting factual claims from social media posts.
"""

SYSTEM_PROMPT = """You are a factual claims extraction system. Your job is to analyze social media posts and extract specific factual claims — statements that can be verified as true or false.

Rules:
1. Extract ONLY factual claims, NOT opinions, questions, or subjective statements.
2. A factual claim is a statement asserting something is true about the world that can be verified.
3. For each claim, provide:
   - "claim_text": The extracted claim, rephrased as a clear statement
   - "confidence": Your confidence (0.0 to 1.0) that this IS a factual claim (not opinion)
   - "category": One of "science", "politics", "economics", "health", "technology", "society", "environment", "other"
   - "reasoning": Brief explanation of why you classified this as a factual claim
   - "source_quote": The exact quote from the post that contains this claim

4. If a post contains NO factual claims, return an empty array.
5. Return ONLY valid JSON. No markdown, no explanations outside the JSON.

Response format:
{"claims": [{"claim_text": "...", "confidence": 0.9, "category": "...", "reasoning": "...", "source_quote": "..."}]}"""


FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": 'Analyze this social media post for factual claims:\n\n"India\'s AI market is expected to reach $17 billion by 2027, according to a NASSCOM report. The government has invested ₹10,000 crore in the IndiaAI Mission."'
    },
    {
        "role": "assistant",
        "content": '{"claims": [{"claim_text": "India\'s AI market is expected to reach $17 billion by 2027", "confidence": 0.92, "category": "technology", "reasoning": "This is a specific, verifiable prediction attributed to NASSCOM. The dollar amount and timeline make it a concrete factual claim.", "source_quote": "India\'s AI market is expected to reach $17 billion by 2027, according to a NASSCOM report"}, {"claim_text": "The Indian government has invested ₹10,000 crore in the IndiaAI Mission", "confidence": 0.95, "category": "politics", "reasoning": "This is a specific financial figure about government spending that can be verified through official records.", "source_quote": "The government has invested ₹10,000 crore in the IndiaAI Mission"}]}'
    },
    {
        "role": "user",
        "content": 'Analyze this social media post for factual claims:\n\n"I think AI is going to be amazing for everyone! So excited about the future 🚀🔥"'
    },
    {
        "role": "assistant",
        "content": '{"claims": []}'
    },
    {
        "role": "user",
        "content": 'Analyze this social media post for factual claims:\n\n"OpenAI reportedly laid off 20% of its safety team last month. Some researchers say this could impact AI alignment research, though others disagree."'
    },
    {
        "role": "assistant",
        "content": '{"claims": [{"claim_text": "OpenAI laid off 20% of its safety team", "confidence": 0.78, "category": "technology", "reasoning": "The word \'reportedly\' introduces some uncertainty, but this is still a specific, verifiable factual claim about a corporate action with a concrete percentage.", "source_quote": "OpenAI reportedly laid off 20% of its safety team last month"}]}'
    },
    {
        "role": "user",
        "content": 'Analyze this social media post for factual claims:\n\n"Breaking: 3 million students in India now have access to AI-powered learning tools. The literacy rate in participating schools increased by 15%. Meanwhile, China has deployed AI tutors in 50,000 schools."'
    },
    {
        "role": "assistant",
        "content": '{"claims": [{"claim_text": "3 million students in India now have access to AI-powered learning tools", "confidence": 0.88, "category": "technology", "reasoning": "Specific number of students with a concrete claim about access to technology. Verifiable through education ministry data.", "source_quote": "3 million students in India now have access to AI-powered learning tools"}, {"claim_text": "The literacy rate in participating schools increased by 15%", "confidence": 0.82, "category": "society", "reasoning": "Specific percentage increase in a measurable metric. The vagueness of \'participating schools\' slightly reduces confidence.", "source_quote": "The literacy rate in participating schools increased by 15%"}, {"claim_text": "China has deployed AI tutors in 50,000 schools", "confidence": 0.85, "category": "technology", "reasoning": "Specific number of schools with a concrete action. Verifiable claim about Chinese education policy.", "source_quote": "China has deployed AI tutors in 50,000 schools"}]}'
    },
]


def build_extraction_prompt(post_text):
    """
    Build the full message list for claims extraction.

    Combines the system prompt, few-shot examples, and the target post
    into a messages array suitable for the OpenRouter chat completions API.

    Args:
        post_text: The social media post text to analyze.

    Returns:
        List of message dicts with 'role' and 'content' keys.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    messages.extend(FEW_SHOT_EXAMPLES)
    messages.append({
        "role": "user",
        "content": f"Analyze this social media post for factual claims:\n\n\"{post_text}\""
    })
    return messages
