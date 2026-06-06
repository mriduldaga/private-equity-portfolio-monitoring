# Contributing

Contributions that improve the monitoring logic, reporting workflows, data model, or
dashboard usability are welcome.

## Development

1. Create a virtual environment.
2. Install the project and test dependencies:

   ```bash
   pip install -r requirements.txt
   pip install pytest
   ```

3. Run the dashboard:

   ```bash
   streamlit run app.py
   ```

4. Run the validation suite before opening a pull request:

   ```bash
   python -m pytest
   python -m compileall -q app.py pages src
   ```

Keep sample data fictional and do not commit confidential portfolio company information.
