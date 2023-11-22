# semantic-sql
SQL queries that support semantic predicates as well

## Example SQL Queries
```sql
SELECT id, COUNT(*) as c
FROM objects
WHERE class_name='person'
GROUP BY id
HAVING c = 2
SEMANTIC 'married couple'
```