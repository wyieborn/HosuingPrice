import streamlit as st
import requests
from datetime import date

st.title('Hello, *World!* :sunglasses:')

fields = {
    "Suburb": {"type": "text", "required": True},
    "Address": {"type": "text", "required": True},
    "Rooms": {"type": "number", "required": True},
    "Type": {"type": "text", "required": True},
    "Price": {"type": "number", "required": True},
    "Method": {"type": "text", "required": True},
    "SellerG": {"type": "text", "required": True},
    "Date": {"type": "date", "required": True},
    "Distance": {"type": "number", "required": True},
    "Postcode": {"type": "number", "required": True},
    "Bedroom2": {"type": "number", "required": True},
    "Bathroom": {"type": "number", "required": True},
    "Car": {"type": "number", "required": False},
    "Landsize": {"type": "number", "required": True},
    "BuildingArea": {"type": "number", "required": True},
    "YearBuilt": {"type": "number", "required": False},
    "CouncilArea": {"type": "text", "required": False},
    "Lattitude": {"type": "number", "required": True},
    "Longtitude": {"type": "number", "required": True},
    "Regionname": {"type": "text", "required": True},
    "Propertycount": {"type": "number", "required": True},
}

def check_required_fields(user_data, fields):
    missing_fields = []
    for field, properties in fields.items():
        if properties["required"] and (field not in user_data or user_data[field] is None or user_data[field] == ""):
            missing_fields.append(field)
    return missing_fields

def display_required_fields_warnings(required_fields):
    if required_fields:
        st.warning("Please fill in all mandatory fields.")
        for field in required_fields:
            st.markdown(
                f"<span style='color:red'>Required field: {field}</span>",
                unsafe_allow_html=True,
            )

def display_additional_info(response):
    additional_info = f"Response {response}"
    st.write(additional_info)

def get_user_input(fields):
    user_data = {}
    num_columns = 2
    columns = st.columns(num_columns)

    for idx, (field, options) in enumerate(fields.items()):
        field_type = options["type"]
        required = options["required"]
        if field_type in ["text", "number"]:
            user_data[field] = (
                columns[idx % num_columns].text_input(
                    f"Enter {field}{'*' if required else ''}", ""
                )
                if field_type == "text"
                else columns[idx % num_columns].number_input(
                    f"Enter {field}{'*' if required else ''}"
                )
            )
        elif field_type == "date":
            user_data[field] = columns[idx % num_columns].date_input(
                f"Enter {field}{'*' if required else ''}", value=date.today()
            )
        
    return user_data

def serialize_dates(data):
    from datetime import datetime, date
    if isinstance(data, dict):
        return {k: serialize_dates(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_dates(i) for i in data]
    elif isinstance(data, datetime):
        return data.isoformat()  # Convert datetime to ISO format string
    elif isinstance(data, date):
        return data.isoformat()  # Convert date to ISO format string
    return data

user_data = get_user_input(fields)
user_data = serialize_dates(user_data)
if st.button("Predict"):
    import json, pandas as pd
    # # Convert JSON string to Python list
    # data = json.loads(user_data)

    # Convert Python list to DataFrame
    # df = pd.DataFrame.from_dict(user_data, orient='index')

    # print(df)
    print(user_data)
    json_data = json.dumps(user_data)
    print(json_data)
    missing_fields = check_required_fields(user_data, fields)
    if missing_fields:
        st.error(f"The following fields are required: {', '.join(missing_fields)}")
    else:
        with st.spinner("Processing data..."):

            response = requests.post(
                "http://localhost:5000/predict", data=json_data, headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                st.title("Predicted price for the house is: " + str(response.text))
            else:
                st.error("Failed to process data. Please try again.")
                st.text(f"Response from server: {response.text}")