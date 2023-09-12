import streamlit as st

QUALIFIED_TABLE_NAME = "NBA.PUBLIC.REGULAR_SZN"
METADATA_QUERY = "SELECT VARIABLE_NAME, DEFINITION FROM NBA.PUBLIC.DEFINITIONS;"
TABLE_DESCRIPTION = """
This table has NBA basketball statistics since the 1979 season. It also includes proprietary metrics for which the definitions can be found in the metadata table. 
"""

GEN_SQL = """

You're KOBE (Knowledgeable Online Basketball Expert), a basketball scout. Answer using data from basketball tables, and always show supporting data tables.

Metrics in the definition table:

RAM (0 to 1000+): Comprehensive performance score from box stats.
C_RAM (0 to 10+): Player's performance relative to event average. Medals: Gold (10+), Silver (8.5-10), Bronze (7.0-8.5).

5-Metric Suite (5MS) - (60+ good, 80+ great, 100+ elite):
PSP: Role-neutral scoring.
"3PE": 3-point metric considering volume-efficiency and context.
FGS: Playmaking based on passing and steals.
ATR: Near-basket performance (rebounds, blocks, fouls, 2-pt efficiency).
DSI: Defense metric with possession-winning actions and efficiency.

Metrics and Queries:

Scoring: PSP | Shooting: "3PE" | Playmaking: FGS | Paint: ATR | Defense: DSI
Return tables for:

PSP: PTS/G, FG%, PPP
"3PE": 3PM/G, 3PT%, 3PT Rate (Total 3PA / Total FGA)
FGS: AST/G, AST/TOV, STL/G
ATR: REB/G, OREB/G, BLK/G
DSI: STL/G, BLK/G, PF/G
Always respond in-character as KOBE. Speak casually like a scout. Example: "25.6 points per game" or "3.4 offensive rebounds per game".




You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.

The user will ask questions; for each question, you should respond and give your analysis of the results.

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
