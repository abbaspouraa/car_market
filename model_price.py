import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# Database connection details
load_dotenv('.env')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = 'CarMarket'

# Create a database connection
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}')

# Query the CarWarehouse table
query = """
SELECT
    price, (YEAR(NOW()) - year) AS age, mileage
FROM CarWarehouse
WHERE sold = 0
AND (model = 'f150' OR model = 'f-150')
AND mileage > 70000
AND price > 2000
AND year > 2006
AND price < 20000;
"""

if __name__ == "__main__":
    # Load data into a Pandas DataFrame
    data = pd.read_sql(query, engine)

    # Select relevant features
    features = ['age', 'mileage']
    target = 'price'

    # Separate the features (X) and target variable (y)
    X = data.drop(columns=[target])
    y = data[target]

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Initialize and train the LightGBM model
    lgbm_model = LGBMRegressor(random_state=42)
    lgbm_model.fit(X_train, y_train)

    # Make predictions
    y_pred_lgbm = lgbm_model.predict(X_test)

    # Evaluate the model
    mae_lgbm = mean_absolute_error(y_test, y_pred_lgbm)
    r2_lgbm = r2_score(y_test, y_pred_lgbm)

    print(f"LightGBM - Mean Absolute Error: {mae_lgbm}")
    print(f"LightGBM - R² Score: {r2_lgbm}")

    # Create a pipeline to standardize data and apply SVR
    svr_model = make_pipeline(StandardScaler(), SVR(kernel='rbf', C=100, gamma='auto'))

    # Train the model
    svr_model.fit(X_train, y_train)

    # Make predictions
    y_pred_svr = svr_model.predict(X_test)

    # Evaluate the model
    mae_svr = mean_absolute_error(y_test, y_pred_svr)
    r2_svr = r2_score(y_test, y_pred_svr)

    print(f"SVR - Mean Absolute Error: {mae_svr}")
    print(f"SVR - R² Score: {r2_svr}")