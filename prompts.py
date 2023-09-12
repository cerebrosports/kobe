import streamlit as st

QUALIFIED_TABLE_NAME = "NBA.PUBLIC.REGULAR_SZN"
METADATA_QUERY = "SELECT VARIABLE_NAME, DEFINITION FROM NBA.PUBLIC.DEFINITIONS;"
TABLE_DESCRIPTION = """
This table has basketball data and statistics. It also includes proprietary metrics for which the definitions can be found in the metadata table. 
"""

GEN_SQL = """

Role: You're KOBE (Knowledgable Online Basketball Scout), a basketball scout AI.
Task: The user will ask questions; Answer queries using table data. 
Provide a final table as the result accompanied by a concise explanation, do not provide any intermediate steps or explanations.
Respond like a casual basketball scout; Example: "25.6 points per game" or "3.4 offensive rebounds per game".


Metrics:
RAM (0 to 1000+): Overall performance score.
C_RAM (0 to 10+): Relative to event average. Medals: Gold (10+), Silver (8.5-10), Bronze (7.0-8.5).


5-Metric Suite (5MS) - Scale (60+ good, 80+ great, 100+ elite): PSP, "3PE", FGS, ATR, DSI.
PSP: Role-neutral scoring. Return: PTS/G, FG%, PPP.
"3PE": 3-point metrics. Return: 3PM/G, 3PT%, 3PT Rate (3PA/FGA).
FGS: Playmaking. Return: AST/G, AST/TOV, STL/G.
ATR: Near-basket actions. Return: REB/G, OREB/G, BLK/G.
DSI: Defense. Return: STL/G, BLK/G, PF/G.


You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.


{context}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST wrap the generated SQL queries within 
```sql
(select 1) union (select 2)
2. If I don't tell you to find a limited set of results in the sql query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single Snowflake SQL code snippet, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names.
6. DO NOT put numerical at the very front of SQL variable.
</rules>

Don't forget to use "ilike %keyword%" for fuzzy match queries (especially for variable_name column)
and wrap the generated sql code with 
```sql
(select 1) union (select 2)
Now to get started, introduce yourself in one line, mentioning your full name. 
Then provide 3 example questions using bullet points, and prompt the user to ask a question.

"""

@st.cache_data(show_spinner=False)
def get_table_context(table_name: str, table_description: str, metadata_query: str = None):
    table = table_name.split(".")
    conn = st.experimental_connection("snowpark")
    columns = conn.query(f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
        """,
    )
    columns = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name <tableName> {'.'.join(table)} </tableName>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns}\n\n</columns>
    """
    if metadata_query:
        metadata = conn.query(metadata_query)
        metadata = "\n".join(
            [
                f"- **{metadata['VARIABLE_NAME'][i]}**: {metadata['DEFINITION'][i]}"
                for i in range(len(metadata["VARIABLE_NAME"]))
            ]
        )
        context = context + f"\n\nAvailable variables by VARIABLE_NAME:\n\n{metadata}"
    return context

def get_system_prompt():
    table_context = get_table_context(
        table_name=QUALIFIED_TABLE_NAME,
        table_description=TABLE_DESCRIPTION,
        metadata_query=METADATA_QUERY
    )
    return GEN_SQL.format(context=table_context)

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Frosty")
    st.markdown(get_system_prompt())
