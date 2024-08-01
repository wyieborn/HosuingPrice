from flask import Flask, request
import pandas as pd
import pickle
# import start

app = Flask(__name__)






def load_model():
    
    file_name = "xgb_model.pkl"

    # load
    model = pickle.load(open(file_name, "rb"))
    
    return model

    
# Function to remove outliers based on IQR
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]


    
def preprocessing(data):

    # load the dataset
    file_path = 'melb_data.csv'
    df = pd.read_csv(file_path)
    # Remove outliers for specific columns
    columns_to_clean = ['Bathroom', 'Landsize', 'Propertycount', 'Distance']
    for col in columns_to_clean:
        df = remove_outliers(df, col)
    
    data = pd.concat([data, df])
    
    categorical_columns = ['Method', 'Type', 'Regionname', 'CouncilArea']
    # Perform one-hot encoding on categorical columns
    data_encoded = pd.get_dummies(data, columns=categorical_columns)

    # Handling missing values
    data.update(data['Car'].fillna(data['Car'].median()))
    data.update(data['BuildingArea'].fillna(data['BuildingArea'].median()))
    data.update(data['YearBuilt'].fillna(data['YearBuilt'].median()))
    data.update(data['CouncilArea'].fillna(data['CouncilArea'].mode()[0]))


    return data_encoded

def feature_engineering(data):
    print('from feature eng')
    print(data)
    # Feature engineering
    data['Age'] = 2024 - data['YearBuilt']
    data['AreaPerRoom'] = data['BuildingArea'] / data['Rooms']
    data['LandAreaPerRoom'] = data['Landsize'] / data['Rooms']
    data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')

    data['Month'] = data['Date'].dt.month
    data['Year'] = data['Date'].dt.year
    
    return data

def prepare_features(data):
    import xgboost as xgb
    from sklearn.preprocessing import MinMaxScaler

    dct = {k:[v] for k,v in data.items()} # mapping keys
    data = pd.DataFrame(dct) 
    
    data = feature_engineering(data)
    data_encoded = preprocessing(data) 

    drop_list = ['Date', 'YearBuilt']

    drop_list = ['Price','Suburb', 'SellerG','Address', 'Date', 'YearBuilt']
     # Display the encoded DataFrame
    data_encoded = data_encoded.drop(drop_list, axis=1)
    print(data_encoded.head())
    print(data_encoded.columns)
    # Cast every column to float
    data_encoded = data_encoded.astype(float)

    print(data_encoded.columns)
    scaler = MinMaxScaler()

    # fit and transfrom
    data_scaled = scaler.fit_transform(data_encoded)
    data_scaled = xgb.DMatrix(data_scaled)
    print(data_scaled)

    return data_scaled

@app.route('/')
def test_api():
    return 'Welcome to Housing Price Prediction Api V1.0.0'

# Flask route for making predictions
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    data = prepare_features(data)
    model = load_model()
    prediction = model.predict(data)
    return str(prediction[0])
    
if __name__ == '__main__':
    app.run(debug=True)
