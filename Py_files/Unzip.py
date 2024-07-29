
#%%
import zipfile
import os
os.chdir("D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\Csv_Files\\Ameriflux_dT_insitu\\")
file_list=os.listdir()
def unzip_selected_file(zip_file_path, unique_string, output_dir):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if unique_string in file_name:
                zip_ref.extract(file_name, output_dir)
                print(f"Extracted {file_name} to {output_dir}")
                return file_name
    print(f"No file found with unique string '{unique_string}' in {zip_file_path}")
    return None
def process_zip_files(zip_files, unique_string, output_dir):
    extracted_files = []
    for zip_file in zip_files:
        extracted_file = unzip_selected_file(zip_file, unique_string, output_dir)
        if extracted_file:
            extracted_files.append(extracted_file)
    return extracted_files
# zip_files = ['path/to/zip1.zip', 'path/to/zip2.zip', 'path/to/zip3.zip']
unique_string = 'BIF'
output_dir = 'D:\\Backup\\Rouhin_Lenovo\\US_project\\GEE_SEBAL_Project\\Csv_Files\\AF_dT_unzip_BIF\\'

extracted_files = process_zip_files(file_list, unique_string, output_dir)
print(f"Extracted files: {extracted_files}")
