from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
from functions import download_mp3, delete_path, upload_file
import uuid

app = FastAPI()

class VoiceGenerationRequest(BaseModel):
    music_url: str
    music_title: str
    voice_directory: str
    p_value: int
    ir_value: int

@app.post("/generate-voice")
async def generate_voice(request: VoiceGenerationRequest):
    try:
        # Path to your virtual environment
        venv_path = '/home/kamila/RVCmodel/AICoverGen/.venv'

        # Construct the command to activate virtual environment and run Python script
        activation_script = os.path.join(venv_path, 'bin', 'activate')
        python_interpreter = os.path.join(venv_path, 'bin', 'python3.9')
        python_script_path = '/home/kamila/RVCmodel/AICoverGen/src/main.py'

        # Download the file from the URL
        music_path = f"/home/kamila/RVCmodel/AICoverGenAPI/downloads/{request.music_title}.mp3"
        download_mp3(request.music_url, music_path)

        # Construct the command to execute the Python script
        command = f". {activation_script} && {python_interpreter} {python_script_path} -i '{music_path}' -dir {request.voice_directory} -p {request.p_value} -ir {request.ir_value}"

        # Execute the command
        process = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if the command was successful
        if process.returncode != 0:
            print(process.stderr.decode())
            raise HTTPException(status_code=500, detail=f"Failed to execute script: {process.stderr.decode()}")
        
        # Get the customed path from the output
        output_lines = process.stdout.split('\n')
        customed_path = output_lines[-2][23:]
        dirForDelete = output_lines[-2][23:79]

        # Delete the downloaded file
        delete_path(music_path)

        print(dirForDelete)

        # Upload the file to S3
        key = f"{uuid.uuid4()}tkm{request.music_title}"
        fileLocation = upload_file(customed_path, key)

        # Delete the customed file
        delete_path(dirForDelete)

        return {"key": key, "location": fileLocation}
    except subprocess.CalledProcessError as e:
        # If subprocess.run() throws an error, raise HTTPException with error details
        raise HTTPException(status_code=500, detail=f"Failed to execute script: {e.stderr.decode()}")

