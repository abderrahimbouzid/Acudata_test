import google.generativeai as genai

genai.configure(api_key="AIzaSyCRORooRAFbOMh4xZkoPRht3CEWlH2Q3NE")

print("Available models for generateContent:\n")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  {m.name}")
