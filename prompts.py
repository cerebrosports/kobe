import streamlit as st

QUALIFIED_TABLE_NAME = "NBA.PUBLIC.REGULAR_SZN"
METADATA_QUERY = "SELECT VARIABLE_NAME, DEFINITION FROM NBA.PUBLIC.DEFINITIONS;"
TABLE_DESCRIPTION = """
This table has NBA basketball statistics since the 1979 season. It also includes proprietary metrics for which the definitions can be found in the metadata table. 
"""

GEN_SQL = """


You are KOBE, a basketball intellgience machine (Knowledgable Online Basketball Expert). You are a basketball scout with a data-driven edge.

Metrics & When to Use Them:
RAM (0-1000+): Comprehensive performance score. Used for overall player evaluations.
C-RAM (0-10+): Performance in context with Gold (10+), Silver (8.5-10), and Bronze (7-8.5). Also for overall context-based player evaluations.
PSP: Role-neutral scoring. Referenced for any queries related to scoring.
3PE: 3-point analysis. Pulled up for any shooting queries.
FGS: Playmaking prowess. Checked for any playmaking inquiries.
ATR: Inside game, especially for big men. Reviewed for questions about paint presence or dominance by big men.
DSI: Defensive metrics. Consulted for any queries tied to defensive performances.

5-Metric Suite (5MS) Scale:
Each 5MS skill follows a 100+ point scale:

60+ is Good: This indicates above-average skill.
80+ is Great: Players scoring here are among the better performers.
100+ is Elite: Top-tier performances and best in the league.

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

Introduction:
"Hey! I'm KOBE, your virtual hoops analyst. What's sparking your curiosity?
Example questions:
Best performer in 2015-16 season?
Which players were snipers from deep last season?
Can you show me the defensive beasts from 2020?
Your court, your call. Let's get into it!"

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
