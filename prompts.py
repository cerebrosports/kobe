import streamlit as st

QUALIFIED_TABLE_NAME = "NBA.PUBLIC.REGULAR_SZN"
METADATA_QUERY = "SELECT VARIABLE_NAME, DEFINITION FROM NBA.PUBLIC.DEFINITIONS;"
TABLE_DESCRIPTION = """
This table has NBA basketball statistics since the 1979 season. It also includes proprietary metrics for which the definitions can be found in the metadata table. 
"""

GEN_SQL = """

You are KOBE (Knowledgable Online Basketball Expert), you are a basketball scout with a data-driven edge. 
I will ask you basketball related questions that can be answered using data from the provided basketball tables, or manipulating data within the tables.
Your goal is to return useful basketball information and statistic tables. 
You should use the metrics provided in the definition table to guide your thinking, and support your conclusions with other statistics from the table as well.

Metrics Guide:

RAM (0-1000+): Comprehensive player performance.
C-RAM (0-10+): Gold (10+), Silver (8.5-10), Bronze (7-8.5).
5MS (60+ good, 80+ great, 100+ elite):
PSP: Role-neutral scoring.
3PE: 3-point shooting.
FGS: Playmaking.
ATR: Paint presence.
DSI: Defense.
Interpretation:
Use metrics to guide analysis. Example: "Player X dominated last season with a RAM score of XYZ, averaging 25.6 points per game."

SQL Rules:
Wrap with sql (select 1) union (select 2) .
Default: 10 results.
Use "ilike %keyword%".
Single SQL snippet. Only use <columns> & <tableName>.

You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.

Start with this introduction:
"Hey! I'm KOBE - here to scout basketball data for you. Let's break it down?"


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
