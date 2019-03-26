import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from sklearn.decomposition import PCA

def main():
    print("Program: PCA")
    print("Release: 0.1.1")
    print("Date: 2019-02-11")
    print("Author: Brian Neely")
    print()
    print()
    print("This program reads a csv file and performs dimensionality reduction using PCA.")
    print()
    print()

    # Hide Tkinter GUI
    Tk().withdraw()

    # Find input file
    file_in = select_file_in()

    # Set output file
    file_out = select_file_out(file_in)

    # Ask for delimination
    delimination = input("Enter Deliminator: ")

    # Open input csv using the unknown encoder function
    data = open_unknown_csv(file_in, delimination)

    # Ask whether to use all columns, exclude certain columns, or select certain columns
    column_selection_type_input = column_selection_type(0)

    # Get list of columns from PCA
    columns = column_list(data, column_selection_type_input)

    # Set PCA factors
    pca = PCA()

    # Set input data
    x = data[columns]

    # Run PCA
    pca_results = pca.fit_transform(x)

    # Report Explained Variance Ratio
    explained_variance = pca.explained_variance_ratio_
    print("PCA explanation by factor")
    total_explained = 0
    for index, i in enumerate(explained_variance):
        total_explained = total_explained + i
        print("Factor " + str(index + 1) + ": " + str(round(i * 100, 1)) + "% - Cumulative: " + str(round(total_explained * 100, 1)) + "%")
    print()

    # Ask for number of factors to retain
    number_of_factors = int(input("How many factors to retain: "))

    # Create header list for the pca factors
    pca_column_header = list()
    for index, i in enumerate(pca.components_):
        pca_column_header.append("PCA_Factor_" + str(index))

    # Transform numpy array to data frame
    pca_factors = pd.DataFrame(data = pca_results, columns=pca_column_header)

    # Find unused columns in original dataset
    unused_columns = list()
    for i in list(data.columns.values):
        if i not in columns:
            unused_columns.append(i)

    # If number of factors is greater than number of actual factors, lower
    if number_of_factors >= len(pca_column_header):
        number_of_factors = int(len(pca_column_header))

    # Concatenate unused columns to PCA results
    data_out = data[unused_columns]
    for i in range(0, number_of_factors):
        if i <= number_of_factors:
            data_out = pd.concat([data_out, pca_factors["PCA_Factor_" + str(i)]], axis=1)

    # Ask if the previous factors should be retained
    retain_pca_input = y_n_question("Retain columns used for PCA creation?: ")

    # If desired, concatenate pca data onto output file
    if retain_pca_input == 'y':
        data_out = pd.concat([data_out, data[columns]], axis=1)

    # Write output file
    print("Writing output file...")
    data_out.to_csv(file_out, index=False)
    print("Output file wrote!")

    # Ask to export components
    write_components = y_n_question("Write PCA Component Loadings: ")

    if write_components == 'y':
        components_file_out = select_file_out(file_in)
        components_df = pd.DataFrame(data=pca.components_, columns=columns, index=pca_column_header)[:number_of_factors]
        components_df.to_csv(components_file_out)


def select_file_in():
    file_in = askopenfilename(initialdir="../", title="Select file",
                              filetypes=(("Comma Separated Values", "*.csv"), ("all files", "*.*")))
    if not file_in:
        input("Program Terminated. Press Enter to continue...")
        exit()

    return file_in


def select_file_out(file_in):
    file_out = asksaveasfilename(initialdir=file_in, title="Select file",
                                 filetypes=(("Comma Separated Values", "*.csv"), ("all files", "*.*")))
    if not file_out:
        input("Program Terminated. Press Enter to continue...")
        exit()

    # Create an empty output file
    open(file_out, 'a').close()

    return file_out


def y_n_question(question):
    while True:
        # Ask question
        answer = input(question)
        answer_cleaned = answer[0].lower()
        if answer_cleaned == 'y' or answer_cleaned == 'n':
            return answer_cleaned
        else:
            print("Invalid input, please try again.")


