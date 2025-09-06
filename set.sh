#!/bin/bash

# Define directories and files
dirs=(
  "data_engine"
  "filtration_engine"
  "matching_engine"
  "resume_engine"
  "referral_engine"
  "auto_apply_engine"
  "schemas"
)

files=(
  "__init__.py"
  "interfaces.py"
)

# Create directories and add common files
for dir in "${dirs[@]}"; do
  mkdir -p "$dir"
  for file in "${files[@]}"; do
    touch "$dir/$file"
  done
done

# Special single files in each engine
touch data_engine/linkedin_scraper.py
touch filtration_engine/generic_filter.py
touch matching_engine/llm_matcher.py
touch resume_engine/pdf_resume_generator.py
touch referral_engine/linkedin_connector.py
touch auto_apply_engine/autofill_form.py

# Schemas
touch schemas/job.py
touch schemas/user.py
touch schemas/application.py

# Root file
touch main.py

echo "✅ Project structure created successfully!"
