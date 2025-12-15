### Financial Data Pipeline

**Project Overview**

A Scalable (Extract, Transform, Load) pipeline for extracting financial data from Financial Modeling Prep API, processing it, and storing it in Google BigQuery for analytics and reporting

Objectives:
- Automate daily extraction of financial data (stock prices, company financials, market data)
- Transform and validate data for consistency
- Load data into BigQuery for analysis
- Implement caching to optimize API usage
- Schedule and monitor data pipeline workflows

**Architecture Diagram**

Extraction Layer
- Stock Prices (OED)
- API Client Layer (requests + retry logic)

Caching Layer
Redis Cache
- Reduce redundant API calls

Transformation Layer
Data Processing (Pandas/ Numpy)
- Type conversion and formating

Loading Layer
Google BigQuery
- staging tables
- production tables

Orchestration Layer
Apache Airflow
- DAG scheduling (daily, hourly)
- task dependencies
- error handlign and retries
- monitoring and alerting

**Tech Stack**
Environment
- python 3.9 & above
- pip

Data Handling & Processing
- numpy
- pandas
- python-dateutil

Google Cloud & BigQuery
- google-cloud bigquery
- google-auth
- google-api-core

Redis
- caching 

Airflow
- 

Web API Communication
- requests

Jupyter & Notebook Ecosystem
- jupyter
- jupyterlab

**System Requirement**

**Installation & Setup**
- sign up for Alpha Vantage free API key (500calls/day)
- sign up for Financial Modeling Prep 
- create a Google Cloud Platform account and enable BigQuery API with JSON key (download the JSON file as that will be your key)
- install python 3.9 or above
- install homebrew
- install Google Cloud SDK locally

**Configuration**

**Data Schema**

**Monitoring & Logging**

**Testing**

