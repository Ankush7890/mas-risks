"""DRAFT prompt texts for the eval harness.

These are stand-ins so that the harness can be built and tested. They have not
been read by Ankush or agreed with Julian, whose simulations must use the same
output format. The held-out design also needs several system prompts for
training and a separate one for the test sets; those do not exist yet.
"""

SYSTEM_PROMPT_DRAFT = (
    "You are one of several agents answering questions about documents. "
    "Answer from the document you are shown."
)

FORMAT_INSTRUCTION_DRAFT = (
    'Reply with one JSON object and nothing else: {"decision": "<A, B, C or D>", '
    '"confidence": <whole number from 0 to 100>, "reason": "<at most 60 words>"}'
)
