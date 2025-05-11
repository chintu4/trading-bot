import pandas  as pd

def save_data(filename,data):
    # k=pd.DataFrame(data,index=[0])
    k=data
    # k.save_csv(filename)
    if filename[-2:]=="csv":
        k.to_csv(f"./data/{filename}")
    elif filename[-4:]=="xlsx":
        k.to_excel(f"./data/{filename}")
    else:
        k.to_excel(f"./data/{filename}.xlsx")