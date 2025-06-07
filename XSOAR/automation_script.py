import demistomock as demisto
from CommonServerPython import *
from CommonServerUserPython import *

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import re
import string
from typing import Dict, List, Tuple, Any
import json

class EmailClassifier:
    def __init__(self):
        self.vectorizer = None
        self.classifier = None
        self.incident_types = {
            'phishing': ['phishing', 'suspicious_email', 'email_security'],
            'malware': ['malware', 'virus', 'trojan'],
            'data_breach': ['data_leak', 'breach', 'exfiltration'],
            'business_email_compromise': ['bec', 'ceo_fraud', 'wire_fraud'],
            'spam': ['spam', 'unwanted_email'],
            'suspicious_activity': ['anomaly', 'suspicious_behavior']
        }
    
    def preprocess_email_text(self, text: str) -> str:
        """
        Preprocess email text for feature extraction
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_email_features(self, email_data: Dict) -> Dict:
        """
        Extract comprehensive features from email
        """
        features = {}
        
        # Text content features
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        combined_text = f"{subject} {body}"
        
        # Basic text statistics
        features['subject_length'] = len(subject)
        features['body_length'] = len(body)
        features['total_length'] = len(combined_text)
        features['word_count'] = len(combined_text.split())
        
        # Sender features
        sender = email_data.get('sender', '')
        features['sender_external'] = 1 if '@' in sender and not any(domain in sender for domain in ['company.com', 'organization.org']) else 0
        
        # Attachment features
        attachments = email_data.get('attachments', [])
        features['has_attachments'] = 1 if attachments else 0
        features['attachment_count'] = len(attachments)
        
        # Suspicious keywords
        suspicious_keywords = [
            'urgent', 'verify', 'suspended', 'click here', 'act now',
            'wire transfer', 'bank account', 'social security',
            'password', 'login', 'account', 'confirm'
        ]
        
        text_lower = combined_text.lower()
        features['suspicious_keyword_count'] = sum(1 for keyword in suspicious_keywords if keyword in text_lower)
        
        # URL and link features
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, combined_text)
        features['url_count'] = len(urls)
        
        return features

def classify_email_content(email_data: Dict) -> Dict:
    """
    Main classification function using multiple approaches
    """
    classifier = EmailClassifier()
    
    # Extract features
    features = classifier.extract_email_features(email_data)
    
    # Approach 1: Rule-based classification
    rule_based_result = rule_based_classification(email_data, features)
    
    # Approach 2: ML-based classification
    ml_result = ml_based_classification(email_data, features)
    
    # Approach 3: GenAI classification
    genai_result = genai_classification(email_data)
    
    # Combine results with confidence scoring
    final_result = combine_classification_results(rule_based_result, ml_result, genai_result)
    
    return final_result

def rule_based_classification(email_data: Dict, features: Dict) -> Dict:
    """
    Rule-based classification using heuristics
    """
    subject = email_data.get('subject', '').lower()
    body = email_data.get('body', '').lower()
    combined_text = f"{subject} {body}"
    
    # Phishing indicators
    phishing_keywords = ['verify', 'suspended', 'click here', 'urgent action', 'account locked']
    phishing_score = sum(1 for keyword in phishing_keywords if keyword in combined_text)
    
    # BEC indicators
    bec_keywords = ['wire transfer', 'invoice', 'payment urgent', 'ceo', 'urgent request']
    bec_score = sum(1 for keyword in bec_keywords if keyword in combined_text)
    
    # Malware indicators
    malware_score = features.get('attachment_count', 0) * 2 if any(ext in str(email_data.get('attachments', [])) 
                                                                   for ext in ['.exe', '.zip', '.rar']) else 0
    
    scores = {
        'phishing': phishing_score,
        'business_email_compromise': bec_score,
        'malware': malware_score,
        'spam': features.get('suspicious_keyword_count', 0),
        'suspicious_activity': max(phishing_score, bec_score) if features.get('sender_external', 0) else 0
    }
    
    predicted_type = max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'
    confidence = min(max(scores.values()) / 10.0, 1.0)
    
    return {
        'incident_type': predicted_type,
        'confidence': confidence,
        'method': 'rule_based',
        'scores': scores
    }

def ml_based_classification(email_data: Dict, features: Dict) -> Dict:
    """
    Machine Learning based classification using TF-IDF and various algorithms
    """
    try:
        # Prepare text data
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        combined_text = f"{subject} {body}"
        
        # Load or train model (this would typically be pre-trained)
        model_data = load_trained_model()
        
        if model_data:
            vectorizer = model_data['vectorizer']
            classifier = model_data['classifier']
            
            # Vectorize the email text
            text_features = vectorizer.transform([combined_text])
            
            # Predict
            prediction = classifier.predict(text_features)[0]
            confidence = max(classifier.predict_proba(text_features)[0])
            
            return {
                'incident_type': prediction,
                'confidence': confidence,
                'method': 'ml_based',
                'algorithm': model_data.get('algorithm', 'unknown')
            }
        else:
            # Fallback to simple bag of words approach
            return simple_bow_classification(combined_text)
            
    except Exception as e:
        demisto.error(f"ML classification failed: {str(e)}")
        return {'incident_type': 'general', 'confidence': 0.0, 'method': 'ml_failed'}

def simple_bow_classification(text: str) -> Dict:
    """
    Simple bag of words classification
    """
    # Define keyword patterns for each incident type
    patterns = {
        'phishing': ['phishing', 'verify account', 'click here', 'suspend', 'urgent'],
        'malware': ['malware', 'virus', 'infected', 'trojan', 'suspicious file'],
        'business_email_compromise': ['wire transfer', 'invoice', 'payment', 'ceo', 'urgent request'],
        'data_breach': ['data breach', 'leak', 'unauthorized access', 'compromised'],
        'spam': ['spam', 'promotion', 'offer', 'deal', 'free']
    }
    
    text_lower = text.lower()
    scores = {}
    
    for incident_type, keywords in patterns.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[incident_type] = score
    
    if max(scores.values()) > 0:
        predicted_type = max(scores, key=scores.get)
        confidence = min(scores[predicted_type] / 5.0, 1.0)
    else:
        predicted_type = 'general'
        confidence = 0.0
    
    return {
        'incident_type': predicted_type,
        'confidence': confidence,
        'method': 'simple_bow',
        'scores': scores
    }

def genai_classification(email_data: Dict) -> Dict:
    """
    GenAI-based classification using external AI service
    """
    try:
        # Prepare the email content
        subject = email_data.get('subject', '')
        body = email_data.get('body', '')
        sender = email_data.get('sender', '')
        
        # Create prompt for AI classification
        prompt = f"""
        Analyze the following email and classify it into one of these incident types:
        - phishing
        - malware
        - business_email_compromise
        - data_breach
        - spam
        - suspicious_activity
        - general
        
        Email Details:
        From: {sender}
        Subject: {subject}
        Body: {body[:1000]}...
        
        Provide your response in JSON format with:
        - incident_type: the classification
        - confidence: score from 0.0 to 1.0
        - reasoning: brief explanation
        """
        
        # Call external AI service (Claude, GPT, etc.)
        ai_response = call_external_ai_service(prompt)
        
        if ai_response:
            return {
                'incident_type': ai_response.get('incident_type', 'general'),
                'confidence': ai_response.get('confidence', 0.0),
                'method': 'genai',
                'reasoning': ai_response.get('reasoning', '')
            }
        else:
            return {'incident_type': 'general', 'confidence': 0.0, 'method': 'genai_failed'}
            
    except Exception as e:
        demisto.error(f"GenAI classification failed: {str(e)}")
        return {'incident_type': 'general', 'confidence': 0.0, 'method': 'genai_failed'}

def call_external_ai_service(prompt: str) -> Dict:
    """
    Call external AI service (implement based on your chosen service)
    """
    # This would integrate with your Anthropic Claude service or other AI
    # Example integration with HTTP request
    
    try:
        # Get integration parameters from XSOAR
        ai_endpoint = demisto.params().get('ai_endpoint')
        api_key = demisto.params().get('ai_api_key')
        
        if not ai_endpoint or not api_key:
            return None
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'prompt': prompt,
            'max_tokens': 500,
            'temperature': 0.1
        }
        
        response = requests.post(ai_endpoint, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            # Parse the AI response and extract classification
            return parse_ai_response(result.get('response', ''))
        else:
            demisto.error(f"AI service returned status code: {response.status_code}")
            return None
            
    except Exception as e:
        demisto.error(f"Error calling AI service: {str(e)}")
        return None

def parse_ai_response(ai_text: str) -> Dict:
    """
    Parse AI response to extract classification data
    """
    try:
        # Try to parse as JSON first
        if '{' in ai_text and '}' in ai_text:
            json_start = ai_text.find('{')
            json_end = ai_text.rfind('}') + 1
            json_str = ai_text[json_start:json_end]
            return json.loads(json_str)
        else:
            # Fallback parsing
            return {'incident_type': 'general', 'confidence': 0.0}
    except:
        return {'incident_type': 'general', 'confidence': 0.0}

def combine_classification_results(rule_result: Dict, ml_result: Dict, genai_result: Dict) -> Dict:
    """
    Combine multiple classification results with weighted scoring
    """
    # Define weights for each method
    weights = {
        'rule_based': 0.3,
        'ml_based': 0.4,
        'genai': 0.3
    }
    
    # Collect all predictions
    predictions = [rule_result, ml_result, genai_result]
    valid_predictions = [p for p in predictions if p.get('confidence', 0) > 0]
    
    if not valid_predictions:
        return {
            'incident_type': 'general',
            'confidence': 0.0,
            'method': 'combined',
            'details': predictions
        }
    
    # Calculate weighted scores for each incident type
    incident_scores = {}
    
    for prediction in valid_predictions:
        incident_type = prediction.get('incident_type', 'general')
        confidence = prediction.get('confidence', 0.0)
        method = prediction.get('method', '')
        weight = weights.get(method, 0.1)
        
        if incident_type not in incident_scores:
            incident_scores[incident_type] = 0
        
        incident_scores[incident_type] += confidence * weight
    
    # Select the highest scoring incident type
    if incident_scores:
        final_incident_type = max(incident_scores, key=incident_scores.get)
        final_confidence = min(incident_scores[final_incident_type], 1.0)
    else:
        final_incident_type = 'general'
        final_confidence = 0.0
    
    return {
        'incident_type': final_incident_type,
        'confidence': final_confidence,
        'method': 'combined',
        'individual_results': predictions,
        'scores': incident_scores
    }

def load_trained_model():
    """
    Load pre-trained ML model from XSOAR storage or external source
    """
    try:
        # Try to load from XSOAR list or integration storage
        model_data = demisto.getList('EmailClassificationModel')
        if model_data:
            return json.loads(model_data)
        else:
            return None
    except:
        return None

def main():
    """
    Main execution function for XSOAR automation
    """
    try:
        # Get email data from XSOAR context
        email_data = {
            'subject': demisto.args().get('subject', ''),
            'body': demisto.args().get('body', ''),
            'sender': demisto.args().get('sender', ''),
            'attachments': demisto.args().get('attachments', [])
        }
        
        # Perform classification
        classification_result = classify_email_content(email_data)
        
        # Set XSOAR context
        demisto.setContext('EmailClassification', classification_result)
        
        # Create incident with classified type
        incident_type = classification_result.get('incident_type', 'general')
        confidence = classification_result.get('confidence', 0.0)
        
        # Only auto-classify if confidence is above threshold
        confidence_threshold = float(demisto.params().get('confidence_threshold', 0.7))
        
        if confidence >= confidence_threshold:
            # Update incident type
            demisto.executeCommand('setIncident', {
                'type': incident_type,
                'severity': calculate_severity(incident_type, confidence)
            })
            
            demisto.results({
                'Type': entryTypes['note'],
                'Contents': classification_result,
                'ContentsFormat': formats['json'],
                'HumanReadable': f"Email classified as: {incident_type} (confidence: {confidence:.2f})",
                'EntryContext': {
                    'EmailClassification': classification_result
                }
            })
        else:
            demisto.results({
                'Type': entryTypes['note'],
                'Contents': classification_result,
                'ContentsFormat': formats['json'],
                'HumanReadable': f"Low confidence classification: {incident_type} (confidence: {confidence:.2f}). Manual review recommended.",
                'EntryContext': {
                    'EmailClassification': classification_result
                }
            })
            
    except Exception as e:
        demisto.error(f"Email classification failed: {str(e)}")
        return_error(f"Email classification failed: {str(e)}")

def calculate_severity(incident_type: str, confidence: float) -> int:
    """
    Calculate incident severity based on type and confidence
    """
    severity_mapping = {
        'phishing': 3,
        'malware': 4,
        'business_email_compromise': 4,
        'data_breach': 4,
        'suspicious_activity': 2,
        'spam': 1,
        'general': 1
    }
    
    base_severity = severity_mapping.get(incident_type, 1)
    
    # Adjust based on confidence
    if confidence < 0.5:
        return max(base_severity - 1, 1)
    elif confidence > 0.8:
        return min(base_severity + 1, 4)
    else:
        return base_severity

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()