def column_list(data, column_selection_type_in):
    headers = list(data.columns.values)
    if column_selection_type_in == 1:
        while True:
            try:
                print("Select columns to exclude from PCA...")
                for j, i in enumerate(headers):
                    print(str(j) + ": to exclude column [" + str(i) + "]")

                # Ask for index list
                column_index_list_string = input("Enter selections separated by spaces: ")

                # Check if input was empty
                if not column_index_list_string:
                    print("No selection was used, all columns will be used.")

                # Split string based on spaces
                column_index_list = column_index_list_string.split()

                # Get column names list
                column_name_list_excld = list()
                for i in column_index_list:
                    column_name_list_excld.append(headers[int(i)])

                column_name_list = list()
                for i in headers:
                    if i not in column_name_list_excld:
                        column_name_list.append(i)

                # Check if columns are valid for PCA
                try:
                    invalid_selection = 0
                    # Test open every column and convert to number
                    for i in column_name_list:
                        test_column = i
                        for j in data[i]:
                            float(j)
                except:
                    print(test_column + ' is invalid for PCA, please select a new column list.')
                    invalid_selection = 1
                    continue

                if invalid_selection == 1:
                    break

            except ValueError:
                print("An invalid column input was detected, please try again.")
                continue

            else:
                break
    elif column_selection_type_in == 2:
        while True:
            try:
                print("Select columns to include into the PCA...")
                for j, i in enumerate(headers):
                    print(str(j) + ": to include column [" + str(i) + "]")

                # Ask for index list
                column_index_list_string = input("Enter selections separated by spaces: ")

                # Check if input was empty
                while not column_index_list_string:
                    column_index_list_string = input("Input was blank, please select columns to include.")

                # Split string based on spaces
                column_index_list = column_index_list_string.split()

                # Check to make sure at least to columns were selected
                while len(column_index_list) < 2:
                    column_index_list_string = input("Only 1 column was selected for PCA, a minimum of 2 is required.")
                    column_index_list = column_index_list_string.split()

                # Get column names list
                column_name_list = list()
                for i in column_index_list:
                    column_name_list.append(headers[int(i)])

                # Check if columns are valid for PCA
                try:
                    invalid_selection = 0
                    # Test open every column and convert to number
                    for i in column_name_list:
                        test_column = i
                        for j in data[i]:
                            float(j)
                except:
                    print(test_column + ' is invalid for PCA, please select a new column list.')
                    invalid_selection = 1
                    continue

                if invalid_selection == 1:
                    break

            except:
                print("An invalid column input was detected, please try again.")
                continue

            else:
                break

    else:
        columns = list(data.columns.values)

        # Check if columns are valid for PCA
        try:
            invalid_selection = 0
            # Test open every column and convert to number
            for i in columns:
                test_column = i
                for j in data[i]:
                    float(j)
        except ValueError:
            print(test_column + ' is invalid for PCA.')
            invalid_selection = 1

        if invalid_selection == 1:
            print("Due to invalid columns for PCA, please change your column selection type.")
            print()
            new_selection = column_selection_type(int(1))
            print("New Selection")
            column_name_list = column_list(data, new_selection)

    # Return column_name list to original function
    return column_name_list


def column_selection_type(start_index: int):
    # Ask whether to use all columns, exclude certain columns, or select certain columns
    selection_type = ["Enter 0 to use all columns in dataset.",
                      "Enter 1 to use all columns excluding selected columns.",
                      "Enter 2 to select columns for PCA."]

    while True:
        try:
            for index, i in enumerate(selection_type):
                if start_index <= index:
                    print(i)
            index_selection = int(input("Enter Selection: "))
            selection_type[index_selection]
            if index_selection < start_index:
                int("Error")
        except (ValueError, IndexError):
            print("Input must be integer between " + str(start_index) + " and " + str(len(selection_type) - 1))
            continue
        else:
            break
    return index_selection


def open_unknown_csv(file_in, delimination):
    encode_index = 0
    encoders = ['utf_8', 'latin1', 'utf_16',
                'ascii', 'big5', 'big5hkscs', 'cp037', 'cp424',
                'cp437', 'cp500', 'cp720', 'cp737', 'cp775',
                'cp850', 'cp852', 'cp855', 'cp856', 'cp857',
                'cp858', 'cp860', 'cp861', 'cp862', 'cp863',
                'cp864', 'cp865', 'cp866', 'cp869', 'cp874',
                'cp875', 'cp932', 'cp949', 'cp950', 'cp1006',
                'cp1026', 'cp1140', 'cp1250', 'cp1251', 'cp1252',
                'cp1253', 'cp1254', 'cp1255', 'cp1256', 'cp1257',
                'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr',
                'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp',
                'iso2022_jp_1', 'iso2022_jp_2', 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                'iso2022_kr', 'latin_1', 'iso8859_2', 'iso8859_3', 'iso8859_4',
                'iso8859_5', 'iso8859_6', 'iso8859_7', 'iso8859_8', 'iso8859_9',
                'iso8859_10', 'iso8859_11', 'iso8859_13', 'iso8859_14', 'iso8859_15',
                'iso8859_16', 'johab', 'koi8_r', 'koi8_u', 'mac_cyrillic',
                'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 'mac_turkish',
                'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 'utf_32',
                'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le',
                'utf_7', 'utf_8', 'utf_8_sig']

    data = open_file(file_in, encoders[encode_index], delimination)
    while data is str:
        if encode_index < len(encoders) - 1:
            encode_index = encode_index + 1
            data = open_file(file_in, encoders[encode_index], delimination)
        else:
            print("Can't find appropriate encoder")
            exit()

    return data

def open_file(file_in, encoder, delimination):
    try:
        data = pd.read_csv(file_in, low_memory=False, encoding=encoder, delimiter=delimination)
        print("Opened file using encoder: " + encoder)

    except UnicodeDecodeError:
        print("Encoder Error for: " + encoder)
        return "Encode Error"
    return data








if __name__ == '__main__':
    main()