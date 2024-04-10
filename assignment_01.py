import pandas as pd



def set_intersection(column_data_1, column_data_2):
    # 將colunm轉為list
    list1 = column_data_1.tolist()
    list2 = column_data_2.tolist()

    # 利用&找出交集
    intersection_result = list(set(list1) & set(list2))

    # return 結果
    return intersection_result


def cartesian_product(df1, df2):
    # 將dataframe 轉為字典
    if not isinstance(df1, list):
        df1 = df1.to_dict('records')
    if not isinstance(df2, list):
        df2 = df2.to_dict('records')

    result = []
    # 走過第一個字典集中的每一行
    for dict1 in df1:
        # 走過第二個字典集中的每一行
        for dict2 in df2:
            # 合併加回列表
            merged_dict = {**dict1, **dict2}
            result.append(merged_dict)

    # 轉回DataFrame
    return pd.DataFrame(result)


def set_union(column_data_1, column_data_2):
    # 將column 轉為list
    list1 = column_data_1.tolist()
    list2 = column_data_2.tolist()

    # 將兩list合併，使用集合消除重複，轉回list
    union_result = list(set(list1 + list2))

    return union_result


def set_difference(column_data_1, column_data_2):
    # 將column 轉為list
    list1 = column_data_1.tolist()
    list2 = column_data_2.tolist()

    # 將兩list合併，使用集合找到defference，轉回list
    difference_result = list(set(list1) - set(list2))

    return difference_result


def simpleSelect(df, query_string):
    # 分解字串
    parts = query_string.split()
    if len(parts) != 3:
        raise ValueError(
            "Query string format should be 'column_name operator value' or 'column_name1 operator column_name2'.")

    column_name, operator, value_or_column = parts

    # 確定比較對象是常數還是其他列
    if value_or_column in df.columns:
        # 找到此列
        value_column = df[value_or_column]
    else:
        try:
            # 處理成福點數
            value_column = float(value_or_column)
        except ValueError:
            # 如果不是數字則當成字串
            value_column = value_or_column

    # 判斷operator
    if operator == '>':
        result = df[column_name] > value_column
    elif operator == '<':
        result = df[column_name] < value_column
    elif operator == '>=':
        result = df[column_name] >= value_column
    elif operator == '<=':
        result = df[column_name] <= value_column
    elif operator == '==':
        result = df[column_name] == value_column
    else:
        raise ValueError(f"Unsupported operator: {operator}")

    # return
    return df[result]


def project(df, columns):
    return df[columns]


def rename(df, rename_dict):
    # 取得所有列的名字
    new_columns = df.columns.tolist()

    # 看過整個字典找到目標
    for original_name, new_name in rename_dict.items():
        # 確保原始列名存在於DataFrame中
        if original_name in new_columns:
            # 找到原始列名的索引
            index = new_columns.index(original_name)
            # 更新列名
            new_columns[index] = new_name
        else:
            print(f"Column '{original_name}' does not exist in DataFrame.")
            return df

    # 將更新后的列名列表给DataFrame.columns
    df.columns = new_columns
    return df


