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


def train_classification_model():
    """
    Train ML model using historical XSOAR incident data
    """
    # Fetch historical incidents
    incidents = demisto.executeCommand('getIncidents', {
        'query': 'type:Email',
        'size': 1000
    })
    
    # Prepare training data
    training_data = []
    labels = []
    
    for incident in incidents:
        email_subject = incident.get('emailsubject', '')
        email_body = incident.get('emailbody', '')
        incident_type = incident.get('type', 'general')
        
        training_data.append(f"{email_subject} {email_body}")
        labels.append(incident_type)
    
    # Train model
    vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
    X = vectorizer.fit_transform(training_data)
    y = labels
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train classifier
    classifier = MultinomialNB()
    classifier.fit(X_train, y_train)
    
    # Evaluate
    accuracy = classifier.score(X_test, y_test)
    
    # Save model
    model_data = {
        'vectorizer': vectorizer,
        'classifier': classifier,
        'accuracy': accuracy,
        'algorithm': 'MultinomialNB'
    }
    
    # Store in XSOAR
    demisto.setList('EmailClassificationModel', json.dumps(model_data, default=str))
    
    return model_data