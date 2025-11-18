import pyodbc

server = 'matarsqldbserver.database.windows.net'
database = 'MyDataBase'
username = 'dawa3isqi'
password = 'Ma*5929525'
driver= '{ODBC Driver 18 for SQL Server}'

connection = pyodbc.connect(
    'DRIVER=' + driver + 
    ';SERVER=' + server + 
    ';PORT=1433;DATABASE=' + database + 
    ';UID=' + username + ';PWD=' + password +
    ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
)
cursor = connection.cursor()

# Create the table
cursor.execute("""
CREATE TABLE Task3Stats (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    SensorID INT,
    TemperatureMin FLOAT,
    TemperatureMax FLOAT,
    TemperatureAvg FLOAT,
    WindMin FLOAT,
    WindMax FLOAT,
    WindAvg FLOAT,
    HumidityMin FLOAT,
    HumidityMax FLOAT,
    HumidityAvg FLOAT,
    CO2Min FLOAT,
    CO2Max FLOAT,
    CO2Avg FLOAT,
    Timestamp DATETIME DEFAULT GETUTCDATE()
)
""")
connection.commit()
print("Table created successfully.")