def load_data(file_path):
    # 讀資料
    return pd.read_csv(file_path, sep=',', index_col=0)


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def user_interface():


    results_dict = {}
    active_db = None
    isSkip = "Y"

    while True:
        # 檢查是否是第一次使用
        if isSkip == "N" :
            isSave = input("Save this result? Enter your choice (Y or N): ")
            # 確認是否留下紀錄
            if (isSave == "Y" or isSave == "y"):
                key = input("Enter a key name for this result: ")
                results_dict[key] = active_db


        if len(results_dict.keys()) != 0:
            print("\nWhich database would you like to operate on?")
            for key in results_dict.keys():
                print(f"Database: {key}")
            db_choice = input("Enter your choice: ")
            # 找到dict中對應的data
            if db_choice in results_dict:
                active_db = results_dict[db_choice]
                print(f"Database {db_choice} selected.")
                print("Database Schema:")
                print("----------------")
                for column in active_db.columns:
                    print(column)
                # 輸出schema
                print("\nTotal Columns:", len(active_db.columns))
            else:
                print("\nInvalid choice. Please enter a valid choice.")
                continue

        isSkip = "N";
        print("\nAvailable operations:")
        print("0. load a csv file")
        print("1. Select based on a condition")
        print("2. Project target columns")
        print("3. Rename column")
        print("4. Cartesian Product")
        print("5. Set Union")
        print("6. Set Difference")
        print("7. Set intersection")
        print("8. Exit")
        choice = input("Enter your choice (0-8): ")

        if choice == '0':
            isSkip = 'Y'
            str = input("input csv file: ")
            try:
                data = pd.read_csv(str, index_col=0)
                results_dict[str] = data
                active_db = data

            except:
                print("file name does no exist!")



        elif choice == '1':
            if len(results_dict.keys()) == 0:
                print("No data available!")
                isSkip = 'Y'
                continue
            # 進行select
            print("--------------------------------")
            condition = input("Enter your condition (e.g., 'HP > 50' for Pokemon or 'trainer_id > 1' for Trainers): ")
            try:
                active_db = simpleSelect(active_db, condition)
                print("\nSelected data with conditions:\n", active_db)
            except Exception as e:
                print("\nError evaluating condition:", e)

        elif choice == '2':
            if len(results_dict.keys()) == 0:
                print("No data available!")
                isSkip = 'Y'
                continue
            # 進行project
            print("--------------------------------")
            columns_input = input("Enter the columns you want to project (separated by commas, e.g., 'Name, Type 1'): ")
            columns = [col.strip() for col in columns_input.split(',')]
            try:
                active_db = project(active_db, columns)
                print("\nProjected columns:\n", active_db)
            except KeyError as e:
                print(f"\nError: One or more column names are incorrect: {e}")
            except Exception as e:
                print(f"\nAn unexpected error occurred: {e}")

        elif choice == '3':
            isSkip = 'Y'
            if len(results_dict.keys()) == 0:
                print("No data available!")
                isSkip = 'Y'
                continue
            # 進行rename
            print("--------------------------------")
            for key in results_dict.keys():
                print(f"Key: {key}")

            old_key = input("Enter the key name you want to rename: ")
            if old_key in results_dict:
                new_key = input("Enter the new key name: ")
                if new_key in results_dict:
                    print(f"\nError: The key name '{new_key}' already exists. Please use a different name.")
                else:
                    # 重新命名
                    results_dict[new_key] = results_dict.pop(old_key)
                    print(f"\nKey '{old_key}' has been renamed to '{new_key}'.")
            else:
                print(f"\nError: The key name '{old_key}' does not exist.")

            original_name = input("Enter the original column name you want to rename: ").strip()
            new_name = input("Enter the new column name: ").strip()
            rename_dict = {original_name: new_name}
            try:
                active_db = rename(active_db, rename_dict)
                print(f"\nRenamed '{original_name}' to '{new_name}':\n", active_db)
            except KeyError as e:
                print(f"\nError: The column name '{original_name}' does not exist in the DataFrame: {e}")
            except Exception as e:
                print(f"\nAn unexpected error occurred: {e}")

        elif choice == '4':
            if len(results_dict.keys()) == 0:
                print("No data available!")
                isSkip = 'Y'
                continue

            # 進行products
            print("--------------------------------")
            print("\nWhich database would you like to operate on?")
            for key in results_dict.keys():
                print(f"Database: {key}")

            db_choice = input("Enter your choice: ")
            if db_choice in results_dict:
                Cartesian_db = results_dict[db_choice]
                print(f"Database {db_choice} selected.")
            try:
                active_db = cartesian_product(active_db, Cartesian_db)
                print("\nCartesian Product result:\n", active_db)
            except Exception as e:
                print("\nError performing Cartesian Product:", e)

        elif choice == '5':
            if len(results_dict) < 2:
                print("No enough data available! At least 2 datasets are required.")
                continue

            # 顯示可用的database
            print("Available datasets:")
            for key in results_dict.keys():
                print(f"Dataset: {key}")
            # 進行Union
            print("--------------------------------")
            print("Please select the dataset for union operation:")
            db_choice1 = input("Enter your choice: ")
            if db_choice1 not in results_dict not in results_dict:
                print("Invalid dataset selection. Please make sure to select available datasets.")
                continue

            print("--------------------------------")
            print("Performing Set Union between two specified columns.")
            col1 = input(f"Enter the column name from current : ").strip()
            col2 = input(f"Enter the column name from {db_choice1}: ").strip()

            try:
                #從database 中獲得數據
                column_data_1 = active_db[col1] if col1 in active_db.columns else pd.Series([], dtype='object')
                column_data_2 = results_dict[db_choice1][col2] if col2 in results_dict[
                    db_choice1].columns else pd.Series([], dtype='object')

                # 進行union
                union_result = set_union(column_data_1, column_data_2)
                result_db = pd.DataFrame({col1: union_result})
                active_db = result_db

                print("\nSet Union result of the specified columns:\n", result_db)
            except Exception as e:
                print("\nError performing Set Union:", e)

        elif choice == '6':
            if len(results_dict) < 2:
                print("No enough data available! At least 2 datasets are required.")
                continue

            # 顯示可用的database
            print("Available datasets:")
            for key in results_dict.keys():
                print(f"Dataset: {key}")

            # 選擇進行set difference的database
            print("--------------------------------")
            print("Please select the dataset for difference operation:")
            db_choice1 = input("Enter your choice: ")
            if db_choice1 not in results_dict:
                print("Invalid dataset selection. Please make sure to select available datasets.")
                continue

            print("--------------------------------")
            print("Performing Set Difference between two specified columns.")
            col1 = input("Enter the column name from current: ").strip()
            col2 = input(f"Enter the column name from {db_choice1}: ").strip()

            try:
                # 獲得指定column
                column_data_1 = active_db[col1] if col1 in active_db.columns else pd.Series([], dtype='object')
                column_data_2 = results_dict[db_choice1][col2] if col2 in results_dict[
                    db_choice1].columns else pd.Series([], dtype='object')

                # 進行set difference
                difference_result = set_difference(column_data_1, column_data_2)
                result_db = pd.DataFrame({col1: difference_result})
                active_db = result_db

                print("\nSet Difference result of the specified columns:\n", result_db)
            except Exception as e:
                print("\nError performing Set Difference:", e)
        elif choice == '7':
            if len(results_dict) < 2:
                print("No enough data available! At least 2 datasets are required.")
                continue

            # 顯示可用的database
            print("Available datasets:")
            for key in results_dict.keys():
                print(f"Dataset: {key}")

            # 進行交集
            print("--------------------------------")
            print("Please select the dataset for intersection operation:")
            db_choice1 = input("Enter your choice: ")
            if db_choice1 not in results_dict:
                print("Invalid dataset selection. Please make sure to select available datasets.")
                continue

            print("--------------------------------")
            print("Performing Set Intersection between two specified columns.")
            col1 = input(f"Enter the column name from the current dataset: ").strip()
            col2 = input(f"Enter the column name from {db_choice1}: ").strip()

            try:
                # 獲得指定column
                column_data_1 = active_db[col1] if col1 in active_db.columns else pd.Series([], dtype='object')
                column_data_2 = results_dict[db_choice1][col2] if col2 in results_dict[
                    db_choice1].columns else pd.Series([], dtype='object')

                # 進行set intersections
                intersection_result = set_intersection(column_data_1, column_data_2)
                result_db = pd.DataFrame({col1: intersection_result})

                # 更新 active_db
                active_db = result_db

                print("\nSet Intersection result of the specified columns:\n", result_db)
            except Exception as e:
                print("\nError performing Set Intersection:", e)
        elif choice == '8':
            print("\nExiting...")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 8.")


if __name__ == "__main__":
    user_interface()