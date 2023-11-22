# Semantic SQL
SQL queries that support semantic predicates as well

## Setup
- Download the data [Google Drive Link](https://drive.google.com/file/d/1Z14mnJI4ANrylNDpp65N8RbGgZ-eA7IY/view?usp=sharing)
- Unzip the data and keep it in the project directory
- Install the requirements
```python
pip install -r requirements.txt
```
- Run the command to start
```python
streamlit run main.py
```
This command starts the semantic-sql at the following address http://localhost:8501/

- Click **Setup DB** button to create and populate the database table and build the vector index. Wait for sometime, this may take upto ~30 seconds. This step is only required for the first time. You don't need to run this again ever in the future unless you click **Reset DB**
- Every time, you want to run a query, click **New Query** button.
- Type in the __sql__ query and click **Execute Query**
### Example SQL Queries
```sql
SELECT id, COUNT(*) as c
FROM objects
WHERE class_name='person'
GROUP BY id
HAVING c = 2
SEMANTIC 'married couple'
```