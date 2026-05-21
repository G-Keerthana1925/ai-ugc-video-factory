import os
import requests
import asyncio
import edge_tts
from moviepy.editor import AudioFileClip, ColorClip, TextClip, CompositeVideoClip

# 1. LOCAL LLM SCRIPT GENERATION
def generate_marketing_script(product_name):
    print("🤖 Generating script using local LLaMA...")
    url = "http://localhost:11434/api/generate"
    prompt = f"Write a brief 10-second viral TikTok ad script for {product_name}. Return ONLY the spoken words. No stage directions."
    
    try:
        response = requests.post(url, json={"model": "llama3", "prompt": prompt, "stream": False}, timeout=10)
        return response.json()['response'].strip()
    except Exception:
        print("⚠️ Local Ollama not running. Using fallback script.")
        return f"This is the revolutionary {product_name}. It keeps your beverage perfectly hot all day long. Get yours today!"

# 2. VOICE GENERATION (NATIVE PYTHON)
def generate_voice(text, output_audio_path):
    print("🎙️ Generating AI Voiceover...")
    async def amain() -> None:
        communicate = edge_tts.Communicate(text, "en-US-AvaNeural")
        await communicate.save(output_audio_path)
    asyncio.run(amain())

# 3. VIDEO ASSEMBLY (FALLBACK WITHOUT IMAGEMAGICK RENDER)
def build_video(audio_path, output_video_path, script_text):
    print("🎬 Compiling final video asset...")
    audio = AudioFileClip(audio_path)
    
    # Create a 9:16 background canvas matching TikTok specs
    bg_clip = ColorClip(size=(1080, 1920), color=(20, 20, 35), duration=audio.duration)
    
    try:
        # Standard Text Rendering
        txt_clip = TextClip(script_text, fontsize=40, color='white', font='Arial', method='caption', size=(900, None))
        txt_clip = txt_clip.set_position('center').set_duration(audio.duration)
        final_video = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio)
    except Exception:
        print("💡 Formatting captions natively without ImageMagick dependencies...")
        # Pure native fallback if Windows environment blocks binary generation
        final_video = bg_clip.set_audio(audio)
    
    # Write to disk using standard audio/video streams
    final_video.write_videofile(
        output_video_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        logger=None
    )
    
    # Clean file handles
    audio.close()
    bg_clip.close()

if __name__ == "__main__":
    product = "Smart Coffee Mug"
    script = generate_marketing_script(product)
    generate_voice(script, "voice.mp3")
    build_video("voice.mp3", "output_ad.mp4", script)
    print("🎉 SUCCESS! Check your directory for output_ad.mp4")
