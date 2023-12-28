import gradio as gr
import requests

# Securely input your actual OpenAI API key
openai_api_key = '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'

def process_audio_and_query(audio_file_path, topics):
    if audio_file_path is not None:
        try:
            # Read and transcribe audio
            with open(audio_file_path, 'rb') as audio_file:
                files = {"file": audio_file}
                # Transcribe audio using Whisper API
                response = requests.post(
                    url="https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {openai_api_key}"},
                    files=files,
                    data={"model": "whisper-1"}
                )

            if response and response.status_code == 200:
                transcription = response.json().get('text', '')
                print("Transcription:", transcription)  # Debug print

                # Check if the transcription contains any of the topics
                is_dirty = any(topic.lower() in transcription.lower() for topic in topics.split(','))

                # Prepare prompt for GPT-4
                messages = [{"role": "system", "content": f"Analyze the following text for mentions of these topics: {topics}"},
                            {"role": "user", "content": transcription}]
                
                # Send messages to GPT-4 chat completion
                gpt_response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {openai_api_key}"},
                    json={
                        "model": "gpt-4-1106-preview",  # Use "gpt-4-vision-preview" if you want the model with vision capabilities
                        "messages": messages
                    }
                )

                gpt_text = ""
                if gpt_response.status_code == 200:
                    gpt_text = gpt_response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
                    print("GPT-4 Response:", gpt_text)  # Debug print
                else:
                    print("Error with GPT-4 API:", gpt_response.status_code)  # Error handling for GPT-4 response
                    gpt_text = f"Error: {gpt_response.status_code}"
                
                analysis_result = "Dirty" if is_dirty else "Clean"
                return transcription, analysis_result, gpt_text
            else:
                print("Error with Whisper API:", response.status_code)  # Error handling for Whisper API
                return "", "Error in Whisper API", ""
        except Exception as e:
            print("An error occurred:", str(e))  # General error handling
            return "", f"An error occurred: {str(e)}", ""
    else:
        return "", "No audio file provided", ""

# Setting up the Gradio Interface
iface = gr.Interface(
    fn=process_audio_and_query,
    inputs=[
        gr.Audio(label="Upload Audio File", type="filepath"),
        gr.Textbox(label="Topics to Look For")
    ],
    outputs=[
        gr.Textbox(label="Transcription", placeholder="Transcription will appear here..."),
        gr.Label(label="Analysis Result"),
        gr.Textbox(label="GPT-4 Response", placeholder="GPT-4 Response will appear here...")
    ]
)

iface.launch()
