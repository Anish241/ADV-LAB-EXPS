import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np
from sklearn.preprocessing import LabelEncoder
import spacy
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO

class DataVizSystem:
    def __init__(self):
        self.data = None
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            st.error("Please install spacy language model using: python -m spacy download en_core_web_sm")
    
    def load_data(self, file):
        try:
            self.data = pd.read_csv(file)
            # Store column names in lowercase for easier matching
            self.columns_lower = {col.lower(): col for col in self.data.columns}
            self._analyze_columns()
            return True
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return False
    
    def _analyze_columns(self):
        """Analyze and categorize columns"""
        self.column_types = {}
        for column in self.data.columns:
            if self.data[column].dtype in ['int64', 'float64']:
                if len(self.data[column].unique()) <= 10:
                    self.column_types[column] = 'ordinal'
                else:
                    self.column_types[column] = 'scale'
            elif len(self.data[column].unique()) <= 2:
                self.column_types[column] = 'binary'
            else:
                self.column_types[column] = 'nominal'
    
    def _preprocess_query(self, query):
        """Preprocess the query to identify column names"""
        query = query.lower()
        columns_mentioned = []
        
        # Check for exact matches first
        for col_lower, col_original in self.columns_lower.items():
            if col_lower in query:
                columns_mentioned.append(col_original)
        
        # If no exact matches, try fuzzy matching with spacy
        if not columns_mentioned:
            doc = self.nlp(query)
            for token in doc:
                # Check if the token text is similar to any column name
                for col_lower, col_original in self.columns_lower.items():
                    if (token.text in col_lower or 
                        col_lower in token.text or 
                        token.similarity(self.nlp(col_lower)) > 0.8):
                        columns_mentioned.append(col_original)
        
        return list(set(columns_mentioned))  # Remove duplicates
    
    def process_query(self, query):
        """Process natural language query and generate appropriate visualization"""
        # Extract potential column names from query
        columns_mentioned = self._preprocess_query(query)
        
        if not columns_mentioned:
            return None, "No relevant columns found in query. Available columns: " + ", ".join(self.data.columns)
        
        # Detect query type and create visualization
        if any(word in query.lower() for word in ['relationship', 'affecting', 'affect', 'effect', 'correlation', 'impact']):
            if len(columns_mentioned) >= 2:
                return self._create_relationship_plot(columns_mentioned[0], columns_mentioned[1])
            elif len(columns_mentioned) == 1:
                # Try to find a relevant second column
                if 'outcome' in query.lower() or 'result' in query.lower():
                    potential_outcome_columns = [col for col in self.data.columns 
                                              if any(term in col.lower() 
                                                    for term in ['outcome', 'result', 'status', 'condition'])]
                    if potential_outcome_columns:
                        return self._create_relationship_plot(columns_mentioned[0], potential_outcome_columns[0])
            
            return None, "Need two columns for relationship analysis. Please specify both columns."
        else:
            return self._create_single_variable_plot(columns_mentioned[0])

    # [Previous methods remain the same: generate_key_visualizations, _create_relationship_plot, _create_single_variable_plot]
    def generate_key_visualizations(self):
        """Generate the most important visualizations based on data types"""
        visualizations = []
        
        # 1. Distribution of numerical variables
        numerical_cols = [col for col, type_ in self.column_types.items() 
                         if type_ == 'scale']
        if numerical_cols:
            for col in numerical_cols[:3]:
                fig = px.histogram(self.data, x=col, title=f'Distribution of {col}')
                visualizations.append(("Numerical Distribution", fig))
                
                # Add box plot for the same variable
                fig = px.box(self.data, y=col, title=f'Box Plot of {col}')
                visualizations.append(("Box Plot", fig))
        
        # 2. Categorical variable distributions
        categorical_cols = [col for col, type_ in self.column_types.items() 
                          if type_ in ['binary', 'nominal', 'ordinal']]
        if categorical_cols:
            for col in categorical_cols[:3]:
                value_counts = self.data[col].value_counts()
                df_plot = pd.DataFrame({
                    'Category': value_counts.index,
                    'Count': value_counts.values
                })
                fig = px.bar(df_plot, 
                           x='Category', 
                           y='Count',
                           title=f'Distribution of {col}')
                visualizations.append(("Categorical Distribution", fig))
        
        # 3. Correlation matrix for numerical variables
        if len(numerical_cols) > 1:
            fig = px.imshow(self.data[numerical_cols].corr(),
                          title='Correlation Matrix',
                          labels=dict(color="Correlation"))
            visualizations.append(("Correlation Matrix", fig))
        
        return visualizations
    
    def _create_relationship_plot(self, col1, col2):
        """Create visualization for relationship between two variables"""
        if self.column_types[col1] == 'scale' and self.column_types[col2] == 'scale':
            fig = px.scatter(self.data, x=col1, y=col2, 
                           title=f'Relationship between {col1} and {col2}')
        elif (self.column_types[col1] in ['binary', 'nominal', 'ordinal'] and 
              self.column_types[col2] == 'scale'):
            fig = px.box(self.data, x=col1, y=col2,
                        title=f'{col2} by {col1}')
        elif (self.column_types[col2] in ['binary', 'nominal', 'ordinal'] and 
              self.column_types[col1] == 'scale'):
            fig = px.box(self.data, x=col2, y=col1,
                        title=f'{col1} by {col2}')
        else:
            crosstab = pd.crosstab(self.data[col1], self.data[col2])
            fig = px.imshow(crosstab, title=f'Relationship between {col1} and {col2}')
        
        return fig, None

    def _create_single_variable_plot(self, column):
        """Create visualization for a single variable"""
        if self.column_types[column] == 'scale':
            fig = px.histogram(self.data, x=column,
                             title=f'Distribution of {column}')
        else:
            value_counts = self.data[column].value_counts()
            df_plot = pd.DataFrame({
                'Category': value_counts.index,
                'Count': value_counts.values
            })
            fig = px.bar(df_plot,
                        x='Category',
                        y='Count',
                        title=f'Distribution of {column}')
        
        return fig, None

