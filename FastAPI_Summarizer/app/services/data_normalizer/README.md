Notes for integration with an LLM log summarizer:

Your summarizer should only ever receive llm_payload from this service.

normalized_log can be stored back into SIEM/SOAR or used for analytics.

Extend FIELD_MAP, FULLY_SENSITIVE_FIELDS, IDENTIFIER_FIELDS, and regexes to match your MSSP environments and regulatory constraints.