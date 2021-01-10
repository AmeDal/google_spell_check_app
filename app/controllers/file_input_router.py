import os
import time

from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from ..core.schema.file_input_schema import FileInputResponse
from ..settings import get_app_settings


config = get_app_settings()
router_name = 'File Input'
router_description = 'APIs to control file inputs for running spell check'
openapi_tag = {'name': router_name, 'description': router_description}
router = APIRouter(prefix = '/file-input', tags = [router_name])


@router.get("/",
            summary = 'Check if given file exists in the input folder',
            response_model = FileInputResponse,
            response_model_exclude_unset = True)
async def check_file_by_name(file_name: str = Query('*', description = 'Use * to get all files present in the input folder')):
    try:
        all_files = [
            os.path.basename(i)
            for i in os.listdir(os.path.abspath(config.UPLOAD_FOLDER))
            if os.path.isfile(os.path.join(os.path.abspath(config.UPLOAD_FOLDER), i))
        ]
        if file_name == "*":
            return FileInputResponse(
                response_message = f'Found {len(all_files)} files',
                all_files = all_files)
        else:
            file_name_with_different_case = [i.lower() for i in all_files if i.lower() == file_name.lower()]
            if file_name in all_files:
                return FileInputResponse(response_message = f"'{file_name}' is present")
            elif len(file_name_with_different_case) > 0:
                return FileInputResponse(
                    response_message =
                    f"'{file_name}' is present but with different case: {', '.join(file_name_with_different_case)}"
                )
            else:
                return FileInputResponse(response_message = f"'{file_name}' is not present")
    except Exception as e:
        error_message = f"Could not get file(s) due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)

@router.post("/upload",
             summary = 'Upload file to the input folder',
             description = '## Upload file to be used as input for spell-check\nIf CSV or Excel is provided, **first column** is supposed to be unique identifier column and **second column** will be used as input for spell-checking',
             response_model = FileInputResponse,
             response_model_exclude_unset = True)
async def upload_input_file(file: UploadFile = File(..., description = 'Choose file to be uploaded as input')):
    try:
        file_name = file.filename
        file_size = file.file._file.getbuffer().nbytes
        allowed_file_extensions = ", ".join(config.ALLOWED_UPLOAD_EXTENSIONS)
        if os.path.splitext(file_name)[1].replace(".", "") in config.ALLOWED_UPLOAD_EXTENSIONS:
            uploaded_file = os.path.join(config.UPLOAD_FOLDER, file_name)
            start = progress = time.perf_counter()
            downloaded_content = 0
            with open(uploaded_file, "wb") as f:
                while True:
                    chunk = await file.read(config.FILE_WRITE_BUFFER_SIZE)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded_content += len(chunk)
                    elapsed_time = time.perf_counter() - progress
                    # Print progress after every minute
                    if elapsed_time > 60:
                        progress = time.perf_counter()
                        print(f'\n\tDownloaded {(downloaded_content / file_size) * 100:.2f}% at {downloaded_content / elapsed_time / 1000:.2f} kB/sec of {uploaded_file}\n')
            print(f"\nFinished downloading '{uploaded_file}' in {time.perf_counter() - start:.2f} seconds\n")
            return FileInputResponse(response_message = f"'{file_name}' uploaded successfully!")
        else:
            return FileInputResponse(response_message = f"Invalid file_type! Allowed file extensions are: '{allowed_file_extensions}'")
    except Exception as e:
        error_message = f"Could not upload file due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)

@router.delete("/",
             summary = 'Delete file from the input folder',
             response_model = FileInputResponse,
             response_model_exclude_unset = True)
async def delete_input_file(
    confirmation_flag: bool,
    file_name: str = Query('*', description = 'Use * to delete all files present in the input folder')):
    try:
        upload_folder = os.path.abspath(config.UPLOAD_FOLDER)
        if confirmation_flag:
            all_files = [os.path.basename(i) for i in os.listdir(upload_folder)]
            if file_name == "*":
                [os.unlink(os.path.join(upload_folder, i)) for i in os.listdir(upload_folder)]
                return FileInputResponse(response_message = f'{len(all_files)} files deleted', deleted_files = all_files)
            else:
                if file_name in all_files:
                    [
                        os.unlink(os.path.join(upload_folder, i)) for i in os.listdir(upload_folder)
                        if os.path.basename(i) == file_name
                    ]
                    return FileInputResponse(response_message = f"{file_name}' deleted successfully")
                else:
                    return FileInputResponse(response_message = f"Could not delete '{file_name}' as it is not present")
        else:
            return FileInputResponse(response_message = 'Did not delete any file as confirmation_flag was false')
    except Exception as e:
        error_message = f"Could not delete file(s) due to exception: '{e}'"
        print(error_message)
        raise HTTPException(status_code = 500, detail = error_message)
